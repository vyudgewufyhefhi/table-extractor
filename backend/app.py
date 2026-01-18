from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from models import db, User, FileRecord, TextRecord
from auth import register_user, authenticate_user
from excel_utils import create_excel_from_table
from datetime import datetime, timedelta, timedelta
import os
from dotenv import load_dotenv
import uuid
import json

# ===== 统一路径配置 =====
# 获取项目根目录（backend 的父目录）
_backend_dir = os.path.dirname(os.path.abspath(__file__))
_backend_dir_name = os.path.basename(_backend_dir)

# 判断是否在 Docker 容器中（工作目录通常是 /app）
IS_DOCKER = os.path.exists('/app') and os.getcwd() == '/app'

if IS_DOCKER:
    # Docker 环境：工作目录是 /app，代码从 backend/ 复制到 /app/
    # 数据库目录：/app/instance（根目录，通过挂载）
    # 上传文件目录：/app/uploads（根目录，通过挂载）
    PROJECT_ROOT = '/app'
    INSTANCE_DIR = '/app/instance'  # Docker 挂载路径（根目录的 instance）
    UPLOADS_DIR = '/app/uploads'  # Docker 挂载路径
else:
    # 本地开发：backend 的父目录是项目根目录
    # 数据库目录：根目录的 instance（统一位置）
    # 上传文件目录：根目录的 uploads
    PROJECT_ROOT = os.path.dirname(_backend_dir)
    INSTANCE_DIR = os.path.join(PROJECT_ROOT, 'instance')  # 根目录的 instance
    UPLOADS_DIR = os.path.join(PROJECT_ROOT, 'uploads')

# 加载环境变量（优先从根目录加载）
root_env_path = os.path.join(PROJECT_ROOT, '.env')
backend_env_path = os.path.join(os.path.dirname(__file__), '.env')

# 先加载根目录的.env，再加载backend目录的.env（如果存在）
if os.path.exists(root_env_path):
    load_dotenv(root_env_path)
if os.path.exists(backend_env_path):
    load_dotenv(backend_env_path, override=False)  # 不覆盖根目录的配置

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

# 统一数据库路径：使用根目录的 instance/table_extractor.db
# 确保 instance 目录存在
os.makedirs(INSTANCE_DIR, exist_ok=True)
# 数据库文件路径（绝对路径）
default_db_path = os.path.join(INSTANCE_DIR, 'table_extractor.db')
# 将绝对路径转换为 SQLite URI 格式（使用 3 个斜杠表示绝对路径）
# 注意：SQLite URI 使用 / 作为路径分隔符，需要转换 Windows 路径
if os.name == 'nt':  # Windows
    db_uri = 'sqlite:///' + default_db_path.replace('\\', '/')
else:  # Unix/Linux
    db_uri = 'sqlite:///' + default_db_path
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', db_uri)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 统一 uploads 路径：使用根目录的 uploads
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
# 确保 uploads 目录在项目根目录
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(os.path.join(UPLOADS_DIR, 'excel'), exist_ok=True)
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_FILE_SIZE', 10485760))  # 10MB

# 初始化扩展
db.init_app(app)

# 自动生成CORS配置
def get_cors_origins():
    """根据部署模式自动生成CORS允许的源"""
    deploy_mode = os.getenv('DEPLOY_MODE', 'local').lower()
    cors_origins_env = os.getenv('CORS_ORIGINS', '').strip()
    
    # 如果手动指定了CORS_ORIGINS，优先使用
    if cors_origins_env:
        return [origin.strip() for origin in cors_origins_env.split(',') if origin.strip()]
    
    # 根据部署模式自动生成
    if deploy_mode == 'cloud':
        public_domain = os.getenv('PUBLIC_DOMAIN', '').strip()
        public_ip = os.getenv('PUBLIC_IP', '').strip()
        frontend_port = os.getenv('VITE_PORT', '5173')
        
        origins = []
        if public_domain:
            # 使用域名
            origins.append(f'http://{public_domain}')
            origins.append(f'https://{public_domain}')
        elif public_ip:
            # 使用公网IP
            origins.append(f'http://{public_ip}:{frontend_port}')
            origins.append(f'http://{public_ip}:3000')
        
        if origins:
            return origins
    
    # 默认本地开发配置
    return ['http://localhost:5173', 'http://localhost:3000']

allowed_origins = get_cors_origins()
CORS(app, supports_credentials=True, origins=allowed_origins)

# 确保上传目录存在（已在上面初始化，这里不需要重复创建）


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({'status': 'ok', 'message': '服务运行正常'}), 200


def parse_plain_text_table(raw_text: str):
    """
    将用户粘贴的纯文本解析为表格结构。
    约定：
    - 按换行分割为多行
    - 每行按空白字符分割为多个单元格
    - 第一行为表头，后续为数据行
    """
    import re

    if not raw_text or not raw_text.strip():
        raise ValueError("文本内容为空")

    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    if not lines:
        raise ValueError("文本中没有有效内容")

    # 解析每一行，使用任意数量的空白字符分隔
    rows = [re.split(r"\s+", line) for line in lines]

    if len(rows) < 2:
        # 只有一行时，也允许作为数据行，但表头仍为第一行
        headers = rows[0]
        data_rows = rows[1:]
    else:
        headers = rows[0]
        data_rows = rows[1:]

    # 统一列数：取最大列数，补空字符串
    max_cols = max(len(r) for r in [headers] + data_rows)
    headers = headers + [""] * (max_cols - len(headers))
    normalized_rows = []
    for r in data_rows:
        r = r + [""] * (max_cols - len(r))
        normalized_rows.append(r)

    return {
        "headers": headers,
        "rows": normalized_rows,
    }


def cleanup_orphaned_excel_files_for_user(user_id=None, exclude_path=None):
    """
    自动清理孤立的Excel文件（不在数据库中的文件）
    
    Args:
        user_id: 如果指定，只清理该用户的临时文件（通过文件创建时间推断）
        exclude_path: 排除的文件路径（通常是当前正在使用的文件）
    
    Returns:
        删除的文件数量
    """
    try:
        # 获取所有数据库中的Excel文件路径
        all_records = TextRecord.query.all()
        db_excel_files = set()
        
        for record in all_records:
            if record.excel_path:
                excel_path = record.excel_path
                if not os.path.isabs(excel_path):
                    excel_path = os.path.abspath(os.path.join(
                        PROJECT_ROOT, 
                        excel_path
                    ))
                db_excel_files.add(excel_path)
                db_excel_files.add(os.path.basename(excel_path))
        
        # 扫描 uploads/excel 目录（基于项目根目录）
        excel_dir = os.path.join(PROJECT_ROOT, app.config['UPLOAD_FOLDER'], 'excel')
        
        if not os.path.exists(excel_dir):
            return 0
        
        deleted_count = 0
        now = datetime.now()
        # 清理超过1小时的未保存文件
        max_age = timedelta(hours=1)
        
        # 遍历目录中的所有文件
        for filename in os.listdir(excel_dir):
            if not filename.endswith('.xlsx'):
                continue
            
            file_path = os.path.join(excel_dir, filename)
            file_path_abs = os.path.abspath(file_path)
            
            # 排除当前正在使用的文件
            if exclude_path and (file_path_abs == exclude_path or os.path.basename(exclude_path) == filename):
                continue
            
            # 检查文件是否在数据库中
            is_in_db = False
            for record in all_records:
                if record.excel_path:
                    record_path = record.excel_path
                    if not os.path.isabs(record_path):
                        record_path = os.path.abspath(os.path.join(
                            PROJECT_ROOT, 
                            record_path
                        ))
                    if record_path == file_path_abs or os.path.basename(record_path) == filename:
                        is_in_db = True
                        break
            
            # 如果不在数据库中，检查文件创建时间
            if not is_in_db:
                try:
                    # 获取文件修改时间（作为创建时间的近似值）
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path_abs))
                    file_age = now - file_mtime
                    
                    # 如果文件超过1小时，或者用户指定了user_id且文件是最近生成的（可能是该用户的临时文件）
                    if file_age > max_age:
                        # 超过1小时，直接删除
                        os.remove(file_path_abs)
                        deleted_count += 1
                    elif user_id is not None:
                        # 如果指定了user_id，且文件是最近生成的（可能是该用户的临时文件），也删除
                        # 这里假设最近5分钟内生成的文件可能是该用户的临时文件
                        if file_age < timedelta(minutes=5):
                            os.remove(file_path_abs)
                            deleted_count += 1
                except Exception as e:
                    # 删除失败不影响主流程
                    pass
        
        return deleted_count
    except Exception as e:
        # 清理失败不影响主流程
        print(f"清理孤立文件时出错: {str(e)}")
        return 0


@app.route('/api/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    user, error = register_user(username, password)
    if error:
        return jsonify({'success': False, 'error': error}), 400
    
    return jsonify({
        'success': True,
        'user': user.to_dict(),
        'message': '注册成功'
    }), 201


@app.route('/api/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json() or {}
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        # 调试日志（生产环境可移除）
        if not username:
            return jsonify({'success': False, 'error': '请输入用户名'}), 200
        if not password:
            return jsonify({'success': False, 'error': '请输入密码'}), 200
        
        user, error = authenticate_user(username, password)
        if error:
            # 登录失败不应该返回401，应该返回200但success=False
            # 401是用于已登录用户的token过期等情况
            return jsonify({'success': False, 'error': error}), 200
        
        return jsonify({
            'success': True,
            'user': user.to_dict(),
            'message': '登录成功'
        }), 200
    except Exception as e:
        # 捕获任何异常，避免500错误
        return jsonify({'success': False, 'error': f'登录失败: {str(e)}'}), 200


# ===== 手动文本模式接口（不调用大模型，也不上传文件） =====


@app.route('/api/manual/parse', methods=['POST'])
def manual_parse():
    """
    接收用户粘贴的纯文本，解析为表格并生成 Excel，同时写入历史记录。
    请求体示例：
    {
        "user_id": 1,
        "raw_text": "……",
        "title": "可选，自定义标题"
    }
    """
    data = request.get_json() or {}
    user_id = data.get('user_id')
    raw_text = data.get('raw_text', '')
    custom_title = data.get('title')

    if not user_id:
        return jsonify({'success': False, 'error': '需要用户ID'}), 400

    if not raw_text or not raw_text.strip():
        return jsonify({'success': False, 'error': '文本内容不能为空'}), 400

    try:
        # 确认用户存在
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'error': '用户不存在'}), 404

        # 生成标题：2026年01月16日13:45:30（时分秒用冒号）
        # 先检查同一秒是否已有生成记录，防止频繁生成（在生成Excel之前检查）
        now = datetime.now()
        title_format = now.strftime("%Y年%m月%d日%H:%M:%S")
        
        if custom_title and str(custom_title).strip():
            title = str(custom_title).strip()
        else:
            title = title_format
        
        # 检查同一秒是否已有生成记录（检查用户的最近一条记录）
        existing_record = TextRecord.query.filter_by(user_id=user_id).order_by(
            TextRecord.created_at.desc()
        ).first()
        
        if existing_record:
            # 检查是否是同一秒
            existing_time = existing_record.created_at
            # 比较到秒级别
            if (existing_time.year == now.year and 
                existing_time.month == now.month and 
                existing_time.day == now.day and
                existing_time.hour == now.hour and
                existing_time.minute == now.minute and
                existing_time.second == now.second):
                return jsonify({
                    'success': False,
                    'error': '生成表格过于频繁，请稍后再试！'
                }), 400

        # 解析文本为表格
        table_data = parse_plain_text_table(raw_text)

        # 在生成新Excel之前，自动清理该用户之前生成的未保存临时文件
        cleanup_orphaned_excel_files_for_user(user_id=user_id)
        
        # 生成 Excel
        excel_filename = f"{uuid.uuid4().hex}.xlsx"
        # 确保路径是绝对路径，基于项目根目录
        excel_dir = os.path.join(PROJECT_ROOT, app.config['UPLOAD_FOLDER'], 'excel')
        os.makedirs(excel_dir, exist_ok=True)
        excel_path = os.path.join(excel_dir, excel_filename)
        # 转换为绝对路径
        excel_path_abs = os.path.abspath(excel_path)
        create_excel_from_table(table_data, excel_path_abs)

        # 不自动保存到历史记录，只返回Excel信息
        # 用户需要点击"存入历史记录"按钮才会保存

        return jsonify({
            'success': True,
            'data': {
                'title': title,
                'excel_path': excel_path_abs,
                'excel_filename': excel_filename,
                'table_data': table_data,
                'raw_text': raw_text
            },
            'message': '解析并生成Excel成功'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'解析失败: {str(e)}'}), 500


@app.route('/api/users/<int:user_id>/manual-records', methods=['GET'])
def get_manual_records(user_id):
    """获取用户的手动文本历史记录"""
    records = TextRecord.query.filter_by(user_id=user_id).order_by(
        TextRecord.created_at.desc()
    ).all()
    return jsonify({
        'success': True,
        'records': [r.to_dict() for r in records],
    }), 200


@app.route('/api/manual/save', methods=['POST'])
def save_to_history():
    """
    将生成的Excel数据保存到历史记录
    请求体：
    {
        "user_id": 1,
        "title": "2026年01月16日14_00_22",
        "raw_text": "...",
        "table_data": {...},
        "excel_path": "..."
    }
    """
    data = request.get_json() or {}
    user_id = data.get('user_id')
    title = data.get('title')
    raw_text = data.get('raw_text', '')
    table_data = data.get('table_data', {})
    excel_path = data.get('excel_path')

    if not user_id:
        return jsonify({'success': False, 'error': '需要用户ID'}), 400
    if not title:
        return jsonify({'success': False, 'error': '需要标题'}), 400
    if not excel_path:
        return jsonify({'success': False, 'error': '需要Excel文件路径'}), 400

    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'error': '用户不存在'}), 404

        # 在保存到历史记录之前，自动清理该用户之前生成的未保存临时文件（排除当前要保存的文件）
        cleanup_orphaned_excel_files_for_user(user_id=user_id, exclude_path=excel_path)
        
        # 保存到历史记录
        record = TextRecord(
            user_id=user_id,
            title=title,
            raw_text=raw_text,
            table_json=json.dumps(table_data, ensure_ascii=False),
            excel_path=excel_path,
        )
        db.session.add(record)
        db.session.commit()

        return jsonify({
            'success': True,
            'record': record.to_dict(),
            'message': '已保存到历史记录'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'保存失败: {str(e)}'}), 500


@app.route('/api/manual/<int:record_id>', methods=['DELETE'])
def delete_record(record_id):
    """删除单条历史记录"""
    try:
        record = TextRecord.query.get_or_404(record_id)
        
        # 删除Excel文件（如果存在）
        if record.excel_path and os.path.exists(record.excel_path):
            try:
                os.remove(record.excel_path)
            except Exception as e:
                print(f"删除Excel文件失败: {str(e)}")
        
        db.session.delete(record)
        db.session.commit()
        
        return jsonify({'success': True, 'message': '删除成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'删除失败: {str(e)}'}), 500


@app.route('/api/manual/batch-delete', methods=['POST'])
def batch_delete_records():
    """批量删除历史记录
    请求体：
    {
        "record_ids": [1, 2, 3]
    }
    """
    try:
        data = request.get_json() or {}
        record_ids = data.get('record_ids', [])
        
        if not record_ids or not isinstance(record_ids, list):
            return jsonify({'success': False, 'error': '需要提供记录ID列表'}), 400
        
        records = TextRecord.query.filter(TextRecord.id.in_(record_ids)).all()
        
        # 删除Excel文件
        for record in records:
            if record.excel_path and os.path.exists(record.excel_path):
                try:
                    os.remove(record.excel_path)
                except Exception as e:
                    print(f"删除Excel文件失败: {str(e)}")
        
        # 批量删除记录
        for record in records:
            db.session.delete(record)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'成功删除{len(records)}条记录'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'批量删除失败: {str(e)}'}), 500


@app.route('/api/manual/download-temp', methods=['GET'])
def download_temp_excel():
    """下载临时生成的Excel文件（未保存到历史记录）"""
    excel_path = request.args.get('path')
    filename = request.args.get('filename', 'excel.xlsx')
    
    if not excel_path:
        return jsonify({'success': False, 'error': '需要文件路径'}), 400
    
    # 处理路径（基于项目根目录）
    if not os.path.isabs(excel_path):
        excel_path = os.path.join(PROJECT_ROOT, excel_path)
    
    if not os.path.exists(excel_path):
        return jsonify({'success': False, 'error': 'Excel文件不存在'}), 404
    
    return send_file(
        excel_path,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


@app.route('/api/manual/<int:record_id>/download-excel', methods=['GET'])
def download_manual_excel(record_id):
    """下载手动文本生成的Excel"""
    record = TextRecord.query.get_or_404(record_id)
    
    if not record.excel_path:
        return jsonify({'success': False, 'error': 'Excel文件路径不存在'}), 404
    
    # 处理路径：如果是相对路径，转换为绝对路径（基于项目根目录）
    excel_path = record.excel_path
    if not os.path.isabs(excel_path):
        # 相对路径，需要基于项目根目录
        excel_path = os.path.join(PROJECT_ROOT, excel_path)
    
    # 如果还是找不到，尝试基于UPLOAD_FOLDER的绝对路径
    if not os.path.exists(excel_path):
        excel_path = os.path.join(PROJECT_ROOT, app.config['UPLOAD_FOLDER'], 'excel', os.path.basename(record.excel_path))
    
    if not os.path.exists(excel_path):
        return jsonify({'success': False, 'error': f'Excel文件不存在: {excel_path}'}), 404

    filename = f"{record.title}.xlsx"
    # 替换标题中的非法文件名字符
    for ch in [' ', ':', '/', '\\', '*', '?', '"', '<', '>', '|']:
        filename = filename.replace(ch, '_')

    return send_file(
        excel_path,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


@app.route('/api/users/<int:user_id>/files', methods=['GET'])
def get_user_files(user_id):
    """
    兼容旧接口：目前不再使用文件上传和AI识别，这里返回空列表，
    以免前端旧代码报错。
    """
    return jsonify({
        'success': True,
        'files': []
    }), 200


@app.route('/api/files/<int:file_id>', methods=['GET'])
def get_file(file_id):
    """兼容旧接口，返回404"""
    return jsonify({'success': False, 'error': '文件功能已停用'}), 404


@app.route('/api/manual/cleanup-orphaned-files', methods=['POST'])
def cleanup_orphaned_excel_files():
    """清理孤立的Excel文件（不在数据库中的文件）"""
    try:
        # 获取所有数据库中的Excel文件路径
        all_records = TextRecord.query.all()
        db_excel_files = set()
        
        for record in all_records:
            if record.excel_path:
                # 标准化路径（转换为绝对路径）
                excel_path = record.excel_path
                if not os.path.isabs(excel_path):
                    excel_path = os.path.abspath(os.path.join(
                        PROJECT_ROOT, 
                        excel_path
                    ))
                db_excel_files.add(excel_path)
                # 也添加文件名（用于匹配）
                db_excel_files.add(os.path.basename(excel_path))
        
        # 扫描 uploads/excel 目录（基于项目根目录）
        excel_dir = os.path.join(PROJECT_ROOT, app.config['UPLOAD_FOLDER'], 'excel')
        
        if not os.path.exists(excel_dir):
            return jsonify({
                'success': True,
                'message': 'Excel目录不存在，无需清理',
                'deleted_count': 0
            }), 200
        
        deleted_count = 0
        deleted_files = []
        
        # 遍历目录中的所有文件
        for filename in os.listdir(excel_dir):
            if not filename.endswith('.xlsx'):
                continue
            
            file_path = os.path.join(excel_dir, filename)
            file_path_abs = os.path.abspath(file_path)
            
            # 检查文件是否在数据库中
            is_in_db = False
            for record in all_records:
                if record.excel_path:
                    record_path = record.excel_path
                    if not os.path.isabs(record_path):
                        record_path = os.path.abspath(os.path.join(
                            PROJECT_ROOT, 
                            record_path
                        ))
                    # 比较绝对路径或文件名
                    if record_path == file_path_abs or os.path.basename(record_path) == filename:
                        is_in_db = True
                        break
            
            # 如果不在数据库中，删除文件
            if not is_in_db:
                try:
                    os.remove(file_path_abs)
                    deleted_count += 1
                    deleted_files.append(filename)
                except Exception as e:
                    print(f"删除孤立文件失败 {filename}: {str(e)}")
        
        return jsonify({
            'success': True,
            'message': f'清理完成，删除了 {deleted_count} 个孤立文件',
            'deleted_count': deleted_count,
            'deleted_files': deleted_files
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'清理失败: {str(e)}'}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # 启动时自动清理所有超过1小时的孤立文件
        deleted = cleanup_orphaned_excel_files_for_user()
        if deleted > 0:
            print(f"启动时清理了 {deleted} 个孤立文件")
    
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    app.run(host=host, port=port, debug=True)


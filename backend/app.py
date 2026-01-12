from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from models import db, User, FileRecord
from auth import register_user, authenticate_user
from file_utils import allowed_file, get_file_type, save_uploaded_file, pdf_to_base64_preview, image_to_base64
from ai_service import extract_table_from_image, extract_table_from_pdf
from excel_utils import create_excel_from_table, create_excel_from_multi_page
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from dotenv import load_dotenv
import uuid

# 加载环境变量
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///table_extractor.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_FILE_SIZE', 10485760))  # 10MB

# 初始化扩展
db.init_app(app)
CORS(app, supports_credentials=True, origins=["http://localhost:5173", "http://localhost:3000"])

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'excel'), exist_ok=True)


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
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    user, error = authenticate_user(username, password)
    if error:
        return jsonify({'success': False, 'error': error}), 401
    
    return jsonify({
        'success': True,
        'user': user.to_dict(),
        'message': '登录成功'
    }), 200


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """上传文件"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': '没有文件'}), 400
    
    file = request.files['file']
    user_id = request.form.get('user_id', type=int)
    
    if not user_id:
        return jsonify({'success': False, 'error': '需要用户ID'}), 400
    
    if file.filename == '':
        return jsonify({'success': False, 'error': '文件名为空'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'error': '不支持的文件类型'}), 400
    
    try:
        # 保存文件
        file_path, unique_filename, file_ext = save_uploaded_file(file, app.config['UPLOAD_FOLDER'])
        file_size = os.path.getsize(file_path)
        file_type = get_file_type(file.filename)
        
        # 创建文件记录
        file_record = FileRecord(
            user_id=user_id,
            filename=file.filename,
            file_type=file_type,
            file_path=file_path,
            file_size=file_size,
            status='uploaded'
        )
        db.session.add(file_record)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'file': file_record.to_dict(),
            'message': '上传成功'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/files/<int:file_id>/preview', methods=['GET'])
def preview_file(file_id):
    """预览文件"""
    file_record = FileRecord.query.get_or_404(file_id)
    
    try:
        if file_record.file_type == 'pdf':
            page = request.args.get('page', 0, type=int)
            base64_data = pdf_to_base64_preview(file_record.file_path, page)
        else:
            base64_data = image_to_base64(file_record.file_path)
        
        return jsonify({
            'success': True,
            'preview': base64_data,
            'file_type': file_record.file_type
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/files/<int:file_id>/recognize', methods=['POST'])
def recognize_file(file_id):
    """识别文件中的表格"""
    file_record = FileRecord.query.get_or_404(file_id)
    
    # 获取API配置
    api_key = os.getenv('QWEN_API_KEY')
    api_base = os.getenv('QWEN_API_BASE')
    model = os.getenv('QWEN_MODEL', 'qwen-vl-max')
    
    if not api_key:
        return jsonify({'success': False, 'error': 'API密钥未配置'}), 500
    
    try:
        file_record.status = 'processing'
        db.session.commit()
        
        # 根据文件类型调用不同的识别函数
        if file_record.file_type == 'pdf':
            table_data, error = extract_table_from_pdf(file_record.file_path, api_key, api_base, model)
        else:
            table_data, error = extract_table_from_image(file_record.file_path, api_key, api_base, model)
        
        if error:
            file_record.status = 'failed'
            db.session.commit()
            return jsonify({'success': False, 'error': error}), 500
        
        # 保存识别结果
        file_record.set_ai_result(table_data)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'file': file_record.to_dict(),
            'message': '识别成功'
        }), 200
        
    except Exception as e:
        file_record.status = 'failed'
        db.session.commit()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/files/<int:file_id>/correct', methods=['POST'])
def correct_file(file_id):
    """保存用户校正后的表格数据"""
    file_record = FileRecord.query.get_or_404(file_id)
    data = request.get_json()
    corrected_data = data.get('corrected_data')
    
    if not corrected_data:
        return jsonify({'success': False, 'error': '缺少校正数据'}), 400
    
    try:
        file_record.set_corrected_result(corrected_data)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'file': file_record.to_dict(),
            'message': '校正成功'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/files/<int:file_id>/generate-excel', methods=['POST'])
def generate_excel(file_id):
    """生成Excel文件"""
    file_record = FileRecord.query.get_or_404(file_id)
    
    # 获取校正后的数据，如果没有则使用AI识别结果
    if file_record.corrected_result:
        table_data = file_record.to_dict()['corrected_result']
    elif file_record.ai_result:
        table_data = file_record.to_dict()['ai_result']
    else:
        return jsonify({'success': False, 'error': '没有可用的表格数据'}), 400
    
    try:
        # 生成Excel文件
        excel_filename = f"{uuid.uuid4().hex}.xlsx"
        excel_path = os.path.join(app.config['UPLOAD_FOLDER'], 'excel', excel_filename)
        
        # 判断是否为多页表格
        if isinstance(table_data, dict) and table_data.get('multi_page'):
            create_excel_from_multi_page(table_data, excel_path)
        else:
            create_excel_from_table(table_data, excel_path)
        
        # 保存Excel路径
        file_record.set_excel_path(excel_path)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'file': file_record.to_dict(),
            'excel_url': f"/api/files/{file_id}/download-excel",
            'message': 'Excel生成成功'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/files/<int:file_id>/download-excel', methods=['GET'])
def download_excel(file_id):
    """下载Excel文件"""
    file_record = FileRecord.query.get_or_404(file_id)
    
    if not file_record.excel_path or not os.path.exists(file_record.excel_path):
        return jsonify({'success': False, 'error': 'Excel文件不存在'}), 404
    
    return send_file(
        file_record.excel_path,
        as_attachment=True,
        download_name=f"{file_record.filename.rsplit('.', 1)[0]}.xlsx",
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


@app.route('/api/users/<int:user_id>/files', methods=['GET'])
def get_user_files(user_id):
    """获取用户的所有文件记录"""
    files = FileRecord.query.filter_by(user_id=user_id).order_by(FileRecord.uploaded_at.desc()).all()
    return jsonify({
        'success': True,
        'files': [f.to_dict() for f in files]
    }), 200


@app.route('/api/files/<int:file_id>', methods=['GET'])
def get_file(file_id):
    """获取单个文件记录"""
    file_record = FileRecord.query.get_or_404(file_id)
    return jsonify({
        'success': True,
        'file': file_record.to_dict()
    }), 200


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    app.run(host=host, port=port, debug=True)


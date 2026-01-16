from flask import jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
import re


def validate_username(username):
    """验证用户名格式"""
    if not username or len(username.strip()) == 0:
        return False, "用户名不能为空"
    if len(username) < 3:
        return False, "用户名至少需要3个字符"
    if len(username) > 20:
        return False, "用户名不能超过20个字符"
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "用户名只能包含字母、数字和下划线"
    return True, None


def validate_password(password):
    """验证密码格式"""
    if not password:
        return False, "密码不能为空"
    if len(password) < 6:
        return False, "密码至少需要6个字符"
    if len(password) > 50:
        return False, "密码不能超过50个字符"
    return True, None


def register_user(username, password):
    """注册新用户"""
    # 验证用户名
    valid, error = validate_username(username)
    if not valid:
        return None, error
    
    # 验证密码
    valid, error = validate_password(password)
    if not valid:
        return None, error
    
    # 检查用户名是否已存在
    if User.query.filter_by(username=username).first():
        return None, "用户名已存在"
    
    # 创建新用户
    try:
        password_hash = generate_password_hash(password)
        user = User(username=username, password_hash=password_hash)
        db.session.add(user)
        db.session.commit()
        return user, None
    except Exception as e:
        db.session.rollback()
        return None, f"注册失败: {str(e)}"


def authenticate_user(username, password):
    """验证用户登录"""
    try:
        # 确保用户名和密码不为空
        if not username or not password:
            return None, "用户名或密码错误"
        
        # 查找用户（使用精确匹配，不区分大小写可能会有问题，所以保持区分大小写）
        user = User.query.filter_by(username=username).first()
        if not user:
            return None, "用户名或密码错误"
        
        # 验证密码哈希
        if not check_password_hash(user.password_hash, password):
            return None, "用户名或密码错误"
        
        return user, None
    except Exception as e:
        # 捕获数据库查询等异常
        return None, f"登录验证失败: {str(e)}"





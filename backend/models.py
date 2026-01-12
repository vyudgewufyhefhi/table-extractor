from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()


class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关联关系
    files = db.relationship('FileRecord', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class FileRecord(db.Model):
    """文件记录模型"""
    __tablename__ = 'file_records'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)  # pdf, png, jpg等
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    
    # 处理状态
    status = db.Column(db.String(20), default='uploaded')  # uploaded, processing, completed, failed
    
    # 识别结果（JSON格式存储）
    ai_result = db.Column(db.Text, nullable=True)  # AI识别的原始结果
    
    # 用户校正后的结果（JSON格式存储）
    corrected_result = db.Column(db.Text, nullable=True)
    
    # 生成的Excel文件路径
    excel_path = db.Column(db.String(500), nullable=True)
    
    # 时间戳
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'status': self.status,
            'ai_result': json.loads(self.ai_result) if self.ai_result else None,
            'corrected_result': json.loads(self.corrected_result) if self.corrected_result else None,
            'excel_path': self.excel_path,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    def set_ai_result(self, data):
        """设置AI识别结果"""
        self.ai_result = json.dumps(data, ensure_ascii=False)
        self.status = 'completed'
        self.processed_at = datetime.utcnow()
    
    def set_corrected_result(self, data):
        """设置用户校正后的结果"""
        self.corrected_result = json.dumps(data, ensure_ascii=False)
    
    def set_excel_path(self, path):
        """设置Excel文件路径"""
        self.excel_path = path
        self.completed_at = datetime.utcnow()


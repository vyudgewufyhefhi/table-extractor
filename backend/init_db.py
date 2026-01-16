"""初始化数据库"""
from app import app, db
from models import User, FileRecord, TextRecord

with app.app_context():
    # 创建所有表
    db.create_all()
    print("数据库初始化完成！")
    print("已创建表：users, file_records, text_records")


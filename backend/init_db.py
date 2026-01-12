"""初始化数据库"""
from app import app, db
from models import User, FileRecord

with app.app_context():
    # 创建所有表
    db.create_all()
    print("数据库初始化完成！")


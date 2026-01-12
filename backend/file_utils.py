import os
import uuid
from PIL import Image
from pdf2image import convert_from_path
import io
import base64
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()


ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'PNG', 'JPG', 'JPEG'}


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_file_type(filename):
    """获取文件类型"""
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    if ext == 'pdf':
        return 'pdf'
    elif ext in ['png', 'jpg', 'jpeg']:
        return 'image'
    return 'unknown'


def save_uploaded_file(file, upload_folder):
    """保存上传的文件"""
    if not allowed_file(file.filename):
        raise ValueError(f"不支持的文件类型: {file.filename}")
    
    # 生成唯一文件名
    file_ext = file.filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
    
    # 确保上传目录存在
    os.makedirs(upload_folder, exist_ok=True)
    
    # 保存文件
    file_path = os.path.join(upload_folder, unique_filename)
    file.save(file_path)
    
    return file_path, unique_filename, file_ext


def pdf_to_images(pdf_path, output_folder=None):
    """将PDF转换为图片列表"""
    try:
        # 支持自定义Poppler路径（Windows）
        poppler_path = os.getenv('POPPLER_PATH')
        if poppler_path and os.path.exists(poppler_path):
            images = convert_from_path(pdf_path, dpi=300, poppler_path=poppler_path)
        else:
            images = convert_from_path(pdf_path, dpi=300)
        image_paths = []
        
        os.makedirs(output_folder, exist_ok=True)
        
        for i, image in enumerate(images):
            # 保存为PNG
            image_filename = f"{uuid.uuid4().hex}_{i}.png"
            image_path = os.path.join(output_folder, image_filename)
            image.save(image_path, 'PNG')
            image_paths.append(image_path)
        
        return image_paths
    except Exception as e:
        raise Exception(f"PDF转换失败: {str(e)}")


def image_to_base64(image_path):
    """将图片转换为base64编码"""
    try:
        with open(image_path, 'rb') as f:
            image_data = f.read()
            base64_data = base64.b64encode(image_data).decode('utf-8')
            # 获取文件扩展名
            ext = image_path.rsplit('.', 1)[1].lower()
            mime_type = f"image/{ext}" if ext != 'jpg' else "image/jpeg"
            return f"data:{mime_type};base64,{base64_data}"
    except Exception as e:
        raise Exception(f"图片编码失败: {str(e)}")


def pdf_to_base64_preview(pdf_path, page=0):
    """将PDF的指定页面转换为base64预览"""
    try:
        # 支持自定义Poppler路径（Windows）
        poppler_path = os.getenv('POPPLER_PATH')
        if poppler_path and os.path.exists(poppler_path):
            images = convert_from_path(pdf_path, dpi=200, first_page=page+1, last_page=page+1, poppler_path=poppler_path)
        else:
            images = convert_from_path(pdf_path, dpi=200, first_page=page+1, last_page=page+1)
        if images:
            # 转换为base64
            img_byte_arr = io.BytesIO()
            images[0].save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            base64_data = base64.b64encode(img_byte_arr).decode('utf-8')
            return f"data:image/png;base64,{base64_data}"
        return None
    except Exception as e:
        raise Exception(f"PDF预览生成失败: {str(e)}")


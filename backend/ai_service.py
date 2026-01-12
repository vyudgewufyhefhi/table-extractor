import os
import base64
import dashscope
from dashscope import MultiModalConversation
from file_utils import pdf_to_images, image_to_base64
import json


def init_qwen_client(api_key, api_base=None):
    """初始化Qwen客户端"""
    dashscope.api_key = api_key
    if api_base:
        dashscope.base_http_api_url = api_base


def extract_table_from_image(image_path, api_key, api_base=None, model="qwen-vl-max"):
    """从图片中提取表格"""
    try:
        # 初始化客户端
        init_qwen_client(api_key, api_base)
        
        # 读取图片并转换为base64
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        # 构建提示词
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "image": f"data:image/png;base64,{image_data}"
                    },
                    {
                        "text": """请识别这张图片中的表格，并以JSON格式返回表格数据。
要求：
1. 识别表格中的所有单元格内容
2. 保持表格的行列结构
3. 返回格式为：
{
  "headers": ["列1", "列2", ...],
  "rows": [
    ["值1", "值2", ...],
    ["值1", "值2", ...]
  ]
}
如果图片中没有表格，返回 {"error": "未检测到表格"}
如果表格跨多行显示，请合并为一行数据。"""
                    }
                ]
            }
        ]
        
        # 调用API
        response = MultiModalConversation.call(
            model=model,
            messages=messages
        )
        
        if response.status_code == 200:
            # 提取返回的文本
            result_text = response.output.choices[0].message.content[0].text
            
            # 尝试解析JSON
            try:
                # 提取JSON部分（可能包含markdown代码块）
                if "```json" in result_text:
                    json_str = result_text.split("```json")[1].split("```")[0].strip()
                elif "```" in result_text:
                    json_str = result_text.split("```")[1].split("```")[0].strip()
                else:
                    json_str = result_text.strip()
                
                table_data = json.loads(json_str)
                
                # 验证数据结构
                if "error" in table_data:
                    return None, table_data.get("error", "识别失败")
                
                if "headers" not in table_data or "rows" not in table_data:
                    return None, "返回数据格式不正确"
                
                return table_data, None
            except json.JSONDecodeError as e:
                return None, f"JSON解析失败: {str(e)}"
        else:
            return None, f"API调用失败: {response.message}"
            
    except Exception as e:
        return None, f"识别过程出错: {str(e)}"


def extract_table_from_pdf(pdf_path, api_key, api_base=None, model="qwen-vl-max"):
    """从PDF中提取表格（处理所有页面）"""
    try:
        # 将PDF转换为图片
        temp_folder = os.path.join(os.path.dirname(pdf_path), "temp_images")
        os.makedirs(temp_folder, exist_ok=True)
        
        image_paths = pdf_to_images(pdf_path, temp_folder)
        
        if not image_paths:
            return None, "PDF转换失败"
        
        # 识别每一页的表格
        all_tables = []
        errors = []
        
        for i, image_path in enumerate(image_paths):
            table_data, error = extract_table_from_image(image_path, api_key, api_base, model)
            if table_data:
                # 添加页面信息
                table_data["page"] = i + 1
                all_tables.append(table_data)
            else:
                errors.append(f"第{i+1}页: {error}")
        
        # 清理临时图片
        for img_path in image_paths:
            try:
                os.remove(img_path)
            except:
                pass
        
        if all_tables:
            # 如果多页都有表格，合并或分别返回
            if len(all_tables) == 1:
                return all_tables[0], None
            else:
                # 返回多页表格数据
                return {
                    "multi_page": True,
                    "pages": all_tables,
                    "total_pages": len(all_tables)
                }, None
        else:
            return None, "; ".join(errors) if errors else "未识别到表格"
            
    except Exception as e:
        return None, f"PDF处理失败: {str(e)}"


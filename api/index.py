# -*- coding: utf-8 -*-
"""
DocParser Pro - 免费云部署版
适配 Vercel + Supabase
"""

import os
import sys
import uuid
import json
import base64
from datetime import datetime
from pathlib import Path

# 添加core模块路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'core'))

from flask import Flask, render_template, request, jsonify, send_file, Response

app = Flask(__name__, template_folder='../templates', static_folder='../static')

# 配置
SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '')

# 阿里云文档智能AccessKey（从环境变量读取，部署时配置）
ALIBABA_ACCESS_KEY = os.environ.get('ALIBABA_CLOUD_ACCESS_KEY_ID', '')
ALIBABA_SECRET = os.environ.get('ALIBABA_CLOUD_ACCESS_KEY_SECRET', '')  # OCR密钥

# 定价
PRICE_PER_PAGE = 0.25  # 元/页

# 简单的内存存储（Vercel无状态，实际用Supabase）
# 生产环境应该使用Supabase数据库
temp_storage = {}

def get_supabase_client():
    """获取Supabase客户端"""
    try:
        from supabase import create_client
        if SUPABASE_URL and SUPABASE_KEY:
            return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"Supabase连接失败: {e}")
    return None

@app.route('/')
def index():
    """首页"""
    return render_template('index.html')

@app.route('/api/health')
def health():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'time': datetime.now().isoformat(),
        'supabase_connected': bool(SUPABASE_URL and SUPABASE_KEY),
        'alibaba_configured': bool(ALIBABA_ACCESS_KEY and ALIBABA_SECRET)
    })

@app.route('/api/upload', methods=['POST'])
def api_upload():
    """上传PDF并转换"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '没有选择文件'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': '文件名为空'})
    
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'success': False, 'message': '只支持PDF文件'})
    
    output_format = request.form.get('format', 'excel')
    
    # 生成任务ID
    task_id = str(uuid.uuid4())[:8]
    
    try:
        # 读取PDF内容
        pdf_content = file.read()
        
        # 获取页数
        try:
            import PyPDF2
            from io import BytesIO
            pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_content))
            page_count = len(pdf_reader.pages)
        except:
            page_count = 1
        
        # 计算费用
        cost = page_count * PRICE_PER_PAGE
        
        # 保存到临时存储（实际应该上传到Supabase Storage）
        temp_storage[task_id] = {
            'pdf_content': base64.b64encode(pdf_content).decode(),
            'filename': file.filename,
            'page_count': page_count,
            'format': output_format,
            'cost': cost,
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': f'文件上传成功！共{page_count}页，费用{cost:.2f}元',
            'pages': page_count,
            'cost': cost
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'上传失败: {str(e)}'})

@app.route('/api/convert/<task_id>', methods=['POST'])
def api_convert(task_id):
    """执行转换"""
    if task_id not in temp_storage:
        return jsonify({'success': False, 'message': '任务不存在'})
    
    task = temp_storage[task_id]
    
    # 检查阿里云配置
    if not ALIBABA_ACCESS_KEY or not ALIBABA_SECRET:
        return jsonify({
            'success': False, 
            'message': 'OCR服务未配置，请联系管理员配置阿里云AccessKey'
        })
    
    try:
        # 导入转换器
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'core' / '.venv' / 'lib' / 'python3.12' / 'site-packages'))
        from converter import DocParserConverter
        
        # 创建转换器
        converter = DocParserConverter(
            access_key_id=ALIBABA_ACCESS_KEY,
            access_key_secret=ALIBABA_SECRET
        )
        
        # 解码PDF
        from io import BytesIO
        pdf_content = base64.b64decode(task['pdf_content'])
        
        # 保存临时文件
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp.write(pdf_content)
            tmp_path = tmp.name
        
        # 执行转换
        output_path = tmp_path.replace('.pdf', f'.{"xlsx" if task["format"] == "excel" else "docx"}')
        result = converter.convert(tmp_path, task['format'], output_path)
        
        # 读取结果
        with open(output_path, 'rb') as f:
            output_content = f.read()
        
        # 保存到任务
        task['status'] = 'completed'
        task['output_content'] = base64.b64encode(output_content).decode()
        task['output_filename'] = f"{task['filename'].replace('.pdf', '')}.{task['format'] == 'excel' and 'xlsx' or 'docx'}"
        
        # 清理临时文件
        os.unlink(tmp_path)
        if os.path.exists(output_path):
            os.unlink(output_path)
        
        return jsonify({
            'success': True,
            'message': '转换成功！',
            'download_url': f'/api/download/{task_id}'
        })
        
    except Exception as e:
        task['status'] = 'failed'
        task['error'] = str(e)
        return jsonify({'success': False, 'message': f'转换失败: {str(e)}'})

@app.route('/api/download/<task_id>')
def api_download(task_id):
    """下载转换后的文件"""
    if task_id not in temp_storage:
        return jsonify({'success': False, 'message': '文件不存在'}), 404
    
    task = temp_storage[task_id]
    
    if task.get('status') != 'completed':
        return jsonify({'success': False, 'message': '转换未完成'}), 400
    
    if 'output_content' not in task:
        return jsonify({'success': False, 'message': '文件内容不存在'}), 404
    
    output_content = base64.b64decode(task['output_content'])
    output_filename = task.get('output_filename', 'converted.xlsx')
    
    mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' if output_filename.endswith('.xlsx') else 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    
    return Response(
        output_content,
        mimetype=mime_type,
        headers={
            'Content-Disposition': f'attachment; filename={output_filename}'
        }
    )

@app.route('/api/status/<task_id>')
def api_status(task_id):
    """查询任务状态"""
    if task_id not in temp_storage:
        return jsonify({'success': False, 'message': '任务不存在'})
    
    task = temp_storage[task_id]
    return jsonify({
        'success': True,
        'status': task.get('status', 'unknown'),
        'error': task.get('error', '')
    })

# Vercel需要这个
app.debug = False

# 本地开发时使用
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

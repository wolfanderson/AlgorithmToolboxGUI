from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
import cv2
import numpy as np
from PIL import Image
import base64
import io
from typing import Dict, List, Any
import importlib
import sys
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='static')
CORS(app)

# 配置上传
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 算法模块注册表
ALGORITHM_MODULES = {}

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def register_algorithm(name: str, module_path: str):
    """注册算法模块"""
    ALGORITHM_MODULES[name] = module_path

def load_algorithm_modules():
    """加载所有算法模块"""
    algorithms_dir = 'algorithms'
    if os.path.exists(algorithms_dir):
        for filename in os.listdir(algorithms_dir):
            if filename.endswith('.py') and filename != '__init__.py':
                module_name = filename[:-3]
                try:
                    module = importlib.import_module(f'algorithms.{module_name}')
                    if hasattr(module, 'execute'):
                        ALGORITHM_MODULES[module_name] = module
                except Exception as e:
                    print(f"加载算法模块 {module_name} 失败: {e}")

# 初始化时加载算法模块
load_algorithm_modules()

@app.route('/')
def index():
    """主页面"""
    return send_from_directory('static', 'index.html')

@app.route('/style.css')
def style_css():
    """提供CSS文件"""
    return send_from_directory('static', 'style.css')

@app.route('/app.js')
def app_js():
    """提供JS文件"""
    return send_from_directory('static', 'app.js')

@app.route('/api/upload', methods=['POST'])
def upload_image():
    """上传图片到服务器"""
    try:
        print(f"收到上传请求，方法: {request.method}")
        print(f"Content-Type: {request.content_type}")
        print(f"请求文件: {list(request.files.keys())}")
        
        if 'file' not in request.files:
            print("错误: 请求中没有 'file' 字段")
            return jsonify({'error': '没有文件，请确保表单字段名为 file'}), 400
        
        file = request.files['file']
        print(f"文件对象: {file}")
        print(f"文件名: {file.filename}")
        print(f"文件类型: {file.content_type}")
        
        if file.filename == '':
            return jsonify({'error': '未选择文件'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': f'不支持的文件类型: {file.filename.rsplit(".", 1)[1] if "." in file.filename else "未知"}'}), 400
        
        # 确保上传目录存在
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        print(f"上传目录: {os.path.abspath(UPLOAD_FOLDER)}")
        
        # 生成安全的文件名（时间戳 + 原始文件名）
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        original_filename = secure_filename(file.filename)
        filename = f"{timestamp}_{original_filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        print(f"保存文件到: {os.path.abspath(filepath)}")
        
        # 保存文件
        file.save(filepath)
        
        if not os.path.exists(filepath):
            return jsonify({'error': '文件保存失败'}), 500
        
        file_size = os.path.getsize(filepath)
        print(f"文件保存成功，大小: {file_size} 字节")
        
        # 读取图片并转换为base64（用于前端显示）
        with open(filepath, 'rb') as f:
            image_data = f.read()
            img_base64 = base64.b64encode(image_data).decode()
            
            # 获取文件扩展名以确定MIME类型
            ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'png'
            mime_types = {
                'png': 'image/png',
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'gif': 'image/gif',
                'bmp': 'image/bmp',
                'tiff': 'image/tiff',
                'webp': 'image/webp'
            }
            mime_type = mime_types.get(ext, 'image/png')
        
        result = {
            'success': True,
            'filename': filename,
            'filepath': os.path.abspath(filepath),
            'url': f'/uploads/{filename}',
            'base64': f'data:{mime_type};base64,{img_base64}',
            'size': file_size
        }
        
        print(f"上传成功: {filename}")
        return jsonify(result)
            
    except Exception as e:
        import traceback
        error_msg = str(e)
        traceback.print_exc()
        print(f"上传异常: {error_msg}")
        return jsonify({'error': f'上传失败: {error_msg}'}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """提供上传的文件"""
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/api/algorithms', methods=['GET'])
def get_algorithms():
    """获取所有可用的算法列表"""
    algorithms = []
    for name, module in ALGORITHM_MODULES.items():
        if hasattr(module, 'get_info'):
            info = module.get_info()
            algorithms.append({
                'id': name,
                'name': info.get('name', name),
                'description': info.get('description', ''),
                'inputs': info.get('inputs', []),
                'outputs': info.get('outputs', []),
                'parameters': info.get('parameters', {})
            })
        else:
            algorithms.append({
                'id': name,
                'name': name,
                'description': f'算法模块: {name}',
                'inputs': ['image'],
                'outputs': ['image'],
                'parameters': {}
            })
    return jsonify(algorithms)

@app.route('/api/execute', methods=['POST'])
def execute_workflow():
    """执行工作流"""
    try:
        data = request.json
        nodes = data.get('nodes', [])
        edges = data.get('edges', [])
        input_image = data.get('inputImage')
        
        if not input_image:
            return jsonify({'error': '未提供输入图像'}), 400
        
        # 解码输入图像
        image_data = base64.b64decode(input_image.split(',')[1])
        image = Image.open(io.BytesIO(image_data))
        image_array = np.array(image)
        
        # 构建节点执行顺序（拓扑排序）
        execution_order = topological_sort(nodes, edges)
        
        # 存储每个节点的输出
        node_outputs = {}
        
        # 按顺序执行节点
        for node_id in execution_order:
            node = next((n for n in nodes if n['id'] == node_id), None)
            if not node:
                continue
            
            algorithm_name = node.get('type')
            if algorithm_name not in ALGORITHM_MODULES:
                return jsonify({'error': f'算法 {algorithm_name} 不存在'}), 400
            
            module = ALGORITHM_MODULES[algorithm_name]
            
            # 收集输入
            inputs = {}
            for edge in edges:
                if edge['target'] == node_id:
                    source_node_id = edge['source']
                    source_output_key = edge.get('sourceHandle', 'output')
                    if source_node_id in node_outputs:
                        inputs[edge.get('targetHandle', 'input')] = node_outputs[source_node_id].get(source_output_key)
            
            # 如果没有输入，使用原始图像
            if not inputs:
                inputs['image'] = image_array
            
            # 获取节点参数
            parameters = node.get('data', {}).get('parameters', {})
            
            # 执行算法
            try:
                result = module.execute(inputs, parameters)
                node_outputs[node_id] = result
            except Exception as e:
                return jsonify({'error': f'执行节点 {node_id} 时出错: {str(e)}'}), 500
        
        # 获取最终输出（最后一个节点或指定输出节点）
        final_output = None
        if node_outputs:
            # 找到没有输出的节点作为最终输出
            output_nodes = [n['id'] for n in nodes if not any(e['source'] == n['id'] for e in edges)]
            if output_nodes:
                final_output = node_outputs[output_nodes[0]]
            else:
                # 使用最后一个执行的节点
                final_output = node_outputs[execution_order[-1]]
        
        if final_output is None:
            return jsonify({'error': '没有输出结果'}), 400
        
        # 将输出图像编码为base64
        if isinstance(final_output, dict):
            output_image = final_output.get('image', final_output.get('output'))
        else:
            output_image = final_output
        
        if output_image is not None:
            if isinstance(output_image, np.ndarray):
                # 转换为PIL Image
                if len(output_image.shape) == 3:
                    output_image = Image.fromarray(output_image.astype(np.uint8))
                else:
                    output_image = Image.fromarray(output_image.astype(np.uint8), mode='L')
            
            # 编码为base64
            buffer = io.BytesIO()
            output_image.save(buffer, format='PNG')
            img_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            return jsonify({
                'success': True,
                'result': f'data:image/png;base64,{img_base64}'
            })
        else:
            return jsonify({'error': '算法未返回图像结果'}), 400
            
    except Exception as e:
        return jsonify({'error': f'执行工作流时出错: {str(e)}'}), 500

def topological_sort(nodes: List[Dict], edges: List[Dict]) -> List[str]:
    """拓扑排序，确定节点执行顺序"""
    # 构建图
    graph = {node['id']: [] for node in nodes}
    in_degree = {node['id']: 0 for node in nodes}
    
    for edge in edges:
        source = edge['source']
        target = edge['target']
        graph[source].append(target)
        in_degree[target] += 1
    
    # 找到所有入度为0的节点
    queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
    result = []
    
    while queue:
        node_id = queue.pop(0)
        result.append(node_id)
        
        for neighbor in graph[node_id]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    return result

if __name__ == '__main__':
    # 确保目录存在
    os.makedirs('static', exist_ok=True)
    os.makedirs('algorithms', exist_ok=True)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    print("=" * 50)
    print("工业质检算法组合平台")
    print("=" * 50)
    print(f"已加载 {len(ALGORITHM_MODULES)} 个算法模块:")
    for name in ALGORITHM_MODULES.keys():
        print(f"  - {name}")
    print("=" * 50)
    print("服务启动在: http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, port=5000)


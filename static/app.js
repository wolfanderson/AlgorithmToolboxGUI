// 全局状态
let nodes = [];
let edges = [];
let selectedNode = null;
let draggedNode = null;
let draggedAlgorithm = null;
let isConnecting = false;
let connectionStart = null;
let inputImage = null;
let uploadedImageInfo = null;  // 存储上传的图片信息
let algorithms = [];

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    loadAlgorithms();
    setupEventListeners();
    setupCanvas();
});

// 加载算法列表
async function loadAlgorithms() {
    try {
        const response = await fetch('/api/algorithms');
        algorithms = await response.json();
        renderAlgorithmList();
    } catch (error) {
        console.error('加载算法列表失败:', error);
    }
}

// 渲染算法列表
function renderAlgorithmList() {
    const list = document.getElementById('algorithmList');
    list.innerHTML = '';
    
    algorithms.forEach(algorithm => {
        const item = document.createElement('div');
        item.className = 'algorithm-item';
        item.draggable = true;
        item.innerHTML = `
            <h3>${algorithm.name}</h3>
            <p>${algorithm.description || ''}</p>
        `;
        
        item.addEventListener('dragstart', (e) => {
            draggedAlgorithm = algorithm;
            e.dataTransfer.effectAllowed = 'copy';
        });
        
        list.appendChild(item);
    });
}

// 设置事件监听器
function setupEventListeners() {
    const canvas = document.getElementById('canvas');
    const clearBtn = document.getElementById('clearBtn');
    const runBtn = document.getElementById('runBtn');
    const uploadBtn = document.getElementById('uploadBtn');
    const imageInput = document.getElementById('imageInput');
    
    // 清空画布
    clearBtn.addEventListener('click', () => {
        if (confirm('确定要清空画布吗？')) {
            nodes = [];
            edges = [];
            renderCanvas();
        }
    });
    
    // 执行工作流
    runBtn.addEventListener('click', executeWorkflow);
    
    // 上传图片
    uploadBtn.addEventListener('click', () => imageInput.click());
    imageInput.addEventListener('change', handleImageUpload);
    
    // 画布事件
    canvas.addEventListener('drop', handleDrop);
    canvas.addEventListener('dragover', (e) => e.preventDefault());
    canvas.addEventListener('click', handleCanvasClick);
}

// 设置画布
function setupCanvas() {
    renderCanvas();
}

// 处理图片上传
async function handleImageUpload(e) {
    const file = e.target.files[0];
    if (!file) return;
    
    // 显示上传中状态
    const uploadBtn = document.getElementById('uploadBtn');
    const originalText = uploadBtn.textContent;
    uploadBtn.disabled = true;
    uploadBtn.textContent = '上传中...';
    
    try {
        // 创建FormData
        const formData = new FormData();
        formData.append('file', file);
        
        // 上传到服务器
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            // 保存图片信息
            uploadedImageInfo = {
                filename: result.filename,
                filepath: result.filepath,
                url: result.url,
                size: result.size
            };
            
            // 使用服务器返回的base64或URL
            inputImage = result.base64;
            
            // 显示图片
            const img = document.getElementById('inputImage');
            img.src = inputImage;
            img.style.display = 'block';
            const placeholder = document.querySelector('#inputPreview .placeholder');
            placeholder.style.display = 'none';
            
            // 显示文件信息
            const infoDiv = document.getElementById('imageInfo');
            if (infoDiv) {
                infoDiv.innerHTML = `
                    <div style="font-size: 12px; color: #7f8c8d; margin-top: 10px;">
                        <div>文件名: ${result.filename}</div>
                        <div>路径: ${result.filepath}</div>
                        <div>大小: ${(result.size / 1024).toFixed(2)} KB</div>
                    </div>
                `;
            }
            
            console.log('图片上传成功:', result);
        } else {
            alert('上传失败: ' + (result.error || '未知错误'));
        }
    } catch (error) {
        console.error('上传错误:', error);
        alert('上传失败: ' + error.message);
    } finally {
        uploadBtn.disabled = false;
        uploadBtn.textContent = originalText;
    }
}

// 处理拖放
function handleDrop(e) {
    e.preventDefault();
    if (draggedAlgorithm) {
        const rect = document.getElementById('canvas').getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        createNode(draggedAlgorithm, x, y);
        draggedAlgorithm = null;
    }
}

// 创建节点
function createNode(algorithm, x, y) {
    const nodeId = `node_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const node = {
        id: nodeId,
        type: algorithm.id,
        x: x - 75,
        y: y - 50,
        data: {
            name: algorithm.name,
            parameters: {}
        }
    };
    
    nodes.push(node);
    renderCanvas();
}

// 渲染画布
function renderCanvas() {
    const canvas = document.getElementById('canvas');
    
    // 清除现有节点
    const existingNodes = canvas.querySelectorAll('.node');
    existingNodes.forEach(n => n.remove());
    
    // 渲染节点
    nodes.forEach(node => {
        const nodeElement = createNodeElement(node);
        canvas.appendChild(nodeElement);
    });
    
    // 渲染连接线
    renderConnections();
}

// 创建节点元素
function createNodeElement(node) {
    const algorithm = algorithms.find(a => a.id === node.type);
    const nodeDiv = document.createElement('div');
    nodeDiv.className = 'node';
    nodeDiv.id = node.id;
    nodeDiv.style.left = node.x + 'px';
    nodeDiv.style.top = node.y + 'px';
    
    nodeDiv.innerHTML = `
        <div class="node-header">${node.data.name || algorithm?.name || node.type}</div>
        <div class="node-body">
            <div class="node-ports">
                <div class="port input" data-node="${node.id}" data-port="input"></div>
                <div class="port output" data-node="${node.id}" data-port="output"></div>
            </div>
        </div>
    `;
    
    // 节点拖拽
    let isDragging = false;
    let startX, startY, initialX, initialY;
    
    const header = nodeDiv.querySelector('.node-header');
    header.addEventListener('mousedown', (e) => {
        isDragging = true;
        startX = e.clientX;
        startY = e.clientY;
        initialX = node.x;
        initialY = node.y;
        nodeDiv.style.cursor = 'grabbing';
        e.stopPropagation();
    });
    
    document.addEventListener('mousemove', (e) => {
        if (isDragging) {
            node.x = initialX + (e.clientX - startX);
            node.y = initialY + (e.clientY - startY);
            nodeDiv.style.left = node.x + 'px';
            nodeDiv.style.top = node.y + 'px';
            updateConnections(node.id);
        }
    });
    
    document.addEventListener('mouseup', () => {
        if (isDragging) {
            isDragging = false;
            nodeDiv.style.cursor = 'move';
        }
    });
    
    // 节点选择
    nodeDiv.addEventListener('click', (e) => {
        if (e.target === nodeDiv || e.target === header) {
            selectNode(node.id);
            e.stopPropagation();
        }
    });
    
    // 端口连接
    const ports = nodeDiv.querySelectorAll('.port');
    ports.forEach(port => {
        port.addEventListener('mousedown', (e) => {
            e.stopPropagation();
            startConnection(node.id, port.dataset.port, e);
        });
    });
    
    if (selectedNode === node.id) {
        nodeDiv.classList.add('selected');
    }
    
    return nodeDiv;
}

// 选择节点
function selectNode(nodeId) {
    selectedNode = nodeId;
    renderCanvas();
}

// 开始连接
function startConnection(nodeId, portType, e) {
    isConnecting = true;
    connectionStart = {
        nodeId,
        portType,
        x: e.clientX,
        y: e.clientY
    };
    
    document.addEventListener('mousemove', updateConnectionPreview);
    document.addEventListener('mouseup', finishConnection);
}

// 更新连接预览
function updateConnectionPreview(e) {
    if (!isConnecting) return;
    
    // 这里可以添加连接线预览
}

// 完成连接
function finishConnection(e) {
    if (!isConnecting) return;
    
    const target = e.target;
    if (target && target.classList && target.classList.contains('port')) {
        const targetNodeId = target.dataset.node;
        const targetPortType = target.dataset.port;
        
        // 只能从输出连接到输入，且不能连接到同一节点
        if (connectionStart.portType === 'output' && 
            targetPortType === 'input' && 
            connectionStart.nodeId !== targetNodeId) {
            const edge = {
                id: `edge_${Date.now()}`,
                source: connectionStart.nodeId,
                target: targetNodeId,
                sourceHandle: 'output',
                targetHandle: 'input'
            };
            
            // 检查是否已存在连接
            const exists = edges.some(ed => 
                ed.source === edge.source && ed.target === edge.target
            );
            
            if (!exists) {
                edges.push(edge);
                renderCanvas();
            }
        }
    }
    
    isConnecting = false;
    connectionStart = null;
    document.removeEventListener('mousemove', updateConnectionPreview);
    document.removeEventListener('mouseup', finishConnection);
}

// 绘制连接线
function drawConnection(edge) {
    const canvas = document.getElementById('canvas');
    let svg = canvas.querySelector('svg');
    if (!svg) {
        svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        canvas.appendChild(svg);
    }
    
    const sourceNode = document.getElementById(edge.source);
    const targetNode = document.getElementById(edge.target);
    
    if (!sourceNode || !targetNode) return;
    
    const sourcePort = sourceNode.querySelector('.port.output');
    const targetPort = targetNode.querySelector('.port.input');
    
    if (!sourcePort || !targetPort) return;
    
    const sourceRect = sourcePort.getBoundingClientRect();
    const targetRect = targetPort.getBoundingClientRect();
    const canvasRect = canvas.getBoundingClientRect();
    
    const x1 = sourceRect.left + sourceRect.width / 2 - canvasRect.left;
    const y1 = sourceRect.top + sourceRect.height / 2 - canvasRect.top;
    const x2 = targetRect.left + targetRect.width / 2 - canvasRect.left;
    const y2 = targetRect.top + targetRect.height / 2 - canvasRect.top;
    
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    const dx = x2 - x1;
    const dy = y2 - y1;
    const pathData = `M ${x1} ${y1} C ${x1 + dx * 0.5} ${y1}, ${x2 - dx * 0.5} ${y2}, ${x2} ${y2}`;
    path.setAttribute('d', pathData);
    path.setAttribute('class', 'connection-line');
    path.setAttribute('data-edge', edge.id);
    
    // 点击删除连接
    path.style.pointerEvents = 'all';
    path.style.cursor = 'pointer';
    path.addEventListener('click', () => {
        edges = edges.filter(e => e.id !== edge.id);
        renderCanvas();
    });
    
    svg.appendChild(path);
}

// 更新连接线位置
function updateConnections(nodeId) {
    // 重新渲染所有连接线
    renderConnections();
}

// 渲染所有连接线
function renderConnections() {
    const canvas = document.getElementById('canvas');
    let svg = canvas.querySelector('svg');
    if (!svg) {
        svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        canvas.appendChild(svg);
    }
    svg.innerHTML = '';
    
    edges.forEach(edge => {
        drawConnection(edge);
    });
}

// 处理画布点击
function handleCanvasClick(e) {
    if (e.target.id === 'canvas' || e.target.tagName === 'svg') {
        selectedNode = null;
        renderCanvas();
    }
}

// 执行工作流
async function executeWorkflow() {
    if (!inputImage) {
        alert('请先上传输入图片');
        return;
    }
    
    if (nodes.length === 0) {
        alert('请至少添加一个算法节点');
        return;
    }
    
    try {
        const runBtn = document.getElementById('runBtn');
        runBtn.disabled = true;
        runBtn.textContent = '执行中...';
        
        const response = await fetch('/api/execute', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                nodes: nodes,
                edges: edges,
                inputImage: inputImage
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            const outputImg = document.getElementById('outputImage');
            outputImg.src = result.result;
            outputImg.style.display = 'block';
            document.querySelector('#outputPreview .placeholder').style.display = 'none';
        } else {
            alert('执行失败: ' + (result.error || '未知错误'));
        }
    } catch (error) {
        alert('执行失败: ' + error.message);
    } finally {
        const runBtn = document.getElementById('runBtn');
        runBtn.disabled = false;
        runBtn.textContent = '执行工作流';
    }
}


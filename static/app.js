// 全局错误处理
window.addEventListener('error', (e) => {
    console.error('全局错误:', e.error);
    console.error('错误位置:', e.filename, ':', e.lineno);
    alert('发生错误: ' + e.message + '\n\n请查看控制台获取详细信息。');
});

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
    console.log('页面加载完成，开始初始化...');
    
    // 检查关键元素是否存在
    const uploadBtn = document.getElementById('uploadBtn');
    const imageInput = document.getElementById('imageInput');
    
    if (!uploadBtn) {
        console.error('错误: 上传按钮未找到！');
    } else {
        console.log('上传按钮已找到');
    }
    
    if (!imageInput) {
        console.error('错误: 文件输入框未找到！');
    } else {
        console.log('文件输入框已找到');
    }
    
    loadAlgorithms();
    setupEventListeners();
    setupCanvas();
    
    // 测试按钮是否可点击
    setTimeout(() => {
        testButtons();
    }, 100);
    
    console.log('初始化完成');
});

// 测试按钮功能
function testButtons() {
    console.log('=== 测试按钮功能 ===');
    const clearBtn = document.getElementById('clearBtn');
    const runBtn = document.getElementById('runBtn');
    const uploadBtn = document.getElementById('uploadBtn');
    
    if (clearBtn) {
        console.log('✓ 清空画布按钮存在，可点击:', clearBtn.style.pointerEvents !== 'none');
    }
    if (runBtn) {
        console.log('✓ 执行工作流按钮存在，可点击:', runBtn.style.pointerEvents !== 'none');
    }
    if (uploadBtn) {
        console.log('✓ 上传按钮存在，可点击:', uploadBtn.style.pointerEvents !== 'none');
    }
    console.log('=== 测试完成 ===');
}

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
    console.log('开始设置事件监听器...');
    
    const canvas = document.getElementById('canvas');
    const clearBtn = document.getElementById('clearBtn');
    const runBtn = document.getElementById('runBtn');
    const uploadBtn = document.getElementById('uploadBtn');
    const imageInput = document.getElementById('imageInput');
    
    // 清空画布按钮
    if (clearBtn) {
        clearBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            console.log('点击清空画布按钮');
            if (confirm('确定要清空画布吗？')) {
                nodes = [];
                edges = [];
                renderCanvas();
            }
        });
        console.log('清空画布按钮事件已绑定');
    } else {
        console.error('清空画布按钮未找到');
    }
    
    // 执行工作流按钮
    if (runBtn) {
        runBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            console.log('点击执行工作流按钮');
            executeWorkflow();
        });
        console.log('执行工作流按钮事件已绑定');
    } else {
        console.error('执行工作流按钮未找到');
    }
    
    // 上传图片按钮
    if (uploadBtn) {
        uploadBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            console.log('点击上传按钮');
            try {
                if (imageInput) {
                    imageInput.click();
                } else {
                    console.error('文件输入框不存在');
                    alert('文件输入框未找到，请刷新页面重试');
                }
            } catch (error) {
                console.error('触发文件选择失败:', error);
                alert('无法打开文件选择对话框: ' + error.message);
            }
        });
        console.log('上传按钮事件已绑定');
    } else {
        console.error('上传按钮未找到');
    }
    
    // 文件输入框
    if (imageInput) {
        imageInput.addEventListener('change', (e) => {
            console.log('文件选择改变事件触发');
            handleImageUpload(e);
        });
        console.log('文件输入框事件已绑定');
    } else {
        console.error('文件输入框未找到');
    }
    
    // 拖拽上传功能
    const inputPreview = document.getElementById('inputPreview');
    if (inputPreview) {
        inputPreview.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.stopPropagation();
            const dropZone = document.getElementById('dropZone');
            if (dropZone) {
                dropZone.style.borderColor = '#3498db';
                dropZone.style.backgroundColor = 'rgba(52, 152, 219, 0.1)';
            }
        });
        
        inputPreview.addEventListener('dragleave', (e) => {
            e.preventDefault();
            e.stopPropagation();
            const dropZone = document.getElementById('dropZone');
            if (dropZone) {
                dropZone.style.borderColor = 'transparent';
                dropZone.style.backgroundColor = 'transparent';
            }
        });
        
        inputPreview.addEventListener('drop', (e) => {
            e.preventDefault();
            e.stopPropagation();
            const dropZone = document.getElementById('dropZone');
            if (dropZone) {
                dropZone.style.borderColor = 'transparent';
                dropZone.style.backgroundColor = 'transparent';
            }
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                const file = files[0];
                if (file.type.startsWith('image/')) {
                    console.log('拖拽文件:', file.name);
                    // 创建一个模拟的change事件
                    const dataTransfer = new DataTransfer();
                    dataTransfer.items.add(file);
                    imageInput.files = dataTransfer.files;
                    const changeEvent = new Event('change', { bubbles: true });
                    imageInput.dispatchEvent(changeEvent);
                } else {
                    alert('请拖拽图片文件');
                }
            }
        });
    }
    
    // 画布事件
    if (canvas) {
        canvas.addEventListener('drop', handleDrop);
        canvas.addEventListener('dragover', (e) => e.preventDefault());
        canvas.addEventListener('click', handleCanvasClick);
        console.log('画布事件已绑定');
    } else {
        console.error('画布元素未找到');
    }
    
    // ROI选择事件
    setupROISelection();
    
    console.log('所有事件监听器设置完成');
}

// 设置ROI选择功能
function setupROISelection() {
    const img = document.getElementById('inputImage');
    const container = document.getElementById('imageContainer');
    
    if (!img || !container) return;
    
    let isSelecting = false;
    let startX = 0;
    let startY = 0;
    
    container.addEventListener('mousedown', (e) => {
        if (!roiSelecting) return;
        
        e.preventDefault();
        e.stopPropagation();
        
        isSelecting = true;
        const rect = container.getBoundingClientRect();
        startX = e.clientX - rect.left;
        startY = e.clientY - rect.top;
        
        const selector = document.getElementById('roiSelector');
        if (selector) {
            selector.style.left = startX + 'px';
            selector.style.top = startY + 'px';
            selector.style.width = '0px';
            selector.style.height = '0px';
            selector.style.display = 'block';
        }
    });
    
    container.addEventListener('mousemove', (e) => {
        if (!roiSelecting || !isSelecting) return;
        
        e.preventDefault();
        e.stopPropagation();
        
        const rect = container.getBoundingClientRect();
        const currentX = e.clientX - rect.left;
        const currentY = e.clientY - rect.top;
        
        const width = Math.abs(currentX - startX);
        const height = Math.abs(currentY - startY);
        const left = Math.min(startX, currentX);
        const top = Math.min(startY, currentY);
        
        const selector = document.getElementById('roiSelector');
        if (selector) {
            selector.style.left = left + 'px';
            selector.style.top = top + 'px';
            selector.style.width = width + 'px';
            selector.style.height = height + 'px';
        }
    });
    
    container.addEventListener('mouseup', (e) => {
        if (!roiSelecting || !isSelecting) return;
        
        e.preventDefault();
        e.stopPropagation();
        
        isSelecting = false;
        roiSelecting = false;
        
        if (container) {
            container.classList.remove('selecting');
        }
        
        // 计算相对于图片的坐标
        const imgRect = img.getBoundingClientRect();
        const containerRect = container.getBoundingClientRect();
        const selector = document.getElementById('roiSelector');
        
        if (!selector || selector.style.display === 'none') return;
        
        const selectorRect = selector.getBoundingClientRect();
        
        // 计算选择框相对于图片的位置
        const relativeLeft = selectorRect.left - imgRect.left;
        const relativeTop = selectorRect.top - imgRect.top;
        
        // 计算缩放比例
        const scaleX = img.naturalWidth / imgRect.width;
        const scaleY = img.naturalHeight / imgRect.height;
        
        // 转换为图片坐标
        const x = Math.max(0, Math.round(relativeLeft * scaleX));
        const y = Math.max(0, Math.round(relativeTop * scaleY));
        const width = Math.max(1, Math.round(parseFloat(selector.style.width) * scaleX));
        const height = Math.max(1, Math.round(parseFloat(selector.style.height) * scaleY));
        
        // 确保不超出图片范围
        const finalX = Math.min(x, img.naturalWidth - 1);
        const finalY = Math.min(y, img.naturalHeight - 1);
        const finalWidth = Math.min(width, img.naturalWidth - finalX);
        const finalHeight = Math.min(height, img.naturalHeight - finalY);
        
        // 更新输入框和节点参数
        if (document.getElementById('roiX')) {
            document.getElementById('roiX').value = finalX;
            document.getElementById('roiY').value = finalY;
            document.getElementById('roiWidth').value = finalWidth;
            document.getElementById('roiHeight').value = finalHeight;
            
            // 自动应用参数
            if (currentROINodeId) {
                applyROIParams(currentROINodeId);
            }
        }
        
        console.log('ROI选择完成:', { x: finalX, y: finalY, width: finalWidth, height: finalHeight });
    });
}

// 设置画布
function setupCanvas() {
    renderCanvas();
}

// 处理图片上传
async function handleImageUpload(e) {
    const file = e.target.files[0];
    if (!file) {
        console.log('未选择文件');
        return;
    }
    
    console.log('开始上传文件:', file.name, '大小:', file.size);
    
    // 显示上传中状态
    const uploadBtn = document.getElementById('uploadBtn');
    const originalText = uploadBtn.textContent;
    uploadBtn.disabled = true;
    uploadBtn.textContent = '上传中...';
    
    try {
        // 创建FormData
        const formData = new FormData();
        formData.append('file', file);
        
        console.log('发送上传请求到 /api/upload');
        
        // 上传到服务器
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
            // 注意：不要设置 Content-Type，让浏览器自动设置（包含boundary）
        });
        
        console.log('响应状态:', response.status, response.statusText);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('服务器错误:', errorText);
            throw new Error(`服务器错误: ${response.status} - ${errorText}`);
        }
        
        const result = await response.json();
        console.log('服务器响应:', result);
        
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
            if (placeholder) {
                placeholder.style.display = 'none';
            }
            
            // 图片加载后，如果有ROI选择，更新预览
            img.onload = () => {
                if (selectedNode) {
                    const node = nodes.find(n => n.id === selectedNode);
                    if (node && node.type === 'roi_extraction') {
                        updateROIPreview();
                    }
                }
            };
            
            // 显示文件信息
            const infoDiv = document.getElementById('imageInfo');
            if (infoDiv) {
                infoDiv.innerHTML = `
                    <div style="font-size: 12px; color: #7f8c8d; margin-top: 10px; text-align: left;">
                        <div><strong>文件名:</strong> ${result.filename}</div>
                        <div><strong>路径:</strong> ${result.filepath}</div>
                        <div><strong>大小:</strong> ${(result.size / 1024).toFixed(2)} KB</div>
                    </div>
                `;
            }
            
            console.log('图片上传成功:', result);
            alert('图片上传成功！\n文件名: ' + result.filename + '\n路径: ' + result.filepath);
        } else {
            const errorMsg = result.error || '未知错误';
            console.error('上传失败:', errorMsg);
            alert('上传失败: ' + errorMsg);
        }
    } catch (error) {
        console.error('上传错误详情:', error);
        console.error('错误堆栈:', error.stack);
        alert('上传失败: ' + error.message + '\n\n请检查浏览器控制台获取详细信息。');
    } finally {
        uploadBtn.disabled = false;
        uploadBtn.textContent = originalText;
        // 清空input，允许重复上传同一文件
        e.target.value = '';
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
    showNodeConfig(nodeId);
}

// 显示节点配置面板
function showNodeConfig(nodeId) {
    const node = nodes.find(n => n.id === nodeId);
    if (!node) return;
    
    const algorithm = algorithms.find(a => a.id === node.type);
    if (!algorithm) return;
    
    const configPanel = document.getElementById('nodeConfigPanel');
    const configContent = document.getElementById('nodeConfigContent');
    
    if (!configPanel || !configContent) return;
    
    // 如果是ROI提取算法，显示特殊配置界面
    if (node.type === 'roi_extraction') {
        showROIConfig(node, algorithm, configContent);
    } else {
        // 显示通用参数配置
        showGenericConfig(node, algorithm, configContent);
    }
    
    configPanel.style.display = 'block';
}

// 显示ROI配置界面
function showROIConfig(node, algorithm, container) {
    const params = node.data.parameters || {};
    
    container.innerHTML = `
        <div class="param-group">
            <label>ROI区域选择</label>
            <p style="font-size: 11px; color: #7f8c8d; margin: 5px 0;">在输入图像上拖拽鼠标框选ROI区域</p>
            <button id="enableROISelect" type="button">启用框选</button>
            <button id="clearROISelect" type="button" style="background: #e74c3c; margin-top: 5px;">清除选择</button>
        </div>
        <div class="param-group">
            <label>X坐标</label>
            <input type="number" id="roiX" value="${params.x || 0}" min="0">
        </div>
        <div class="param-group">
            <label>Y坐标</label>
            <input type="number" id="roiY" value="${params.y || 0}" min="0">
        </div>
        <div class="param-group">
            <label>宽度</label>
            <input type="number" id="roiWidth" value="${params.width || 100}" min="1">
        </div>
        <div class="param-group">
            <label>高度</label>
            <input type="number" id="roiHeight" value="${params.height || 100}" min="1">
        </div>
        <button id="applyROIParams" type="button">应用参数</button>
    `;
    
    // 绑定事件
    document.getElementById('enableROISelect').addEventListener('click', () => {
        enableROISelection(node.id);
    });
    
    document.getElementById('clearROISelect').addEventListener('click', () => {
        clearROISelection();
    });
    
    document.getElementById('applyROIParams').addEventListener('click', () => {
        applyROIParams(node.id);
    });
    
    // 输入框变化时更新参数
    ['roiX', 'roiY', 'roiWidth', 'roiHeight'].forEach(id => {
        document.getElementById(id).addEventListener('input', () => {
            updateROIPreview();
        });
    });
    
    // 显示已有的ROI选择
    setTimeout(() => {
        updateROIPreview();
    }, 100);
}

// 显示通用参数配置
function showGenericConfig(node, algorithm, container) {
    const params = node.data.parameters || {};
    const paramDefs = algorithm.parameters || {};
    
    let html = '';
    for (const [key, def] of Object.entries(paramDefs)) {
        const value = params[key] !== undefined ? params[key] : def.default;
        html += `
            <div class="param-group">
                <label>${def.label || key}</label>
                <input type="${def.type === 'number' ? 'number' : 'text'}" 
                       id="param_${key}" 
                       value="${value}"
                       ${def.min !== undefined ? `min="${def.min}"` : ''}
                       ${def.max !== undefined ? `max="${def.max}"` : ''}>
            </div>
        `;
    }
    
    if (html) {
        html += '<button id="applyGenericParams" type="button">应用参数</button>';
    } else {
        html = '<p style="color: #7f8c8d; font-size: 12px;">该算法无需配置参数</p>';
    }
    
    container.innerHTML = html;
    
    if (document.getElementById('applyGenericParams')) {
        document.getElementById('applyGenericParams').addEventListener('click', () => {
            applyGenericParams(node.id, paramDefs);
        });
    }
}

// 应用通用参数
function applyGenericParams(nodeId, paramDefs) {
    const node = nodes.find(n => n.id === nodeId);
    if (!node) return;
    
    const params = {};
    for (const key of Object.keys(paramDefs)) {
        const input = document.getElementById(`param_${key}`);
        if (input) {
            const value = paramDefs[key].type === 'number' ? 
                parseFloat(input.value) : input.value;
            params[key] = value;
        }
    }
    
    node.data.parameters = params;
    console.log('参数已更新:', params);
}

// 启用ROI选择
let roiSelecting = false;
let roiStartX = 0;
let roiStartY = 0;
let currentROINodeId = null;

function enableROISelection(nodeId) {
    currentROINodeId = nodeId;
    roiSelecting = true;
    
    const img = document.getElementById('inputImage');
    const container = document.getElementById('imageContainer');
    
    if (!img || img.style.display === 'none') {
        alert('请先上传输入图片');
        roiSelecting = false;
        return;
    }
    
    if (container) {
        container.classList.add('selecting');
    }
    
    // 清除之前的选择
    clearROISelection();
}

// 清除ROI选择
function clearROISelection() {
    const selector = document.getElementById('roiSelector');
    if (selector) {
        selector.style.display = 'none';
    }
    
    // 清除输入框
    if (document.getElementById('roiX')) {
        document.getElementById('roiX').value = 0;
        document.getElementById('roiY').value = 0;
        document.getElementById('roiWidth').value = 100;
        document.getElementById('roiHeight').value = 100;
    }
}

// 更新ROI预览
function updateROIPreview() {
    const xInput = document.getElementById('roiX');
    const yInput = document.getElementById('roiY');
    const widthInput = document.getElementById('roiWidth');
    const heightInput = document.getElementById('roiHeight');
    
    if (!xInput || !yInput || !widthInput || !heightInput) return;
    
    const x = parseInt(xInput.value || 0);
    const y = parseInt(yInput.value || 0);
    const width = parseInt(widthInput.value || 100);
    const height = parseInt(heightInput.value || 100);
    
    const img = document.getElementById('inputImage');
    const selector = document.getElementById('roiSelector');
    const container = document.getElementById('imageContainer');
    
    if (!img || !selector || !container || img.style.display === 'none') {
        if (selector) selector.style.display = 'none';
        return;
    }
    
    // 等待图片加载完成
    if (!img.complete || img.naturalWidth === 0) {
        img.onload = () => updateROIPreview();
        return;
    }
    
    const imgRect = img.getBoundingClientRect();
    const containerRect = container.getBoundingClientRect();
    
    // 计算缩放比例
    const scaleX = imgRect.width / img.naturalWidth;
    const scaleY = imgRect.height / img.naturalHeight;
    
    // 计算显示坐标
    const displayX = x * scaleX;
    const displayY = y * scaleY;
    const displayWidth = width * scaleX;
    const displayHeight = height * scaleY;
    
    // 设置选择框位置（相对于容器）
    selector.style.left = displayX + 'px';
    selector.style.top = displayY + 'px';
    selector.style.width = displayWidth + 'px';
    selector.style.height = displayHeight + 'px';
    selector.style.display = (width > 0 && height > 0) ? 'block' : 'none';
}

// 应用ROI参数
function applyROIParams(nodeId) {
    const node = nodes.find(n => n.id === nodeId);
    if (!node) return;
    
    const x = parseInt(document.getElementById('roiX')?.value || 0);
    const y = parseInt(document.getElementById('roiY')?.value || 0);
    const width = parseInt(document.getElementById('roiWidth')?.value || 100);
    const height = parseInt(document.getElementById('roiHeight')?.value || 100);
    
    node.data.parameters = { x, y, width, height };
    console.log('ROI参数已更新:', node.data.parameters);
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
    
    // 创建预览线
    createPreviewLine();
}

// 创建预览线
function createPreviewLine() {
    const canvas = document.getElementById('canvas');
    let svg = canvas.querySelector('svg');
    if (!svg) {
        svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        canvas.appendChild(svg);
    }
    
    // 移除旧的预览线
    const oldPreview = svg.querySelector('#preview-line');
    if (oldPreview) {
        oldPreview.remove();
    }
    
    const previewPath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    previewPath.setAttribute('id', 'preview-line');
    previewPath.setAttribute('class', 'connection-preview');
    svg.appendChild(previewPath);
}

// 更新连接预览
function updateConnectionPreview(e) {
    if (!isConnecting || !connectionStart) return;
    
    const canvas = document.getElementById('canvas');
    const svg = canvas.querySelector('svg');
    if (!svg) return;
    
    const previewPath = svg.querySelector('#preview-line');
    if (!previewPath) return;
    
    // 获取起始端口位置
    const sourceNode = document.getElementById(connectionStart.nodeId);
    if (!sourceNode) return;
    
    const sourcePort = sourceNode.querySelector(`.port.${connectionStart.portType}`);
    if (!sourcePort) return;
    
    const sourceRect = sourcePort.getBoundingClientRect();
    const canvasRect = canvas.getBoundingClientRect();
    
    const x1 = sourceRect.left + sourceRect.width / 2 - canvasRect.left;
    const y1 = sourceRect.top + sourceRect.height / 2 - canvasRect.top;
    
    // 获取当前鼠标位置（相对于画布）
    const x2 = e.clientX - canvasRect.left;
    const y2 = e.clientY - canvasRect.top;
    
    // 绘制贝塞尔曲线
    const dx = x2 - x1;
    const dy = y2 - y1;
    const pathData = `M ${x1} ${y1} C ${x1 + dx * 0.5} ${y1}, ${x2 - dx * 0.5} ${y2}, ${x2} ${y2}`;
    previewPath.setAttribute('d', pathData);
}

// 完成连接
function finishConnection(e) {
    if (!isConnecting) return;
    
    // 清除预览线
    const canvas = document.getElementById('canvas');
    const svg = canvas.querySelector('svg');
    if (svg) {
        const previewPath = svg.querySelector('#preview-line');
        if (previewPath) {
            previewPath.remove();
        }
    }
    
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
    
    // 保存预览线（如果存在）
    const previewLine = svg.querySelector('#preview-line');
    
    // 清空所有连接线（但保留预览线）
    const allPaths = svg.querySelectorAll('path');
    allPaths.forEach(path => {
        if (path.id !== 'preview-line') {
            path.remove();
        }
    });
    
    // 重新绘制所有连接线
    edges.forEach(edge => {
        drawConnection(edge);
    });
    
    // 如果之前有预览线，重新添加
    if (previewLine && svg.querySelector('#preview-line') === null) {
        svg.appendChild(previewLine);
    }
}

// 处理画布点击
function handleCanvasClick(e) {
    if (e.target.id === 'canvas' || e.target.tagName === 'svg') {
        selectedNode = null;
        renderCanvas();
        // 隐藏配置面板
        const configPanel = document.getElementById('nodeConfigPanel');
        if (configPanel) {
            configPanel.style.display = 'none';
        }
        
        // 如果正在连接，取消连接并清除预览线
        if (isConnecting) {
            const canvas = document.getElementById('canvas');
            const svg = canvas.querySelector('svg');
            if (svg) {
                const previewPath = svg.querySelector('#preview-line');
                if (previewPath) {
                    previewPath.remove();
                }
            }
            isConnecting = false;
            connectionStart = null;
            document.removeEventListener('mousemove', updateConnectionPreview);
            document.removeEventListener('mouseup', finishConnection);
        }
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


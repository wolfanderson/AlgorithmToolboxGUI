# UML设计图文档

## 1. 系统类图 (System Class Diagram)

### 1.1 完整系统类图

```mermaid
classDiagram
    %% Flask应用核心类
    class FlaskApp {
        -ALGORITHM_MODULES: Dict[str, ModuleType]
        -UPLOAD_FOLDER: str
        -ALLOWED_EXTENSIONS: Set[str]
        +load_algorithm_modules()
        +register_algorithm(name: str, module: ModuleType)
        +allowed_file(filename: str) bool
        +upload_image() Response
        +get_algorithms() Response
        +execute_workflow() Response
    }
    
    %% 工作流执行器
    class WorkflowExecutor {
        -nodes: List[Dict]
        -edges: List[Dict]
        -input_image: np.ndarray
        -node_outputs: Dict[str, Any]
        +topological_sort(nodes, edges) List[str]
        +execute_workflow() Dict[str, Any]
        +collect_node_inputs(node_id: str) Dict[str, Any]
        +execute_node(node: Dict) Dict[str, Any]
    }
    
    %% 算法模块接口
    class AlgorithmModule {
        <<interface>>
        +get_info() Dict[str, Any]
        +execute(inputs: Dict, parameters: Dict) Dict[str, Any]
    }
    
    %% 具体算法实现
    class ImageFilter {
        +get_info() Dict
        +execute(inputs: Dict, parameters: Dict) Dict
    }
    
    class EdgeDetection {
        +get_info() Dict
        +execute(inputs: Dict, parameters: Dict) Dict
    }
    
    class ROIExtraction {
        +get_info() Dict
        +execute(inputs: Dict, parameters: Dict) Dict
    }
    
    class OCRRecognition {
        -_ocr_instances: Dict[str, PaddleOCR]
        +get_ocr_instance(use_angle_cls: bool) PaddleOCR
        +get_info() Dict
        +execute(inputs: Dict, parameters: Dict) Dict
    }
    
    class ImageSegmentation {
        +get_info() Dict
        +execute(inputs: Dict, parameters: Dict) Dict
    }
    
    class ImageRegistration {
        +get_info() Dict
        +execute(inputs: Dict, parameters: Dict) Dict
    }
    
    %% 数据模型
    class Node {
        +id: str
        +type: str
        +x: int
        +y: int
        +data: Dict[str, Any]
    }
    
    class Edge {
        +id: str
        +source: str
        +target: str
        +sourceHandle: str
        +targetHandle: str
    }
    
    class Workflow {
        +nodes: List[Node]
        +edges: List[Edge]
        +inputImage: str
    }
    
    %% 关系
    FlaskApp --> WorkflowExecutor : 使用
    FlaskApp --> AlgorithmModule : 管理
    WorkflowExecutor --> Node : 处理
    WorkflowExecutor --> Edge : 处理
    WorkflowExecutor --> AlgorithmModule : 调用
    AlgorithmModule <|.. ImageFilter
    AlgorithmModule <|.. EdgeDetection
    AlgorithmModule <|.. ROIExtraction
    AlgorithmModule <|.. OCRRecognition
    AlgorithmModule <|.. ImageSegmentation
    AlgorithmModule <|.. ImageRegistration
    Workflow --> Node : 包含
    Workflow --> Edge : 包含
```

## 2. 前端类图 (Frontend Class Diagram)

```mermaid
classDiagram
    %% 画布管理
    class WorkflowCanvas {
        -canvas: HTMLElement
        -nodes: Array~Node~
        -edges: Array~Edge~
        -selectedNode: string
        -connectionStart: Object
        -isConnecting: boolean
        +renderCanvas()
        +createNode(algorithm: Object, x: number, y: number) string
        +deleteNode(nodeId: string)
        +selectNode(nodeId: string)
        +renderConnections()
        +startConnection(nodeId: string, portType: string, e: Event)
        +finishConnection(nodeId: string, portType: string)
    }
    
    %% 节点渲染器
    class NodeRenderer {
        +createNodeElement(node: Object) HTMLElement
        +updateNodePosition(nodeId: string, x: number, y: number)
        +drawConnection(edge: Object)
        +createPreviewLine()
        +updateConnectionPreview(e: Event)
        +removePreviewLine()
    }
    
    %% 图像上传器
    class ImageUploader {
        -inputImage: string
        -uploadedImageInfo: Object
        +handleImageUpload(file: File)
        +displayImagePreview(base64: string)
        +enableROISelection()
        +updateROISelector(x: number, y: number, width: number, height: number)
    }
    
    %% 工作流执行器
    class WorkflowExecutor {
        -nodes: Array
        -edges: Array
        -inputImage: string
        +executeWorkflow()
        +validateWorkflow() boolean
        +displayResult(result: Object)
    }
    
    %% 配置面板
    class ConfigPanel {
        -selectedNode: Object
        +showNodeConfig(node: Object)
        +hideNodeConfig()
        +renderNodeConfig(node: Object) HTMLElement
        +showROIConfig()
        +applyROIParameters()
    }
    
    %% ROI选择器
    class ROISelector {
        -isSelecting: boolean
        -startX: number
        -startY: number
        -currentX: number
        -currentY: number
        +enableSelection()
        +updateSelector(x: number, y: number, width: number, height: number)
        +clearSelection()
        +getROIParameters() Object
    }
    
    %% 算法列表管理器
    class AlgorithmListManager {
        -algorithms: Array~Object~
        +loadAlgorithms()
        +displayAlgorithms()
        +filterAlgorithms(keyword: string)
    }
    
    WorkflowCanvas --> NodeRenderer : 使用
    WorkflowCanvas --> ImageUploader : 使用
    WorkflowCanvas --> ConfigPanel : 使用
    WorkflowCanvas --> WorkflowExecutor : 使用
    ConfigPanel --> ROISelector : 使用
    WorkflowExecutor --> ImageUploader : 使用
```

## 3. 组件图 (Component Diagram)

```mermaid
graph TB
    subgraph "前端组件"
        A[HTML页面]
        B[CSS样式]
        C[JavaScript核心]
        D[画布组件]
        E[配置面板组件]
        F[图像上传组件]
    end
    
    subgraph "后端组件"
        G[Flask应用]
        H[路由处理器]
        I[文件上传处理器]
        J[工作流执行器]
        K[算法模块管理器]
    end
    
    subgraph "算法组件"
        L[图像滤波]
        M[边缘检测]
        N[ROI提取]
        O[OCR识别]
        P[图像分割]
        Q[图像配准]
    end
    
    subgraph "数据存储"
        R[上传文件存储]
        S[临时数据缓存]
    end
    
    A --> C
    B --> A
    C --> D
    C --> E
    C --> F
    
    D --> G
    E --> G
    F --> G
    
    G --> H
    H --> I
    H --> J
    J --> K
    
    K --> L
    K --> M
    K --> N
    K --> O
    K --> P
    K --> Q
    
    I --> R
    J --> S
```

## 4. 部署图 (Deployment Diagram)

```mermaid
graph TB
    subgraph "客户端"
        A[Web浏览器]
        B[用户界面]
    end
    
    subgraph "应用服务器"
        C[Flask Web服务器]
        D[Python运行时]
        E[算法执行引擎]
    end
    
    subgraph "文件系统"
        F[算法模块目录]
        G[上传文件目录]
        H[静态资源目录]
    end
    
    subgraph "外部依赖"
        I[OpenCV库]
        J[NumPy库]
        K[PaddleOCR库]
    end
    
    A -->|HTTP请求| C
    B --> A
    C --> D
    D --> E
    E --> F
    C --> G
    C --> H
    E --> I
    E --> J
    E --> K
```

## 5. 状态图 (State Diagram)

### 5.1 节点状态图

```mermaid
stateDiagram-v2
    [*] --> 未选中
    未选中 --> 选中: 点击节点
    选中 --> 未选中: 点击空白区域
    选中 --> 配置中: 打开配置面板
    配置中 --> 选中: 关闭配置面板
    选中 --> 连接中: 点击输出端口
    连接中 --> 选中: 取消连接
    连接中 --> 已连接: 连接到输入端口
    已连接 --> 选中: 点击节点
    选中 --> 执行中: 工作流执行
    执行中 --> 已完成: 执行成功
    执行中 --> 选中: 执行失败
    已完成 --> 选中: 重置
```

### 5.2 工作流执行状态图

```mermaid
stateDiagram-v2
    [*] --> 空闲
    空闲 --> 验证中: 点击执行
    验证中 --> 验证失败: 验证不通过
    验证中 --> 准备中: 验证通过
    验证失败 --> 空闲: 显示错误
    准备中 --> 执行中: 开始执行
    执行中 --> 执行中: 执行节点
    执行中 --> 执行失败: 节点执行错误
    执行中 --> 完成: 所有节点执行完成
    执行失败 --> 空闲: 显示错误
    完成 --> 空闲: 显示结果
```

## 6. 活动图 (Activity Diagram)

### 6.1 完整工作流执行活动图

```mermaid
flowchart TD
    Start([开始执行工作流]) --> Validate{验证输入}
    Validate -->|失败| Error1[返回错误]
    Validate -->|通过| Decode[解码输入图像]
    Decode --> Build[构建执行图]
    Build --> Sort[拓扑排序]
    Sort --> Init[初始化节点输出缓存]
    Init --> Loop{还有未执行节点?}
    Loop -->|是| GetNode[获取下一个节点]
    GetNode --> CheckInput{节点有输入连接?}
    CheckInput -->|是| GetInput[从上游节点获取输入]
    CheckInput -->|否| UseOriginal[使用原始图像]
    GetInput --> LoadModule[加载算法模块]
    UseOriginal --> LoadModule
    LoadModule --> GetParams[获取节点参数]
    GetParams --> Execute[调用算法execute]
    Execute --> CheckResult{执行成功?}
    CheckResult -->|失败| Error2[返回错误]
    CheckResult -->|成功| SaveOutput[保存节点输出]
    SaveOutput --> Loop
    Loop -->|否| GetFinal[获取最终输出]
    GetFinal --> Encode[编码为Base64]
    Encode --> Return[返回结果]
    Return --> End([结束])
    Error1 --> End
    Error2 --> End
```

### 6.2 节点创建活动图

```mermaid
flowchart TD
    Start([用户拖拽算法]) --> Check{算法有效?}
    Check -->|否| End([结束])
    Check -->|是| GetPos[获取鼠标位置]
    GetPos --> Create[创建节点对象]
    Create --> AddToCanvas[添加到画布]
    AddToCanvas --> Render[渲染节点]
    Render --> AddListener[添加事件监听器]
    AddListener --> End
```

## 7. 序列图详细版

### 7.1 算法模块加载序列图

```mermaid
sequenceDiagram
    participant App as Flask应用
    participant Loader as 模块加载器
    participant FS as 文件系统
    participant Import as importlib
    participant Module as 算法模块
    participant Registry as 模块注册表
    
    App->>Loader: load_algorithm_modules()
    Loader->>FS: 扫描algorithms目录
    FS-->>Loader: 返回文件列表
    
    loop 每个.py文件
        Loader->>Loader: 提取模块名
        Loader->>Import: import_module()
        Import->>Module: 导入模块
        Module-->>Import: 模块对象
        Import-->>Loader: 返回模块
        
        Loader->>Module: 检查execute函数
        Module-->>Loader: 函数存在
        
        Loader->>Registry: 注册模块
        Registry-->>Loader: 注册成功
    end
    
    Loader-->>App: 加载完成
```

### 7.2 ROI配置序列图

```mermaid
sequenceDiagram
    participant User as 用户
    participant Node as 节点
    participant Panel as 配置面板
    participant Image as 图像容器
    participant Selector as ROI选择器
    participant Canvas as 画布
    
    User->>Node: 点击ROI节点
    Node->>Panel: 显示配置面板
    Panel->>Panel: 渲染ROI配置UI
    
    User->>Panel: 点击"启用框选"
    Panel->>Image: 启用ROI选择模式
    Image->>Selector: 激活选择器
    
    User->>Image: 按下鼠标
    Image->>Selector: mousedown事件
    Selector->>Selector: 记录起始坐标
    
    User->>Image: 拖拽鼠标
    Image->>Selector: mousemove事件
    Selector->>Selector: 更新选择框
    Selector->>Canvas: 绘制选择框
    
    User->>Image: 释放鼠标
    Image->>Selector: mouseup事件
    Selector->>Selector: 计算ROI参数
    Selector->>Panel: 更新参数输入框
    Panel->>Node: 保存参数到节点
```

## 8. 包图 (Package Diagram)

```mermaid
graph TB
    subgraph "算法工具箱GUI系统"
        subgraph "前端包"
            A1[static.index.html]
            A2[static.style.css]
            A3[static.app.js]
        end
        
        subgraph "后端包"
            B1[app.py]
            B2[路由模块]
            B3[工作流执行模块]
            B4[文件处理模块]
        end
        
        subgraph "算法包"
            C1[algorithms.__init__]
            C2[algorithms.image_filter]
            C3[algorithms.edge_detection]
            C4[algorithms.roi_extraction]
            C5[algorithms.ocr_recognition]
            C6[algorithms.image_segmentation]
            C7[algorithms.image_registration]
        end
        
        subgraph "工具包"
            D1[requirements.txt]
            D2[配置文件]
        end
    end
    
    A3 --> B1
    B1 --> C1
    C1 --> C2
    C1 --> C3
    C1 --> C4
    C1 --> C5
    C1 --> C6
    C1 --> C7
```

## 9. 交互图 (Interaction Diagram)

### 9.1 多节点工作流交互图

```mermaid
sequenceDiagram
    participant User as 用户
    participant Frontend as 前端
    participant Backend as 后端
    participant Executor as 执行器
    participant Node1 as 节点1(滤波)
    participant Node2 as 节点2(ROI)
    participant Node3 as 节点3(OCR)
    
    User->>Frontend: 执行工作流
    Frontend->>Backend: POST /api/execute
    Backend->>Executor: 执行工作流
    
    Executor->>Executor: 拓扑排序: [Node1, Node2, Node3]
    
    Executor->>Node1: execute(原始图像)
    Node1->>Node1: 图像滤波处理
    Node1-->>Executor: 返回滤波结果
    
    Executor->>Node2: execute(滤波结果)
    Node2->>Node2: ROI提取
    Node2-->>Executor: 返回ROI区域
    
    Executor->>Node3: execute(ROI区域)
    Node3->>Node3: OCR识别
    Node3-->>Executor: 返回识别结果+文本
    
    Executor-->>Backend: 返回最终结果
    Backend-->>Frontend: JSON响应
    Frontend-->>User: 显示结果
```

## 10. 数据模型图 (Data Model Diagram)

```mermaid
erDiagram
    WORKFLOW ||--o{ NODE : contains
    WORKFLOW ||--o{ EDGE : contains
    NODE ||--o{ PARAMETER : has
    EDGE }o--|| NODE : connects_from
    EDGE }o--|| NODE : connects_to
    
    WORKFLOW {
        string id
        string name
        datetime created_at
        datetime updated_at
    }
    
    NODE {
        string id
        string type
        int x
        int y
        json data
    }
    
    EDGE {
        string id
        string source
        string target
        string sourceHandle
        string targetHandle
    }
    
    PARAMETER {
        string key
        string type
        any value
        any default
    }
    
    ALGORITHM {
        string name
        string description
        json inputs
        json outputs
        json parameters
    }
```

---

**文档版本**: v1.0  
**最后更新**: 2024-12-01


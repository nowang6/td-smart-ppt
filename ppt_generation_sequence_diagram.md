# PPT生成系统时序图

基于代码分析和日志记录，以下是PPT生成系统的完整时序图：

```mermaid
sequenceDiagram
    participant User as 用户
    participant NextJS as Next.js前端
    participant FastAPI as FastAPI后端
    participant Cache as 缓存
    participant LLM as LLM服务
    participant ImageGen as 图像生成服务

    Note over User,ImageGen: 阶段1: 文件上传和预处理

    User->>NextJS: 上传Word文档
    NextJS->>FastAPI: POST /api/v1/files/upload
    FastAPI->>Cache: 创建临时文件记录
    FastAPI-->>NextJS: 返回临时文件路径

    NextJS->>FastAPI: POST /api/v1/files/decompose
    FastAPI->>FastAPI: 解析文档内容
    FastAPI->>Cache: 存储解析结果
    FastAPI-->>NextJS: 返回分解后的文档信息

    Note over User,ImageGen: 阶段2: 创建演示文稿

    NextJS->>FastAPI: POST /api/v1/presentation/create
    FastAPI->>Cache: 创建Presentation记录
    FastAPI-->>NextJS: 返回Presentation ID

    Note over User,ImageGen: 阶段3: 生成大纲

    NextJS->>FastAPI: GET /api/v1/outlines/stream/{presentation_id}
    FastAPI->>LLM: 调用LLM生成大纲
    LLM-->>FastAPI: 流式返回大纲内容
    FastAPI->>Cache: 存储大纲数据
    FastAPI-->>NextJS: 流式返回大纲

    Note over User,ImageGen: 阶段4: 准备演示文稿

    NextJS->>FastAPI: GET /api/v1/template-management/summary
    FastAPI->>Cache: 查询模板信息
    FastAPI-->>NextJS: 返回模板摘要

    NextJS->>FastAPI: POST /api/v1/presentation/prepare
    FastAPI->>FastAPI: 生成演示文稿结构
    FastAPI->>Cache: 更新Presentation结构
    FastAPI-->>NextJS: 返回准备完成状态

    Note over User,ImageGen: 阶段5: 流式生成幻灯片

    NextJS->>NextJS: 导航到 /presentation?id={id}&stream=true
    NextJS->>FastAPI: GET /api/v1/presentation/stream/{presentation_id}

    loop 为每个幻灯片
        FastAPI->>LLM: 生成幻灯片内容
        LLM-->>FastAPI: 返回幻灯片内容
        FastAPI->>ImageGen: 生成图像
        ImageGen-->>FastAPI: 返回图像URL
        FastAPI->>Cache: 存储幻灯片和资产
        FastAPI-->>NextJS: 流式返回幻灯片数据
    end

    FastAPI-->>NextJS: 流式生成完成

    Note over User,ImageGen: 阶段6: 获取最终演示文稿

    NextJS->>FastAPI: GET /api/v1/presentation/{presentation_id}
    FastAPI->>Cache: 查询完整演示文稿
    FastAPI-->>NextJS: 返回完整演示文稿数据

    Note over User,ImageGen: 阶段7: 导出演示文稿

    NextJS->>FastAPI: POST /api/v1/presentation/export
    FastAPI->>FastAPI: 生成PPTX/PDF文件
    FastAPI-->>NextJS: 返回导出文件路径

    NextJS-->>User: 显示生成的演示文稿
```

## 关键流程说明

### 1. 文件上传和预处理阶段
- **文件上传**: 用户上传Word文档，系统保存为临时文件
- **文档分解**: 解析文档内容，提取文本信息用于后续处理

### 2. 演示文稿框架创建
- 创建空的演示文稿记录，分配唯一ID

### 3. 大纲生成阶段
- 使用LLM服务根据文档内容生成演示文稿大纲
- 采用流式传输方式实时返回生成进度

### 4. 演示文稿准备阶段
- 查询可用模板信息
- 根据大纲和模板生成演示文稿结构

### 5. 流式幻灯片生成
- 核心生成阶段，为每个幻灯片:
  - 调用LLM生成具体内容
  - 调用图像生成服务创建配图
  - 存储幻灯片数据和资产
  - 流式返回给前端

### 6. 最终处理和导出
- 获取完整演示文稿数据
- 支持更新和编辑
- 导出为PPTX或PDF格式

## 技术特点

1. **异步流式处理**: 使用SSE(Server-Sent Events)实现实时进度更新
2. **模块化设计**: 各阶段职责清晰，便于扩展和维护
3. **并发处理**: 幻灯片生成和图像生成并行执行
4. **错误处理**: 完善的异常处理和重试机制
5. **模板系统**: 支持自定义模板和布局管理
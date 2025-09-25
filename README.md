# TD Smart PPT

一个智能PPT生成系统，结合了现代化的前端界面和强大的后端AI处理能力。

## 项目概述

TD Smart PPT 是一个全栈Web应用程序，旨在帮助用户快速生成高质量的演示文稿。项目采用前后端分离的架构，前端使用 Next.js + TypeScript + Bootstrap，后端使用 Python + Pydantic AI。

## 技术栈

### 前端 (Frontend)
- **框架**: Next.js 15.5.4
- **语言**: TypeScript
- **UI框架**: Bootstrap 5.3.8
- **包管理器**: Yarn
- **开发工具**: ESLint, Turbopack

### 后端 (Backend)
- **语言**: Python 3.12+
- **AI框架**: Pydantic AI 1.0.10+
- **包管理器**: UV
- **依赖管理**: pyproject.toml

## 项目结构

```
td-smart-ppt/
├── frontend/                 # Next.js 前端应用
│   ├── src/
│   │   ├── app/             # App Router 页面
│   │   └── components/      # React 组件
│   ├── public/              # 静态资源
│   ├── package.json         # 前端依赖配置
│   └── tsconfig.json        # TypeScript 配置
├── backend/                 # Python 后端服务
│   ├── main.py              # 主程序入口
│   ├── pyproject.toml       # Python 项目配置
│   └── uv.lock              # 依赖锁定文件
└── README.md                # 项目说明文档
```

## 快速开始

### 环境要求

- Node.js 18+ 
- Python 3.12+
- Yarn 包管理器
- UV 包管理器 (Python)

### 安装依赖

#### 前端依赖
```bash
cd frontend
yarn install
```

#### 后端依赖
```bash
cd backend
uv sync
```

### 启动开发服务器

#### 启动前端 (端口 3000)
```bash
cd frontend
yarn dev
```

#### 启动后端
```bash
cd backend
uv run python main.py
```

访问 [http://localhost:3000](http://localhost:3000) 查看前端应用。

## 开发指南

### 前端开发

- 使用 `yarn dev` 启动开发服务器，支持热重载
- 使用 `yarn build` 构建生产版本
- 使用 `yarn lint` 进行代码检查
- 支持 Turbopack 加速构建

### 后端开发

- 使用 `uv run python main.py` 运行后端服务
- 使用 `uv add <package>` 添加新的依赖
- 使用 `uv sync` 同步依赖

### 代码规范

- 前端使用 ESLint 进行代码检查
- TypeScript 严格模式
- 遵循 Next.js 最佳实践

## 功能特性

- 🎨 现代化响应式UI设计
- ⚡ 快速构建和热重载
- 🤖 AI驱动的PPT生成
- 📱 移动端友好
- 🔧 TypeScript 类型安全
- 🎯 Bootstrap 组件库

## 部署

### 前端部署
```bash
cd frontend
yarn build
yarn start
```

### 后端部署
```bash
cd backend
uv run python main.py
```

## 贡献指南

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

如有问题或建议，请通过以下方式联系：

- 创建 Issue
- 发送邮件至项目维护者

---

**注意**: 这是一个开发中的项目，功能正在不断完善中。

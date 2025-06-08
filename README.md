# MyFast-Admin

<p align="center">
  <img src="src/assets/logo.png" width="120" alt="MyFast-Admin Logo" />
</p>

<div align="center">

MyFast-Admin 是一款基于 FastAPI 和 Vue3 的现代化企业级开发框架，提供完整的前后端解决方案。

[![Vue](https://img.shields.io/badge/Vue-3.x-brightgreen.svg)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100.0+-blue.svg)](https://fastapi.tiangolo.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-blue.svg)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-4.x-yellow.svg)](https://vitejs.dev/)
[![Element Plus](https://img.shields.io/badge/Element_Plus-2.x-blue.svg)](https://element-plus.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

## 🌟 项目简介

MyFast-Admin 是一款开源的企业级应用开发框架，采用前后端分离架构，旨在提供高效、安全、可扩展的解决方案。框架集成了现代化的前端技术栈和强大的后端支持，帮助开发者快速构建企业级应用。

## ✨ 核心特性

- **现代化技术栈**：基于 Vue 3、TypeScript、Vite 和 FastAPI 等最新技术
- **企业级解决方案**：内置权限管理、用户管理、菜单管理等核心功能
- **组件化开发**：丰富的业务组件和自定义组件库
- **响应式设计**：自适应多种屏幕尺寸，支持移动端和桌面端
- **API 自动生成**：后端 API 自动生成文档和类型定义
- **多语言支持**：内置国际化解决方案
- **主题定制**：可自定义主题颜色和布局
- **开发效率工具**：集成代码生成、热重载等开发工具

## 🔥 技术架构

### 前端技术栈

- 核心框架：Vue 3
- 工程化：Vite 4
- 语言：TypeScript 5
- UI 库：Element Plus 2
- 状态管理：Pinia
- 路由管理：Vue Router 4
- HTTP 客户端：Axios
- CSS 预处理：Sass/SCSS

### 后端技术栈

- 核心框架：FastAPI
- 语言：Python 3.9+
- ORM：SQLAlchemy 2.0+
- 数据库：PostgreSQL/MySQL/SQLite
- 认证：OAuth2 + JWT
- 任务队列：Celery（可选）
- 缓存：Redis（可选）
- 文档：Swagger/ReDoc

## 📦 项目结构

```
myfast-frontend/            # 前端项目目录
├── public/                 # 静态资源
├── src/                    # 源码目录
│   ├── api/                # API 接口
│   ├── assets/             # 资源文件
│   ├── components/         # 公共组件
│   ├── composables/        # 组合式函数
│   ├── layouts/            # 布局组件
│   ├── router/             # 路由配置
│   ├── store/              # 状态管理
│   ├── styles/             # 全局样式
│   ├── utils/              # 工具函数
│   └── views/              # 页面视图
├── .env.development        # 开发环境变量
├── .env.production         # 生产环境变量
└── vite.config.ts          # Vite 配置

myfast-backend/             # 后端项目目录
├── app/                    # 应用代码
│   ├── api/                # API 路由
│   ├── core/               # 核心模块
│   ├── crud/               # CRUD 操作
│   ├── db/                 # 数据库模型和会话
│   ├── models/             # 数据模型
│   ├── schemas/            # Pydantic 模式
│   └── services/           # 业务服务
├── static/                 # 静态文件
└── tests/                  # 测试代码
```

## 🚀 快速开始

### 前端开发

1. 安装依赖

```bash
cd myfast-frontend
npm install
```

2. 启动开发服务器

```bash
npm run dev
```

3. 构建生产版本

```bash
npm run build
```

4. 代码检查

```bash
npm run lint
```

### 后端开发

1. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. 安装依赖

```bash
cd myfast-backend
pip install -r requirements.txt
```

3. 设置环境变量

```bash
# 创建 .env 文件并添加必要的环境变量
touch .env
```

4. 启动开发服务器

```bash
uvicorn app.main:app --reload
```

## 💻 开发指南

### IDE 推荐

- [VSCode](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar)（并禁用 Vetur）

### Vue 类型支持

TypeScript 默认无法处理 `.vue` 导入的类型信息，因此我们使用 `vue-tsc` 替代 `tsc` 进行类型检查。在编辑器中，需要 [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) 使 TypeScript 语言服务能够识别 `.vue` 类型。

### 自定义配置

查看 [Vite 配置参考](https://vitejs.dev/config/) 获取更多配置信息。

## 📃 功能列表

- 用户认证
  - 登录/注册
  - 第三方登录集成
  - 多因素认证
  
- 用户管理
  - 用户列表
  - 用户详情
  - 用户角色分配
  
- 角色管理
  - 角色列表
  - 权限分配
  
- 菜单管理
  - 菜单树
  - 动态路由
  
- 部门管理
  - 部门树
  - 人员分配
  
- 系统配置
  - 参数设置
  - 字典管理
  
- 操作日志
  - 登录日志
  - 操作审计

## 🔐 安全建议

- 定期更新依赖包
- 启用 HTTPS
- 实施 CSRF 保护
- 使用安全的认证方式
- 进行输入验证和过滤

## 🤝 参与贡献

1. Fork 本仓库
2. 创建特性分支 `git checkout -b feature/your-feature`
3. 提交更改 `git commit -m 'Add some feature'`
4. 推送到分支 `git push origin feature/your-feature`
5. 提交 Pull Request

## 📄 许可证

[MIT License](LICENSE)

## 📬 联系方式

- 项目维护者：[维护者姓名]
- 电子邮件：[邮箱地址]

---

© 2023-2024 MyFast-Admin 团队. 保留所有权利.

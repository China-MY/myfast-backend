# MyFast-Admin 后端

<div align="center">

MyFast-Admin 是一款基于 FastAPI 和 Vue3 的现代化企业级开发框架，这是项目的后端部分。

[![FastAPI](https://img.shields.io/badge/FastAPI-0.100.0+-blue.svg)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-orange.svg)](https://www.sqlalchemy.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

## 🌟 项目简介

MyFast-Admin 后端采用 FastAPI 框架开发，提供高性能、易于使用的 RESTful API 接口，支持前端各项功能的数据处理和业务逻辑。

## ✨ 核心特性

- **高性能框架**：基于 FastAPI 和 Pydantic，提供极速的 API 响应
- **完整的权限系统**：基于 RBAC 模型的权限控制
- **用户认证**：使用 JWT 令牌的安全认证机制
- **ORM 支持**：基于 SQLAlchemy 2.0 的数据库访问层
- **自动文档**：集成 Swagger UI 和 ReDoc 的 API 文档
- **数据验证**：严格的请求和响应数据验证
- **异步支持**：支持异步数据库操作和请求处理
- **系统配置**：灵活的系统参数和字典管理

## 🔥 技术栈

- **核心框架**：FastAPI
- **语言**：Python 3.9+
- **ORM**：SQLAlchemy 2.0+
- **数据库**：MySQL/SQLite
- **认证**：OAuth2 + JWT
- **文档**：Swagger/ReDoc
- **数据验证**：Pydantic
- **异步处理**：asyncio

## 📦 项目结构
```
myfast-backend/
├── app/
│   ├── api/                # API路由
│   │   ├── deps.py         # 依赖项
│   │   └── v1/             # API v1版本
│   │       ├── auth/       # 认证相关API
│   │       ├── system/     # 系统管理API
│   │       ├── monitor/    # 监控相关API
│   │       ├── endpoints/  # 其他端点
│   │       └── api.py      # API注册
│   ├── core/               # 核心配置
│   ├── crud/               # CRUD操作
│   ├── db/                 # 数据库相关
│   ├── models/             # 数据模型
│   ├── schemas/            # 数据架构
│   ├── schema/             # 补充架构
│   ├── service/            # 业务服务层
│   ├── common/             # 通用功能
│   ├── utils/              # 工具函数
│   └── main.py             # 应用入口
├── sql/                    # SQL脚本文件
├── requirements.txt        # 依赖列表
└── README.md               # 项目说明
```

## 🚀 快速开始

### 环境要求

- Python 3.9+
- 数据库：MySQL/SQLite

### 安装步骤

1. 克隆仓库

```bash
git clone https://gitee.com/myxzgzs/myfast-backend.git
或
git clone https://github.com/China-MY/myfast-backend.git
cd myfast-backend
```

2. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 安装依赖

```bash
pip install -r requirements.txt
```

4. 启动开发服务器

```bash
uvicorn app.main:app --reload
```

5. 访问 API 文档

## 📃 API 功能列表

- **认证管理**
  - 用户登录
  - 注册
  - 令牌刷新
  
- **用户管理**
  - 用户列表
  - 用户详情
  - 用户创建/更新/删除
  - 用户角色分配
  
- **角色管理**
  - 角色列表
  - 角色权限分配
  - 角色创建/更新/删除
  
- **菜单管理**
  - 菜单树
  - 菜单创建/更新/删除
  
- **字典管理**
  - 字典类型管理
  - 字典数据管理
  - 支持按字典类型查询字典数据
  - 字典数据的增删改查
  
- **系统配置**
  - 参数设置
  - 系统配置管理

## 💻 开发指南

### 添加新的 API 端点

1. 在 `app/api/v1/` 下创建新的路由文件
2. 在 `app/models/` 中定义数据模型
3. 在 `app/schemas/` 中创建请求和响应模式
4. 在 `app/crud/` 中实现 CRUD 操作
5. 在 `app/api/v1/your_module.py` 中实现 API 逻辑

### 数据库迁移

项目使用 SQLAlchemy 模型定义数据库结构。如果需要进行数据库迁移，可以考虑使用 Alembic 工具。

## 🔐 安全建议

- 定期更新依赖包
- 使用环境变量存储敏感信息
- 实施适当的速率限制
- 启用 CORS 保护
- 使用 HTTPS

## 🤝 参与贡献

1. Fork 本仓库
2. 创建特性分支 `git checkout -b feature/your-feature`
3. 提交更改 `git commit -m 'Add some feature'`
4. 推送到分支 `git push origin feature/your-feature`
5. 提交 Pull Request

## 📄 许可证

[MIT License](LICENSE)

---

© 2025-2026 明裕学长 团队. 保留所有权利.
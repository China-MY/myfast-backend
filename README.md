# MyFast-Admin 后端

<div align="center">

MyFast-Admin 是一款基于 FastAPI 和 Vue3 的现代化企业级开发框架，这是项目的后端部分。

[![FastAPI](https://img.shields.io/badge/FastAPI-0.100.0+-blue.svg)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-orange.svg)](https://www.sqlalchemy.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

## 🌟 项目简介

MyFast-Admin 后端采用 FastAPI 框架开发，提供高性能、易于使用的 RESTful API 接口，支持前端各项功能的数据处理和业务逻辑。系统采用现代化的异步处理方式，保证高并发场景下的稳定性和响应速度。

## 🔗 配套前端项目

配套的前端项目采用Vue3 + TypeScript + Element Plus开发，提供完整的管理界面：

- Gitee仓库：[https://gitee.com/myxzgzs/myfast-frontend.git](https://gitee.com/myxzgzs/myfast-frontend.git)
- GitHub仓库：[https://github.com/China-MY/myfast-frontend.git](https://github.com/China-MY/myfast-frontend.git)

## ✨ 核心特性

- **高性能框架**：基于 FastAPI 和 Pydantic，提供极速的 API 响应
- **完整的权限系统**：基于 RBAC 模型的权限控制
- **用户认证**：使用 JWT 令牌的安全认证机制
- **ORM 支持**：基于 SQLAlchemy 2.0 的数据库访问层
- **自动文档**：集成 Swagger UI 和 ReDoc 的 API 文档
- **数据验证**：严格的请求和响应数据验证
- **异步支持**：支持异步数据库操作和请求处理
- **系统配置**：灵活的系统参数和字典管理
- **日志管理**：基于 loguru 的高效日志记录
- **定时任务**：支持 APScheduler 的定时任务管理
- **国际化支持**：多语言系统配置

## 🔥 技术栈

- **核心框架**：FastAPI 0.100.0+
- **语言**：Python 3.9+
- **ORM**：SQLAlchemy 2.0+
- **数据库**：MySQL/SQLite
- **认证**：OAuth2 + JWT
- **文档**：Swagger/ReDoc
- **数据验证**：Pydantic 2.0+
- **异步处理**：asyncio
- **定时任务**：APScheduler 3.10.0+
- **日志系统**：loguru 0.7.0+
- **数据迁移**：Alembic 1.11.0+
- **HTTP客户端**：httpx

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
│   │       ├── tool/       # 工具类API
│   │       ├── api.py      # API注册
│   │       └── __init__.py # API初始化
│   ├── core/               # 核心配置
│   ├── crud/               # CRUD操作
│   ├── db/                 # 数据库相关
│   ├── models/             # 数据模型
│   ├── schemas/            # 数据架构
│   ├── service/            # 业务服务层
│   ├── common/             # 通用功能
│   ├── utils/              # 工具函数
│   ├── __init__.py         # 应用初始化
│   └── main.py             # 应用入口
├── sql/                    # SQL脚本文件
├── requirements.txt        # 依赖列表
└── README.md               # 项目说明
```

## 🔄 与前端对接

MyFast-Admin 后端与前端通过 RESTful API 进行交互，前端项目结构如下：

```
myfast-frontend/
├── src/
│   ├── api/                      # API接口定义
│   │   ├── index.ts              # API入口文件
│   │   ├── renzheng.ts           # 认证API
│   │   ├── yonghuguanli.ts       # 用户管理API
│   │   ├── jiaoseguanli.ts       # 角色管理API
│   │   ├── caidanguanli.ts       # 菜单管理API
│   │   ├── zidianguanli.ts       # 字典管理API
│   │   ├── bumenguanli.ts        # 部门管理API
│   │   ├── gangweiguanli.ts      # 岗位管理API
│   │   ├── canshushezhi.ts       # 参数设置API
│   │   ├── zaixianyonghu.ts      # 在线用户API
│   │   ├── shujujiankong.ts      # 数据监控API
│   │   ├── fuwuqijiankong.ts     # 服务器监控API
│   │   ├── huancunjiankong.ts    # 缓存监控API
│   │   ├── dingshirenwu.ts       # 定时任务API
│   │   └── ...                   # 其他API文件
│   └── ...                       # 其他前端源码
└── ...                           # 其他前端配置文件
```

后端API严格按照前端需求进行设计，确保无缝对接。

## 🚀 快速开始

### 环境要求

- Python 3.9+
- 数据库：MySQL/SQLite
- Node.js 16+ (前后端联调)

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

4. 配置环境变量

创建`.env`文件，参考以下配置：

```
# 数据库配置
DATABASE_URL=sqlite:///./myfast.db
# 或使用MySQL
# DATABASE_URL=mysql+pymysql://user:password@localhost/dbname

# JWT配置
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS配置
BACKEND_CORS_ORIGINS=["http://localhost:8080","http://localhost:3000","http://localhost:5173"]
```

5. 启动开发服务器

```bash
uvicorn app.main:app --reload
```

6. 访问 API 文档

浏览器访问：http://localhost:8000/docs 查看 Swagger API 文档
或访问：http://localhost:8000/redoc 查看 ReDoc 格式文档

7. 系统默认账号

```
默认管理员账号：admin
默认管理员密码：Qwe123123
```

## 📃 API 功能列表

- **认证管理 (auth)**
  - 用户登录
  - 用户注册
  - 令牌刷新
  
- **用户中心**
  - 用户信息获取
  - 修改密码
  - 个人信息编辑
  
- **系统管理 (system)**
  - 用户管理
    - 用户列表
    - 用户详情
    - 用户创建/更新/删除
    - 用户角色分配
  
  - 角色管理
    - 角色列表
    - 角色权限分配
    - 角色创建/更新/删除
  
  - 菜单管理
    - 菜单树
    - 菜单创建/更新/删除
  
  - 字典管理
    - 字典类型管理
    - 字典数据管理
    - 支持按字典类型查询字典数据
  
  - 部门管理
    - 部门树结构
    - 部门创建/更新/删除
    
  - 岗位管理
    - 岗位列表
    - 岗位创建/更新/删除
    
  - 参数设置
    - 系统参数配置
    - 参数创建/更新/删除
  
- **监控管理 (monitor)**
  - 在线用户
    - 在线用户查询
    - 强制下线
  
  - 服务器监控
    - CPU/内存/磁盘使用率
    - 系统负载
  
  - 缓存监控
    - 缓存信息
    - 缓存键值管理
  
  - 数据监控
    - 数据库连接信息
    - SQL执行监控
    
- **定时任务 (task)**
  - 任务列表
  - 任务创建/更新/删除
  - 任务执行/暂停
  - 执行日志查询

## 📸 项目截图

### API文档
![API文档](./docs/1.png)

### 登录接口
![登录接口](./docs/2.png)

### 用户管理API
![用户管理API](./docs/3.png)

### 角色管理API
![角色管理API](./docs/4.png)

### 菜单管理API
![菜单管理API](./docs/5.png)

### 字典管理API
![字典管理API](./docs/6.png)

### 部门管理API
![部门管理API](./docs/7.png)

### 岗位管理API
![岗位管理API](./docs/8.png)

### 参数设置API
![参数设置API](./docs/9.png)

### 在线用户API
![在线用户API](./docs/10.png)

### 服务器监控API
![服务器监控API](./docs/11.png)

### 缓存监控API
![缓存监控API](./docs/12.png)

### 定时任务API
![定时任务API](./docs/13.png)

## 💻 开发指南

### 添加新的 API 端点

1. 在 `app/api/v1/` 下创建新的路由文件
2. 在 `app/models/` 中定义数据模型
3. 在 `app/schemas/` 中创建请求和响应模式
4. 在 `app/crud/` 中实现 CRUD 操作
5. 在 `app/api/v1/your_module.py` 中实现 API 逻辑
6. 在 `app/api/v1/api.py` 中注册新的路由

### 数据库迁移

项目使用 SQLAlchemy 模型定义数据库结构，并使用 Alembic 进行数据库迁移：

```bash
# 初始化迁移
alembic init migrations

# 创建迁移
alembic revision --autogenerate -m "描述你的变更"

# 应用迁移
alembic upgrade head
```

### 依赖注入

项目使用 FastAPI 的依赖注入系统，在 `app/api/deps.py` 中定义了常用的依赖项：

- 数据库会话
- 当前用户获取
- 权限检查
- 角色验证

### 前后端联调

1. 确保后端服务运行在 http://localhost:8000
2. 前端项目配置 API 基础路径指向后端服务
3. 在前端 `vite.config.ts` 中配置代理：

```typescript
export default defineConfig({
  // ...其他配置
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
```

4. 确保后端 CORS 设置正确，允许前端域名访问

## 🔐 安全建议

- 定期更新依赖包
- 使用环境变量存储敏感信息
- 实施适当的速率限制
- 启用 CORS 保护
- 使用 HTTPS
- 定期审查日志文件
- 使用强密码策略
- 实施多因素认证
- 定期备份数据库

## 🤝 参与贡献

1. Fork 本仓库
2. 创建特性分支 `git checkout -b feature/your-feature`
3. 提交更改 `git commit -m 'Add some feature'`
4. 推送到分支 `git push origin feature/your-feature`
5. 提交 Pull Request

## 📄 许可证

[MIT License](LICENSE)

---

© 2025-2026 明裕学长. 保留所有权利.
# MyFastAdmin 企业级后台管理系统

基于FastAPI+Vue3的企业级前后端分离管理系统框架，参考若依管理框架的架构设计，实现了基本的权限管理功能。

## 技术栈

### 后端
- Python 3.9+
- FastAPI
- SQLAlchemy
- MySQL
- Redis

### 前端
- Vue 3
- TypeScript
- Ant Design Vue
- Vite

## 项目结构

```
myfast-backend/                    # 后端项目目录
├── app/                           # 应用目录
│   ├── api/                       # API接口层
│   │   ├── auth/                  # 认证相关接口
│   │   ├── system/                # 系统管理接口
│   │   ├── monitor/               # 系统监控接口
│   │   └── tool/                  # 系统工具接口
│   ├── core/                      # 核心模块
│   │   ├── security.py            # 安全相关
│   │   ├── deps.py                # 依赖注入
│   │   └── token.py               # 令牌处理
│   ├── db/                        # 数据库相关
│   │   ├── database.py            # 数据库连接
│   │   └── redis.py               # Redis连接
│   ├── domain/                    # 领域层
│   │   ├── models/                # 数据模型
│   │   └── schemas/               # 数据传输对象(DTO)
│   ├── service/                   # 服务层
│   │   ├── system/                # 系统管理服务
│   │   ├── monitor/               # 系统监控服务
│   │   └── tool/                  # 系统工具服务
│   ├── common/                    # 公共模块
│   │   ├── constants.py           # 常量定义
│   │   ├── exception.py           # 异常处理
│   │   └── response.py            # 响应处理
│   ├── utils/                     # 工具类
│   ├── middleware/                # 中间件
│   └── config/                    # 配置文件
│       └── settings.py            # 应用配置
├── sql/                           # SQL脚本
├── requirements.txt               # 项目依赖
└── main.py                        # 主入口
```

## 功能模块

### 系统管理
- 用户管理
- 角色管理
- 菜单管理
- 部门管理
- 岗位管理
- 字典管理
- 参数设置

### 系统监控
- 在线用户
- 定时任务
- 数据监控
- 服务监控
- 缓存监控
- 缓存列表

### 系统工具
- 代码生成
- 系统接口
- 表单构建

## 快速开始

### 环境准备
- Python 3.9+
- MySQL 5.7+
- Redis

### 后端部署
1. 克隆项目
```bash
git clone https://github.com/your-username/myfast-admin.git
cd myfast-admin
```

2. 安装依赖
```bash
cd myfast-backend
pip install -r requirements.txt
```

3. 创建数据库并导入SQL
```bash
# 创建数据库
mysql -u root -p -e "CREATE DATABASE myfast_admin CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;"
# 导入SQL
mysql -u root -p myfast_admin < sql/myfast_admin.sql
```

4. 修改配置
```bash
# 复制环境变量示例文件
cp .env.example .env
# 修改数据库配置和其他配置
```

5. 启动项目
```bash
python -m app.main
```

### 前端部署
1. 进入前端目录
```bash
cd myfast-frontend
```

2. 安装依赖
```bash
npm install
```

3. 启动开发服务器
```bash
npm run dev
```

4. 构建生产环境
```bash
npm run build
```

## 项目特点

1. 基于FastAPI实现，性能卓越
2. 遵循RESTful API设计规范
3. 基于RBAC的权限控制
4. 前后端分离架构
5. 多数据源支持
6. 代码生成功能
7. 丰富的UI组件

## 开发计划

- [x] 项目基础框架搭建
- [x] 系统管理模块
- [ ] 系统监控模块
- [ ] 系统工具模块
- [ ] 多租户支持
- [ ] 国际化支持
- [ ] 主题定制
- [ ] 更多功能...

## 贡献指南

欢迎提交Pull Request或Issue，一起完善这个项目。

## 许可证

MIT 
# DocParser Pro - 免费云部署版

PDF扫描件智能识别转换工具 - 零成本部署方案

## 技术栈

- **部署平台**: Vercel（免费）
- **数据库**: Supabase PostgreSQL（免费500MB）
- **文件存储**: Supabase Storage（免费1GB）
- **OCR引擎**: 阿里云文档智能（按量付费）

## 快速开始

### 1. 创建Supabase项目

1. 访问 https://supabase.com
2. 注册账号，创建新项目
3. 获取 `SUPABASE_URL` 和 `SUPABASE_KEY`
4. 在 Storage 中创建一个 bucket 叫 `pdf-files`

### 2. 配置阿里云OCR

1. 登录阿里云控制台
2. 开通"文档智能"服务
3. 创建 AccessKey，获取 `AccessKey ID` 和 `AccessKey Secret`

### 3. 部署到Vercel

#### 方式一：一键部署（推荐）

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new)

1. 将代码推送到GitHub
2. 点击上方按钮，选择GitHub仓库
3. 配置环境变量（见下方）
4. 点击 Deploy

#### 方式二：Vercel CLI

```bash
# 安装Vercel CLI
npm i -g vercel

# 登录
vercel login

# 部署
vercel

# 配置环境变量
vercel env add SUPABASE_URL
vercel env add SUPABASE_KEY
vercel env add ALIBABA_CLOUD_ACCESS_KEY_ID
vercel env add ALIBABA_CLOUD_ACCESS_KEY_SECRET

# 重新部署
vercel --prod
```

### 4. 环境变量配置

在Vercel控制台或CLI中设置以下环境变量：

| 变量名 | 说明 | 来源 |
|--------|------|------|
| `SUPABASE_URL` | Supabase项目URL | Supabase控制台 |
| `SUPABASE_KEY` | Supabase匿名密钥 | Supabase控制台 |
| `ALIBABA_CLOUD_ACCESS_KEY_ID` | 阿里云AccessKey ID | 阿里云控制台 |
| `ALIBABA_CLOUD_ACCESS_KEY_SECRET` | 阿里云AccessKey Secret | 阿里云控制台 |

## 本地开发

```bash
# 进入项目目录
cd web-free

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 复制环境变量
cp .env.example .env
# 编辑 .env 填入你的配置

# 运行
python api/index.py
```

访问 http://localhost:5000

## 项目结构

```
web-free/
├── api/
│   └── index.py          # Flask主应用
├── templates/
│   └── index.html        # 前端页面
├── static/               # 静态资源
├── requirements.txt      # Python依赖
├── vercel.json          # Vercel配置
└── README.md            # 本文件
```

## 免费额度说明

| 服务 | 免费额度 | 估算用量 |
|------|----------|----------|
| Vercel | 无限流量 | 够用 |
| Supabase数据库 | 500MB | 约1万条记录 |
| Supabase存储 | 1GB | 约2000个PDF |
| 阿里云OCR | 无免费 | ¥0.0825/页 |

**注意**: 阿里云OCR是按量付费的，没有免费额度。但可以先不配置，部署后测试页面功能。

## 收费策略

- 用户价格: ¥0.25/页
- 阿里云成本: ¥0.0825/页
- 利润率: 约3倍

## 后续升级

当免费额度不够用时，可以：

1. **Supabase** → 阿里云RDS（¥50/月）
2. **Vercel** → 阿里云ECS（¥100/月）
3. **Supabase Storage** → 阿里云OSS（按量计费）

预计月费 ¥150-200 可以支撑初期业务。

## 注意事项

1. Vercel免费版函数执行时间限制10秒，大文件转换可能超时
2. 建议限制上传文件大小（已限制16MB）
3. 生产环境建议添加用户认证和支付系统

## 联系方式

有问题请联系管理员配置阿里云AccessKey。

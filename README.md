# Quant Analysis Project

这是一个量化分析项目，用于收集、分析和预测金融市场数据。

## 功能特点

- 使用 yfinance 爬取雅虎金融数据
- 使用 requests 爬取公司财务报表和华尔街新闻
- 使用 Celery 进行定时任务管理
- 使用 FastAPI 构建 API 服务
- 使用 OpenAI API 进行文本分析
- 使用 PostgreSQL 存储数据
- 使用 Streamlit 进行数据可视化

## 项目结构

```
app/
├── api/            # API 路由
├── core/           # 核心配置
├── crawlers/       # 爬虫模块
├── models/         # 数据模型
├── services/       # 业务逻辑
└── utils/          # 工具函数
config/             # 配置文件
logs/               # 日志文件
tests/              # 测试文件
```

## 安装

1. 创建虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置环境变量：
复制 `.env.example` 到 `.env` 并填写必要的配置信息。

## 运行

1. 启动 FastAPI 服务：
```bash
uvicorn app.main:app --reload
```

2. 启动 Celery worker：
```bash
celery -A app.core.celery_app worker --loglevel=info
```

3. 启动 Streamlit 应用：
```bash
streamlit run app/streamlit_app.py
```

## 开发

- 使用 `pytest` 运行测试
- 使用 `black` 进行代码格式化
- 使用 `flake8` 进行代码检查

## 许可证

MIT 


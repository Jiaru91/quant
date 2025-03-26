from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api import analysis, prediction
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="量化分析API",
    description="提供股票数据分析和预测服务",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(analysis.router, prefix="/api/analysis", tags=["分析"])
app.include_router(prediction.router, prefix="/api/prediction", tags=["预测"])

@app.get("/")
async def root():
    return {
        "message": "欢迎使用量化分析API",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    } 
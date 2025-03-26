from pydantic_settings import BaseSettings
from typing import List, Optional
from pydantic import Field

class Settings(BaseSettings):
    # 数据库配置
    db_host: str = Field(default="localhost", alias="DB_HOST")
    db_port: int = Field(default=5432, alias="DB_PORT")
    db_user: str = Field(default="jane", alias="DB_USER")
    db_password: str = Field(default="060321", alias="DB_PASSWORD")
    db_name: str = Field(default="quant_dev", alias="DB_NAME")
    
    # Redis配置
    redis_host: str = Field(default="localhost", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_db: int = Field(default=0, alias="REDIS_DB")
    
    # API配置
    api_v1_str: str = Field(default="/api/v1", alias="API_V1_STR")
    project_name: str = Field(default="Quant Analysis API", alias="PROJECT_NAME")
    
    # 安全配置
    secret_key: str = Field(
        default="09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7",
        alias="SECRET_KEY"
    )
    access_token_expire_minutes: int = Field(default=11520, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # 外部API配置
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    alpha_vantage_api_key: str = Field(default="PWPMF4TAGXXFV1RO", alias="ALPHA_VANTAGE_API_KEY")
    deepseek_api_key: str = Field(default="sk-0a1fe4a3d5ea4335bb3d8368561581d8", alias="DEEPSEEK_API_KEY")
    
    # 模型配置
    openai_model: str = Field(default="gpt-3.5-turbo", alias="OPENAI_MODEL")
    deepseek_model: str = Field(default="deepseek-reasoner", alias="DEEPSEEK_MODEL")
    
    # 分析配置
    min_confidence_score: float = Field(default=0.7, alias="MIN_CONFIDENCE_SCORE")
    max_noise_threshold: float = Field(default=0.3, alias="MAX_NOISE_THRESHOLD")
    
    # 数据分析配置
    financial_metrics: List[str] = Field(
        default=[
            "revenue",
            "net_income",
            "eps",
            "pe_ratio",
            "debt_to_equity",
            "current_ratio",
            "quick_ratio",
            "operating_margin",
            "net_margin",
            "return_on_equity"
        ],
        alias="FINANCIAL_METRICS"
    )
    
    # 环境配置
    environment: str = Field(default="development", alias="ENVIRONMENT")
    
    # 日志配置
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_file: str = Field(default="logs/dev.log", alias="LOG_FILE")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        populate_by_name = True

settings = Settings() 
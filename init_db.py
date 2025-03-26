from sqlalchemy import create_engine
from app.models.crawler import Base
from app.core.config import settings

def init_database():
    """初始化数据库"""
    print("开始初始化数据库...")
    
    # 创建数据库引擎
    SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    try:
        # 创建所有表
        Base.metadata.create_all(engine)
        print("数据库表创建成功！")
    except Exception as e:
        print(f"创建数据库表时出错: {str(e)}")

if __name__ == "__main__":
    init_database() 
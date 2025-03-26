import hashlib
import logging
from datetime import datetime
from typing import Optional, Dict, Any
import requests
from sqlalchemy.orm import Session
from app.core.database import Base

logger = logging.getLogger(__name__)

class BaseCrawler:
    def __init__(self, db: Session):
        self.db = db
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def generate_hash(self, content: str) -> str:
        """生成内容的MD5哈希值"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    def is_duplicate(self, content_hash: str, model: Base) -> bool:
        """检查内容是否重复"""
        return self.db.query(model).filter(model.content_hash == content_hash).first() is not None

    def save_to_db(self, model: Base) -> bool:
        """保存数据到数据库"""
        try:
            self.db.add(model)
            self.db.commit()
            return True
        except Exception as e:
            logger.error(f"Error saving to database: {str(e)}")
            self.db.rollback()
            return False

    def get_page(self, url: str, params: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """获取页面内容"""
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None 
from typing import Any, Dict, Optional
from pydantic import BaseSettings, PostgresDsn, validator
import secrets


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # MYSQL 数据库
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_HOST: str
    MYSQL_PORT: str
    MYSQL_DB: str
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return f"mysql+pymysql://{values.get('MYSQL_USER')}:{values.get('MYSQL_PASSWORD')}@{values.get('MYSQL_HOST')}:{values.get('MYSQL_PORT')}/{values.get('MYSQL_DB')}"

    # 向量数据库配置
    VECTOR_DB_TYPE: str = "faiss"  # 可选: faiss, pinecone, milvus, pgvector
    VECTOR_DB_PATH: Optional[str] = "./vectorstore"  # FAISS本地存储路径
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENVIRONMENT: Optional[str] = None

    # 嵌入模型配置
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"  # 默认嵌入模型
    EMBEDDING_DIMENSION: int = 384  # 适用于all-MiniLM-L6-v2

    # 聊天模型配置
    CHAT_MODEL_TYPE: str = "openai"  # openai 或 huggingface
    OPENAI_API_KEY: Optional[str] = None
    HF_MODEL_NAME: Optional[str] = "meta-llama/Llama-2-7b-chat-hf"
    HF_API_KEY: Optional[str] = None

    # MinerU PDF配置
    MINERU_TEMP_DIR: str = "./tmp"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
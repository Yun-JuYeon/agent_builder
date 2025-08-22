from langchain_postgres import PGVector
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

from app.config import settings
from app.core.embedding import GeminiEmbeddings

def get_vectorstore(collection_name: str) -> PGVector:
    connection_string =(
                    f"postgresql+psycopg://{settings.PG_USER}:{settings.PG_PASSWORD}@"
                    f"{settings.PG_HOST}:{settings.PG_PORT}/{settings.PG_DB}"
                )
 
    try:    
        # https://docs.sqlalchemy.org/en/20/errors.html#error-e3q8
        engine = create_engine(
            connection_string,
            pool_size=10,                    # 기본적으로 유지할 연결의 수를 설정합니다.
            max_overflow=20,                 # 기본 풀 크기를 초과하여 추가로 생성할 수 있는 연결의 수를 설정합니다.
            pool_timeout=30,                 # 연결 풀이 고갈되었을 때 새 연결을 얻기 위해 대기할 최대 시간을 설정합니다.
            pool_pre_ping=True,              # 연결이 유효한지 미리 확인하여 유효하지 않은 경우 새로운 연결을 생성합니다.
            pool_recycle=1800,               # 일정 시간(30분) 동안 사용되지 않은 연결을 자동으로 재활용합니다.
            pool_reset_on_return='rollback'  # 연결이 반환될 때 트랜잭션을 롤백하여 일관된 상태를 유지합니다.
        )
        embeddings = GeminiEmbeddings(settings.GOOGLE_API_KEY)

        vectorstore =  PGVector(
                        connection=engine,
                        embeddings=embeddings,
                        collection_name=collection_name
                    )
    except OperationalError as e:
        print(f"Database connection failed: {e}")
        raise
    return vectorstore
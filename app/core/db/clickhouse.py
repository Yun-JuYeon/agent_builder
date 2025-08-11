from sqlalchemy import create_engine, MetaData, Table, select
from app.config import settings

clickhouse_host = settings.CL_HOST 
clickhouse_db = settings.CL_DB
clickhouse_pw = settings.CL_PASSWORD
clickhouse_port = settings.CL_PORT
clickhouse_user = settings.CL_USER

"""
ClickHouse 드라이버는 원래 동기 기반이 주류.
(asyncio 지원은 아직 부가 기능 수준이라, 안정성과 커뮤니티 지원은 동기 기반이 더 강함.)

배치성 ClickHouse 작업이라면 동기 처리로 충분하고, 안정성도 더 높을 것으로 판단됨.
"""

DATABASE_URL = (
    f"clickhouse+http://{clickhouse_user}:{clickhouse_pw}@{clickhouse_host}:{clickhouse_port}/{clickhouse_db}"
)

engine = create_engine(DATABASE_URL)
metadata = MetaData()
application_logs = Table("application_logs", metadata, autoload_with=engine)


def select_table_data():
    stmt = select(application_logs.c.uid, application_logs.c.appid, application_logs.c.message)

    with engine.connect() as conn:
        selected_data = conn.execute(stmt).all()
        print(selected_data)

        return selected_data
    

if __name__ == "__main__":
    select_table_data()
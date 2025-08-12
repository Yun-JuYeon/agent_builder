from google.adk.sessions import DatabaseSessionService
from google.adk.sessions.database_session_service import StorageEvent
from google.adk.sessions.database_session_service import StorageSession
from google.adk.events import Event
from app.config import settings

pg_username = settings.PG_USER
pg_password = settings.PG_PASSWORD
pg_port = settings.PG_PORT
pg_db = settings.PG_DB
pg_host = settings.PG_HOST

from urllib.parse import quote_plus
pg_password_quoted = quote_plus(pg_password)
DATABASE_URL = f"postgresql+psycopg2://{pg_username}:{pg_password_quoted}@{pg_host}:{pg_port}/{pg_db}"

# DatabaseSessionService 인스턴스 생성 (동기)
session_service = DatabaseSessionService(DATABASE_URL)

def get_session_ids(app_name: str, user_id: str):
    """
    DatabaseSessionService를 사용해 해당 app/user의 세션 id 목록을 조회
    """
    with session_service.database_session_factory() as sql_session:
        results = (
            sql_session.query(StorageSession.id)
            .filter(StorageSession.app_name == app_name)
            .filter(StorageSession.user_id == user_id)
            .all()
        )
        session_ids = [row[0] for row in results]
        print(f"Session IDs for user '{user_id}' and app '{app_name}': {session_ids}")
        return session_ids

def get_events_for_session(app_name: str, user_id: str, session_id: str) -> list[Event]:
    """
    DatabaseSessionService를 사용해 특정 세션의 이벤트 목록을 조회
    """
    with session_service.database_session_factory() as sql_session:
        results = (
            sql_session.query(StorageEvent)
            .filter(StorageEvent.app_name == app_name)
            .filter(StorageEvent.user_id == user_id)
            .filter(StorageEvent.session_id == session_id)
            .order_by(StorageEvent.timestamp)
            .all()
        )
        events: list[Event] = []
        for event in results:
            # actions 필드가 dict가 아니면 dict로 변환
            if hasattr(event, "actions") and not isinstance(event.actions, dict):
                try:
                    event.actions = event.actions.dict()
                except Exception:
                    event.actions = {}
            events.append(event.to_event())
            print(events[-1])
        return events
    
    
if __name__ == "__main__":
    # 예시 실행
    app_name = "jyyun_weather_agent"
    user_id = "jyyun"
    session_ids = get_session_ids(app_name, user_id)
    if session_ids:
        get_events_for_session(app_name, user_id, session_ids[0])
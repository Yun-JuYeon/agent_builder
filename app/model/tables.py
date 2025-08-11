from sqlalchemy import (
    TIMESTAMP,
    Column,
    Integer,
    MetaData,
    String,
    Table,
)
from sqlalchemy.dialects.postgresql import JSONB


metadata = MetaData()  # 테이블 정의들을 담아놓을 컨테이너

# 테이블 정의
didim_code = Table(
    "didim_code",
    metadata,
    Column("code_group_id", String(20), nullable=False, comment="코드그룹ID"),
    Column("code_group_name", String(100), nullable=False, comment="코드그룹이름"),
    Column("code", String(30), nullable=False, comment="코드값"),
    Column("code_name", String(100), nullable=True, comment="코드이름"),
    Column("code_sequence", Integer, nullable=True, comment="순서"),
    Column("use_yn", String(1), nullable=False, comment="사용여부"),
    Column("created_at", TIMESTAMP, nullable=False, comment="최초등록일시"),
    Column(
        "created_by_dept_code", String(20), nullable=False, comment="최초등록부서코드"
    ),
    Column(
        "created_by_employee_number",
        String(20),
        nullable=False,
        comment="최초등록직원번호",
    ),
    Column("last_updated_at", TIMESTAMP, nullable=True, comment="최종수정일시"),
    Column(
        "updated_by_dept_code", String(20), nullable=True, comment="최종수정부서코드"
    ),
    Column(
        "updated_by_employee_number",
        String(20),
        nullable=True,
        comment="최종수정직원번호",
    ),
)

app_sessions = Table(
    "sessions",
    metadata,
    Column("app_name", String(20), nullable=False, comment="에이전트이름"),
    Column("user_id", String(100), nullable=False, comment="사용자ID"),
    Column("id", String(128), nullable=False, comment="세션ID"),
    Column("state", JSONB, nullable=False, comment="세션 상태"),
    Column("create_time", TIMESTAMP, nullable=False, comment="생성시간"),
    Column("update_time", TIMESTAMP, nullable=False, comment="업데이트 시간"),
)

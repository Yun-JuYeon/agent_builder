## FastAPI 기반 구조 설정 시 참고
1. 가상환경 설정
python -m venv .venv
.venv\Scripts\activate (가상환경 활성화)

2. FastAPI 및 Uvicorn 설치
pip install fastapi uvicorn

3. main.py 설정
FastAPI app 설정


## 프로젝트 실행 방법
1. 서버 실행
uvicorn main:app --reload

2. prometheus 서버 실행(아래 경로는 로컬 프로메테우스 경로)
../../prometheus-3.5.0.windows-amd64/prometheus --config.file=./prometheus.yml

### 서버 정보 
- FastAPI 서버는 localhost:8000
- prometheus 서버는 localhost:9090
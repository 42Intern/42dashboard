import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 환경 변수 설정
UID = os.getenv("UID")
SECRET = os.getenv("SECRET")
REDIRECT_URL = os.getenv("REDIRECT_URL", "http://localhost:8000/auth/callback")  # 기본값 설정

API_BASE_URL = "https://api.intra.42.fr"
TOKEN_URL = "https://api.intra.42.fr/oauth/token"
AUTH_URL = f"https://api.intra.42.fr/oauth/authorize?client_id={UID}&redirect_uri={REDIRECT_URL}&response_type=code"

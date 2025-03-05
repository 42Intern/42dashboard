#### 프로젝트 구조
source venv/bin/activate
```
/dash_app
│── app.py                # Dash 앱 실행 (메인 파일)
│── layout.py             # Dash 레이아웃 정의
│── callbacks.py          # Dash 콜백 함수 정의
│── api_utils.py          # API 요청 관련 유틸 함수
│── config.py             # API 설정값 (API_BASE_URL, TOKEN_URL, UID, SECRET)
│── api_categories.py     # API 리스트
```

### python 가상환경
가상환경 생성
```bash
python3 -m venv venv
```
  
가상환경 실행
```bash
source venv/bin/activate
```

env파일에 UID, SECRET 넣고 .env로 변환하기

### curl로 post 보내는 법
1. access token 얻기
```bash
curl -X POST "https://api.intra.42.fr/oauth/token" \
-d "grant_type=client_credentials" \
-d "client_id=[UID]" \
-d "client_secret=[SECRET]"
```

2. 이후 원하는 api 테스트
```bash
curl  -H "Authorization: Bearer [access_token]" "https://api.intra.42.fr/v2/cursus/81"
``

import json
import requests
import pandas as pd
from config import API_BASE_URL, TOKEN_URL, UID, SECRET
from dash import dash_table, html

# 1. 액세스 토큰을 가져오는 함수
def get_access_token():
    data = {"grant_type": "client_credentials"}
    response = requests.post(TOKEN_URL, data=data, auth=(UID, SECRET))
    if response.status_code == 200:
        return response.json().get("access_token")
    print(f"🔑 토큰 요청 실패: {response.status_code}, {response.text}")
    return None

# 2. 전체 페이지 데이터 가져오기
def fetch_all_pages(endpoint, params=None):
    """페이지네이션을 처리하여 API의 모든 데이터를 가져온다."""
    access_token = get_access_token()
    if not access_token:
        return "❌ 토큰을 가져오지 못했습니다."
    print(f"api 요청중입니다")
    headers = {"Authorization": f"Bearer {access_token}"}
    full_url = f"{API_BASE_URL}{endpoint}"
    all_data = []
    page = 1  # 첫 페이지부터 시작

    while True:
        # 요청 URL 구성
        page_params = params or {}
        page_params["page"] = page  # 페이지 번호 추가
        response = requests.get(full_url, headers=headers, params=page_params)

        if response.status_code != 200:
            print(f"❌ 응답 실패 (코드 {response.status_code}): {response.text}")
            break  # 오류 발생 시 중단

        data = response.json()
        if not data:
            break  # 더 이상 데이터가 없으면 종료

        all_data.extend(data)  # 데이터를 리스트에 추가
        page += 1  # 다음 페이지 요청

    print(f"api 요청완료")
    return generate_table(all_data)

# 3. DataTable 생성
def generate_table(data):
    """API 데이터를 Dash DataTable로 변환"""
    processed_data = flatten_data(data)

    if not processed_data:
        return "✅ 응답 성공: 데이터가 없습니다."

    df = pd.DataFrame(processed_data)

    return dash_table.DataTable(
        columns=[{"name": col, "id": col} for col in df.columns],
        data=df.to_dict("records"),
        style_table={"overflowX": "auto"},
        style_header={"fontWeight": "bold"},
        page_size=10
    )

# 4. 데이터 가공 함수
def flatten_data(data):
    """API 응답 데이터를 DataTable에 넣을 수 있도록 변환"""
    if isinstance(data, list):
        flattened_data = []
        for item in data:
            flattened_item = {key: format_value(value, key) for key, value in item.items()}
            flattened_data.append(flattened_item)
        return flattened_data

    elif isinstance(data, dict):
        return [flatten_data([data])[0]]

    return []

def format_value(value, key):
    """값 변환 함수"""
    if isinstance(value, list):
        return ", ".join(map(str, value))
    elif isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False)
    elif isinstance(value, str) and key == "image" and value.startswith("http"):
        return html.Img(src=value, style={"height": "50px"})
    return value

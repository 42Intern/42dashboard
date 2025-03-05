import json
import requests
import pandas as pd
from config import API_BASE_URL, TOKEN_URL, UID, SECRET
from dash import dash_table, html

# 1. 액세스 토큰을 가져오는 함수
def get_access_token():
    response = requests.post(TOKEN_URL, data={
        "grant_type": "client_credentials",
        "client_id": UID,
        "client_secret": SECRET
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    print(f"❌ 액세스 토큰을 가져오지 못했습니다: {response.status_code}, {response.text}")
    return None

# 2. API 요청 및 데이터 변환
def fetch_api_data(endpoint):
    access_token = get_access_token()
    if not access_token:
        return "❌ 토큰을 가져오지 못했습니다."
    
    headers = {"Authorization": f"Bearer {access_token}"}
    full_url = f"{API_BASE_URL}{endpoint}"
    print(f"🔍 요청 URL: {full_url}")  # 디버깅용 로그

    response = requests.get(full_url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return generate_table(data)
    else:
        return f"❌ 응답 실패 (코드 {response.status_code}): {response.text}"

def remove_outer_quotes(value):
    """문자열이 큰따옴표("")로 감싸져 있으면 바깥쪽 따옴표 제거"""
    if isinstance(value, str) and value.startswith('"') and value.endswith('"'):
        return value[1:-1]  # 앞뒤 따옴표 제거
    return value

def format_value(value, key):
    """DataTable에 넣기 전에 값 변환"""
    if isinstance(value, list):
        # ✅ 리스트 데이터를 쉼표(,)로 구분된 문자열로 변환
        return ", ".join(map(str, value))

    elif isinstance(value, dict):
        # ✅ 딕셔너리를 JSON 문자열로 변환
        return json.dumps(value, ensure_ascii=False)

    elif isinstance(value, str):
        # ✅ 이미지 URL인 경우 HTML <img> 태그로 변환
        if key == "image" and value.startswith("http"):
            return html.Img(src=value, style={"height": "50px"})  # 작은 이미지로 표시
        return remove_outer_quotes(value)  # 바깥 따옴표 제거

    return value  # 그대로 반환

def flatten_data(data):
    """API 응답 데이터를 DataTable에 넣을 수 있도록 변환"""
    if isinstance(data, list):
        flattened_data = []
        for item in data:
            flattened_item = {}
            for key, value in item.items():
                flattened_item[key] = format_value(value, key)  # ✅ 값 변환 함수 적용
            flattened_data.append(flattened_item)
        return flattened_data

    elif isinstance(data, dict):
        return [flatten_data([data])[0]]

    return []

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

import json
import requests
import pandas as pd
from config import API_BASE_URL, TOKEN_URL, UID, SECRET
from dash import dash_table, html

# 1. 액세스 토큰 가져오기
def get_access_token():
    data = {"grant_type": "client_credentials"}
    response = requests.post(TOKEN_URL, data=data, auth=(UID, SECRET))
    if response.status_code == 200:
        return response.json().get("access_token")
    print(f"🔑 토큰 요청 실패: {response.status_code}, {response.text}")
    return None


# 2. 전체 페이지(또는 지정 페이지 수)의 '원본 데이터' 가져오기
def fetch_pages(endpoint, params=None, max_pages=None):
    """
    (변경 없음) 페이지네이션을 처리하여 API의 모든 데이터를 '원본 형태'로 가져옴
    - dict 한 개, list 여러 개 등 API 응답 형태에 따라 달라질 수 있음
    """
    access_token = get_access_token()
    if not access_token:
        return "❌ 토큰을 가져오지 못했습니다."

    headers = {"Authorization": f"Bearer {access_token}"}
    full_url = f"{API_BASE_URL}{endpoint}"
    all_data = []
    page = 1
    
    print(f"🚀 페이지 API 요청 시작: {full_url}")

    while True:
        if max_pages and page > max_pages:
            break
        
        current_params = dict(params or {})
        current_params["page"] = page  # 페이지 번호
        response = requests.get(full_url, headers=headers, params=current_params)

        if response.status_code != 200:
            err_msg = f"❌ 응답 실패 (코드 {response.status_code}): {response.text}"
            print(err_msg)
            return err_msg

        data = response.json()
        # data가 list일 수도, dict일 수도 있음
        if not data:
            break
        
        # data가 list라면 -> extend
        if isinstance(data, list):
            all_data.extend(data)
        else:
            # dict 등 단일 객체인 경우 -> list에 추가
            all_data.append(data)
        page += 1

    return all_data  # 최종적으로 list[dict or 기타] 형태가 됨


# 3. 유연한 테이블 생성 함수
def universal_generate_table(data):
    """
    데이터를 받으면 list[dict] 형태로 정규화 후,
    Pandas DataFrame으로 만든 뒤 전치(transpose)하여
    "각 필드가 행, 각 아이템이 열" 형태로 Dash DataTable을 생성
    """
    import pandas as pd
    from dash import dash_table, html

    # 1) 에러 문자나 빈 값 처리
    if isinstance(data, str):
        return data
    if not data:
        return "✅ 데이터가 없습니다."

    # 2) dict 단일 객체면 -> [dict]
    if isinstance(data, dict):
        data = [data]

    # 3) 리스트가 아니면 -> [{"value": str(data)}]
    if not isinstance(data, list):
        data = [{"value": str(data)}]

    # 4) 리스트 내부 아이템 평탄화
    flattened_list = []
    for item in data:
        if isinstance(item, dict):
            flattened_item = flatten_dict(item)  # 재귀 평탄화
            flattened_list.append(flattened_item)
        else:
            flattened_list.append({"value": str(item)})

    if not flattened_list:
        return "✅ 응답 성공: 데이터가 없습니다."

    # 5) DataFrame 변환
    df = pd.DataFrame(flattened_list)
    if df.empty:
        return "✅ 응답 성공: 데이터가 없습니다."

    # 6) 전치(Transpose)
    df_t = df.T.reset_index().rename(columns={"index": "Field"})

    # 7) Dash DataTable 생성
    return dash_table.DataTable(
        columns=[{"name": str(col), "id": str(col)} for col in df_t.columns],
        data=df_t.to_dict("records"),
        style_table={"overflowX": "auto"},
        style_header={"fontWeight": "bold"},
        style_cell={
        "textAlign": "left",  
        "maxWidth": "300px",   # 셀의 최대 너비를 지정 (원하는 값으로 조정)
        "overflow": "auto",    # 내용이 초과되면 스크롤바 표시
        "whiteSpace": "nowrap" # 텍스트 줄바꿈 없이 한 줄로 표시
        },
        style_data_conditional=[
            {
                "if": {"column_id": "Field"},
                "backgroundColor": "#f2f2f2",
                "fontWeight": "bold",
            },
        ],
        page_action="none",
    )


def flatten_dict(d, parent_key="", sep="."):
    """
    재귀적으로 nested dict를 평탄화.
    예: {"user":{"id":123,"image":"http://..."}} 
        -> {"user.id": 123, "user.image": "http://..."}
    """
    items = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k

        if isinstance(v, dict):
            # dict -> 재귀 평탄화
            sub = flatten_dict(v, parent_key=new_key, sep=sep)
            items.update(sub)
        elif isinstance(v, list):
            # list -> JSON 문자열화 (혹은 원하는 방식)
            items[new_key] = json.dumps(v, ensure_ascii=False)
        else:
            # 일반 값
            if new_key.endswith("image") and isinstance(v, str) and v.startswith("http"):
                # 이미지 URL 처리
                items[new_key] = html.Img(src=v, style={"height": "50px"})
            else:
                items[new_key] = v
    return items
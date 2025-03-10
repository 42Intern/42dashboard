import requests
import pandas as pd
from datetime import datetime
import calendar
from config import API_BASE_URL, TOKEN_URL, UID, SECRET
from api_utils import get_access_token

# API 요청 URL 생성 (Google Apps Script의 makeQueryString 대체)
def make_query_string(params, base_url):
    query_string = "&".join([f"{key}={value}" for key, value in params.items()])
    return f"{base_url}?{query_string}"

# UTC 시간을 한국 시간(KST)으로 변환
def convert_to_kst(utc_time_str):
    utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    kst_time = utc_time.strftime("%Y-%m-%d %H:%M:%S")
    return kst_time

# 주어진 년-월(ex: "2024-08")을 기반으로 시작일과 마지막 날 반환
def get_start_and_end_dates(year_month):
    year, month = map(int, year_month.split("-"))
    start_date = f"{year}-{month:02d}-01"
    last_day = calendar.monthrange(year, month)[1]
    end_date = f"{year}-{month:02d}-{last_day}"
    return start_date, end_date


# 블랙홀에 빠진 유저 목록 조회 및 CSV 저장
def get_blackholed_users(year_month):
    start_date, end_date = get_start_and_end_dates(year_month)


    url = "https://api.intra.42.fr/v2/cursus_users"
    params = {
        "filter[campus_id]": "29",
        "page[size]": "30",
        "range[blackholed_at]": f"{start_date},{end_date}"
    }

    access_token = get_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    try:
        # API 요청
        response = requests.get(make_query_string(params, url), headers=headers)
        response.raise_for_status()  # 오류 발생 시 예외 발생
        json_data = response.json()

        # JSON 데이터 파싱
        data = [
            [item["id"], item["user"]["login"], convert_to_kst(item["blackholed_at"])]
            for item in json_data
        ]

        # pandas DataFrame 생성
        df = pd.DataFrame(data, columns=["ID", "Login", "Blackholed_At"])

        # CSV 파일 저장
        csv_file = "blackholed_users.csv"
        df.to_csv(csv_file, index=False, encoding="utf-8")

        print(f"데이터가 {csv_file} 파일로 저장되었습니다.")
    except requests.RequestException as e:
        print(f"API 요청 중 오류 발생: {e}")


# 실행
if __name__ == "__main__":
    user_input = input("조회할 년-월을 입력하세요 (예: 2024-08): ")
    get_blackholed_users(user_input)
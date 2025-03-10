import sys
import os
import requests
import pandas as pd
from datetime import datetime
import calendar

# 현재 파일의 디렉토리 기준으로 상위 폴더 경로 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 상위 디렉토리에 있는 모듈 import
from config import API_BASE_URL, TOKEN_URL, UID, SECRET
from api_utils import get_access_token


def make_query_string(params, base_url):
    query_string = "&".join([f"{key}={value}" for key, value in params.items()])
    return f"{base_url}?{query_string}"

def convert_to_kst(utc_time_str):
    utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    kst_time = utc_time.strftime("%Y-%m-%d %H:%M:%S")
    return kst_time

def get_start_and_end_dates(year_month):
    if year_month.lower() == "all":
        start_date = "2000-01-01"  # 가능한 가장 과거 날짜 (API가 지원하는 범위 내에서 조정 필요)
        end_date = datetime.today().strftime("%Y-%m-%d")  # 오늘 날짜
    else:
        year, month = map(int, year_month.split("-"))
        start_date = f"{year}-{month:02d}-01"
        last_day = calendar.monthrange(year, month)[1]
        end_date = f"{year}-{month:02d}-{last_day}"
    return start_date, end_date

def get_blackholed_users(year_month):
    start_date, end_date = get_start_and_end_dates(year_month)

    url = "https://api.intra.42.fr/v2/cursus_users"
    params = {
        "filter[campus_id]": "29",
        "page[size]": "100",  # 전체 데이터를 가져오기 위해 페이지 크기 증가
        "range[blackholed_at]": f"{start_date},{end_date}"
    }

    access_token = get_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    all_data = []
    page = 1

    try:
        while True:
            response = requests.get(make_query_string({**params, "page[number]": page}, url), headers=headers)
            response.raise_for_status()
            json_data = response.json()

            if not json_data:
                break  # 더 이상 데이터가 없으면 종료

            all_data.extend([
                [item["id"], item["user"]["login"], convert_to_kst(item["blackholed_at"])]
                for item in json_data
            ])
            page += 1  # 다음 페이지 요청

        if all_data:
            df = pd.DataFrame(all_data, columns=["ID", "Login", "Blackholed_At"])
            csv_file = "blackholed_users.csv"
            df.to_csv(csv_file, index=False, encoding="utf-8")
            print(f"데이터가 {csv_file} 파일로 저장되었습니다.")
        else:
            print("조회된 데이터가 없습니다.")

    except requests.RequestException as e:
        print(f"API 요청 중 오류 발생: {e}")

if __name__ == "__main__":
    user_input = input('조회할 년-월을 입력하세요 (예: "2024-08" 또는 "all" 입력 시 전체 조회): ')
    get_blackholed_users(user_input)

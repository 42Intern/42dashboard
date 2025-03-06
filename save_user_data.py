import requests
import pandas as pd
from config import API_BASE_URL, TOKEN_URL, UID, SECRET
from api_utils import get_access_token
import urllib.parse  # URL 인코딩용


def flatten_json(json_data, prefix=""):
    """JSON을 평탄화하는 함수"""
    flat_dict = {}

    def recursive_flatten(data, key_prefix=""):
        if isinstance(data, dict):
            for key, value in data.items():
                recursive_flatten(value, key_prefix + key + "_")
        elif isinstance(data, list):
            for index, item in enumerate(data):
                recursive_flatten(item, key_prefix + str(index) + "_")
        else:
            flat_dict[key_prefix[:-1]] = data  # 마지막 '_' 제거

    recursive_flatten(json_data, prefix)
    return flat_dict


def fetch_and_save_user_data(user_id):
    """API에서 유저 정보를 가져와 CSV로 저장"""
    access_token = get_access_token()
    print(f"🔑 액세스 토큰: {access_token}")

    if not access_token:
        print("❌ 유효한 액세스 토큰이 없습니다.")
        return

    headers = {
        'Authorization': f'Bearer {access_token}',
        'User-Agent': '42DashboardClient'
    }

    # ✅ 올바른 API URL 적용 (filter[login]=user_id)
    query_params = urllib.parse.urlencode({"filter[login]": user_id})
    api_url = f"{API_BASE_URL}/users?{query_params}"

    print(f"🔗 요청 URL: {api_url}")

    response = requests.get(api_url, headers=headers)
    print(f"📡 응답 상태 코드: {response.status_code}")

    if response.status_code == 200:
        user_data = response.json()
        print(f"📄 응답 데이터: {user_data}")

        if not user_data:
            print("⚠️ 사용자 데이터를 찾을 수 없습니다.")
            return

        # JSON을 평탄화하여 CSV로 저장
        flat_user_data = flatten_json(user_data[0])  # 리스트에서 첫 번째 유저 데이터 선택
        df = pd.DataFrame([flat_user_data])
        df.to_csv("user_data.csv", index=False, encoding="utf-8")
        print("✅ CSV 저장 완료!")
    else:
        print(f"❌ 유저 정보를 가져올 수 없습니다: {response.status_code}, {response.text}")


if __name__ == "__main__":
    user_id = input("Enter User ID: ")
    fetch_and_save_user_data(user_id)

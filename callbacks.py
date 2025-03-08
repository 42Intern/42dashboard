from dash import Input, Output, State, ctx, html, dcc, ALL
import dash.exceptions
from api_categories import API_CATEGORIES
import re
from api_utils import get_access_token, generate_table
import requests
from config import API_BASE_URL

def register_callbacks(app):
    #
    # 콜백 A) 카테고리 선택 시 - 버튼 목록만 업데이트
    #
    @app.callback(
        Output("api-buttons-container", "children"),
        Input("category-selector", "value")
    )
    def update_api_buttons(selected_category):
        """
        1) 카테고리 선택 시
           -> API 목록(버튼들)만 보여주기 (API 요청 금지)
        """
        if not selected_category:
            return ""
        api_list = API_CATEGORIES.get(selected_category, [])
        buttons = [
            html.Button(
                api["label"],
                id={"type": "api-button", "index": api["value"]},
                n_clicks=0,
                style={"margin": "5px"}
            )
            for api in api_list
        ]
        return html.Div(buttons)

    #
    # 콜백 B) 버튼 클릭 or "API 요청 보내기" 버튼 클릭 시
    #
    @app.callback(
        [
            Output("dynamic-inputs", "children"),  # 인자 입력 필드 표시
            Output("selected-endpoint", "data"),   # 선택한 API 엔드포인트 저장
            Output("send-request", "style"),       # "API 요청 보내기" 버튼 스타일
            Output("api-response-table", "children")  # 결과 테이블
        ],
        [
            Input({"type": "api-button", "index": ALL}, "n_clicks"),
            Input("send-request", "n_clicks")
        ],
        [
            State({"type": "api-button", "index": ALL}, "id"),
            State({"type": "input", "index": ALL}, "id"),
            State({"type": "input", "index": ALL}, "value"),
            State("selected-endpoint", "data")
        ],
        prevent_initial_call=True
    )
    def handle_api_clicks(
        api_button_n_clicks, 
        send_request_n_clicks,
        api_button_ids,
        dynamic_input_ids, 
        dynamic_input_values, 
        stored_endpoint
    ):
        """
        2) API 버튼 클릭 시
           - 인자 없는 경우 → 즉시 API 요청
           - 인자 있는 경우 → 입력 필드 + "API 요청 보내기" 버튼 표시
         3) "API 요청 보내기" 버튼 클릭 시
           - 입력 받은 인자를 반영하여 API 요청
        """

        # 0) 사용자가 아무 버튼도 안 눌렀으면, 업데이트 없음
        total_clicks_buttons = sum(api_button_n_clicks) if api_button_n_clicks else 0
        if total_clicks_buttons == 0 and (not send_request_n_clicks or send_request_n_clicks == 0):
            raise dash.exceptions.PreventUpdate

        # 어떤 입력이 트리거 되었는지 확인
        triggered_id = ctx.triggered_id

        #
        # A. "API 버튼" 클릭 감지
        #
        if isinstance(triggered_id, dict) and triggered_id.get("type") == "api-button":
            selected_endpoint = triggered_id["index"]
            param_matches = re.findall(r":(\w+)", selected_endpoint)
            
            # A-1) 인자가 있으면 -> 입력 필드 및 "API 요청 보내기" 버튼 표시
            if param_matches:
                inputs = []
                for param in param_matches:
                    inputs.append(html.Label(f"{param} 입력:"))
                    inputs.append(
                        dcc.Input(
                            id={"type": "input", "index": param},
                            type="text",
                            placeholder=f"{param} 값을 입력하세요"
                        )
                    )
                # 인자 입력필드 / 엔드포인트 저장 / 버튼 보이기 / 테이블은 ""
                return html.Div(inputs), selected_endpoint, {"display": "block"}, ""

            # A-2) 인자가 없으면 -> 즉시 API 요청
            access_token = get_access_token()
            if not access_token:
                return "", selected_endpoint, {"display": "none"}, "❌ 토큰을 가져오지 못했습니다."
            
            full_url = f"{API_BASE_URL}{selected_endpoint}"
            print(f"URL: {full_url}")  # 디버깅
            response = requests.get(full_url, headers={"Authorization": f"Bearer {access_token}"})
            # ✅ 상태 코드 확인
            if response.status_code == 200:
                data = response.json()
                # ✅ 데이터가 비었는지 확인
                if not data:
                    table = "✅ 데이터가 없습니다."
                else:
                    table = generate_table(data)
            else:
                table = f"❌ 응답 실패 (코드 {response.status_code}): {response.text}"
            
            # 입력필드 없앰 / 엔드포인트 저장 / "API 요청 보내기" 숨김 / 테이블 표시
            return "", selected_endpoint, {"display": "none"}, table

        #
        # B. "API 요청 보내기" 버튼 클릭 감지
        #
        elif triggered_id == "send-request":
            if not stored_endpoint:
                # 엔드포인트가 저장되지 않은 경우
                return "", "", {"display": "none"}, "❌ API를 선택하세요."

            # 인자가 있다면 입력값을 치환
            selected_endpoint = stored_endpoint
            if dynamic_input_ids and dynamic_input_values:
                for item, val in zip(dynamic_input_ids, dynamic_input_values):
                    selected_endpoint = selected_endpoint.replace(f":{item['index']}", str(val))

            access_token = get_access_token()
            if not access_token:
                return dash.no_update, stored_endpoint, {"display": "block"}, "❌ 토큰을 가져오지 못했습니다."
            
            full_url = f"{API_BASE_URL}{selected_endpoint}"
            print(f"URL: {full_url}")  # 디버깅
            response = requests.get(full_url, headers={"Authorization": f"Bearer {access_token}"})
            # ✅ 상태 코드 확인
            if response.status_code == 200:
                data = response.json()
                # ✅ 데이터가 비었는지 확인
                if not data:
                    table = "✅ 데이터가 없습니다."
                else:
                    table = generate_table(data)
            else:
                table = f"❌ 응답 실패 (코드 {response.status_code}): {response.text}"
            
            # 기존 입력필드 유지 / 엔드포인트는 그대로 / 버튼 보이기 / 테이블 업데이트
            return dash.no_update, stored_endpoint, {"display": "block"}, table

        else:
            raise dash.exceptions.PreventUpdate

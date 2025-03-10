from dash import Input, Output, State, ctx, html, dcc, ALL
import dash.exceptions
import re
import pandas as pd
import io

from api_categories import API_CATEGORIES
from api_utils import fetch_pages, universal_generate_table  # (예시)
from config import API_BASE_URL


def register_callbacks(app):
    #
    # 카테고리 선택 → 버튼 목록
    #
    @app.callback(
        Output("api-buttons-container", "children"),
        Input("category-selector", "value")
    )
    def update_api_buttons(selected_category):
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
    # 버튼 클릭 or API 요청 버튼 클릭
    #
    @app.callback(
        [
            Output("dynamic-inputs", "children"),
            Output("selected-endpoint", "data"),
            Output("send-request", "style"),
            Output("api-response-table", "children"),
            Output("save-csv", "style"),
        ],
        [
            Input({"type": "api-button", "index": ALL}, "n_clicks"),
            Input("send-request", "n_clicks"),
        ],
        [
            State({"type": "api-button", "index": ALL}, "id"),
            State({"type": "input", "index": ALL}, "id"),
            State({"type": "input", "index": ALL}, "value"),
            State("selected-endpoint", "data"),
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
        total_clicks_buttons = sum(api_button_n_clicks) if api_button_n_clicks else 0
        if total_clicks_buttons == 0 and (not send_request_n_clicks or send_request_n_clicks == 0):
            raise dash.exceptions.PreventUpdate

        triggered_id = ctx.triggered_id

        # A. API 버튼 클릭
        if isinstance(triggered_id, dict) and triggered_id.get("type") == "api-button":
            selected_endpoint = triggered_id["index"]
            param_matches = re.findall(r":(\w+)", selected_endpoint)

            if param_matches:
                # 파라미터가 있으면 인풋 필드 노출
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
                return (
                    html.Div(inputs),
                    selected_endpoint,
                    {"display": "block"},
                    "",
                    {"display": "none"}
                )

            # 파라미터 없으면 -> 첫 페이지(10개)만 보여줌
            data_list = fetch_pages(selected_endpoint, max_pages=1, params={"per_page": 10})
            table = universal_generate_table(data_list)
            if isinstance(table, str) and table.startswith("❌"):
                return ("", selected_endpoint, {"display": "none"}, table, {"display": "none"})

            return (
                "",
                selected_endpoint,
                {"display": "none"},
                table,
                {"display": "block"}
            )

        # B. "API 요청 보내기" 버튼 클릭
        elif triggered_id == "send-request":
            if not stored_endpoint:
                return (
                    "",
                    "",
                    {"display": "none"},
                    "❌ API를 선택하세요.",
                    {"display": "none"}
                )

            # 인자 치환
            selected_endpoint = stored_endpoint
            if dynamic_input_ids and dynamic_input_values:
                for item, val in zip(dynamic_input_ids, dynamic_input_values):
                    selected_endpoint = selected_endpoint.replace(f":{item['index']}", str(val))

            data_list = fetch_pages(selected_endpoint, max_pages=1, params={"per_page": 10})
            table = universal_generate_table(data_list)
            if isinstance(table, str) and table.startswith("❌"):
                return (
                    dash.no_update,
                    stored_endpoint,
                    {"display": "block"},
                    table,
                    {"display": "none"}
                )

            return (
                dash.no_update,
                stored_endpoint,
                {"display": "block"},
                table,
                {"display": "block"}
            )
        
        else:
            raise dash.exceptions.PreventUpdate

    #
    # C. "CSV로 저장" 클릭 -> 전체 데이터 CSV
    #
    @app.callback(
        Output("download-dataframe-csv", "data"),
        Input("save-csv", "n_clicks"),
        State("selected-endpoint", "data"),
        prevent_initial_call=True
    )
    def download_csv(n_clicks, stored_endpoint):
        if not stored_endpoint:
            raise dash.exceptions.PreventUpdate

        # 전체 페이지 가져오기
        data_list = fetch_pages(stored_endpoint)
        if isinstance(data_list, str) and data_list.startswith("❌"):
            raise dash.exceptions.PreventUpdate

        # CSV 변환
        df = pd.DataFrame(data_list)
        if df.empty:
            raise dash.exceptions.PreventUpdate

        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False, encoding="utf-8-sig")
        csv_buffer.seek(0)

        return dcc.send_string(csv_buffer.getvalue(), filename="api_data.csv")

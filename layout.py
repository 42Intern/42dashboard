from dash import dcc, html
from api_categories import API_CATEGORIES

def create_layout():
    return html.Div([
        html.H1("42 Intra API 테스트 대시보드"),

        # 카테고리 선택 드롭다운
        html.Label("API 카테고리 선택"),
        dcc.Dropdown(
            id="category-selector",
            options=[{"label": key, "value": key} for key in API_CATEGORIES.keys()],
            placeholder="카테고리를 선택하세요",
        ),

        # 선택한 카테고리의 API 목록 버튼 표시
        html.Div(id="api-buttons-container", style={"margin-top": "20px"}),

        # API 요청을 위한 입력 필드 동적 생성 영역
        html.Div(id="dynamic-inputs", style={"margin-top": "20px"}),

        # 선택한 API 엔드포인트를 저장하는 숨겨진 Store
        dcc.Store(id="selected-endpoint", data=""),

        # "📡 API 요청 보내기" 버튼 (인자가 필요한 경우에만 표시)
        html.Button("📡 API 요청 보내기", id="send-request", n_clicks=0,
                    style={"margin-top": "10px", "display": "none"}),

        html.Hr(),

        # API 응답 출력 (첫 번째 페이지만 표시)
        html.Div(id="api-response-table", style={"margin-top": "20px"}),

        # "📥 CSV로 저장" 버튼 (첫 페이지 요청 후 표시)
        html.Button("📥 CSV로 저장", id="save-csv", n_clicks=0,
                    style={"margin-top": "10px", "display": "none"}),

        # CSV 다운로드 링크를 dcc.Loading으로 감싸서 진행 중 상태 표시
        dcc.Loading(
            id="download-loading",
            type="default",
            custom_spinner=html.Div("다운로드중..."),
            children=[dcc.Download(id="download-dataframe-csv")],
            style={"margin-top": "10px"}
        ),
    ])

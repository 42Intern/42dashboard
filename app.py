from dash import Dash
import layout
import callbacks

# Dash 앱 초기화
app = Dash(__name__, suppress_callback_exceptions=True)
app.layout = layout.create_layout()

# 콜백 등록
callbacks.register_callbacks(app)

if __name__ == "__main__":
    app.run_server(debug=True)

import dash_html_components as html
from dash import Dash


class DashReportServer:
    def __init__(self):
        external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

        # TODO: change page name (currently it is "Dash") to "Speaking Eye Reports"
        self.app = Dash(__name__, external_stylesheets=external_stylesheets)
        self.app.layout = self.__get_layout()

    def __get_layout(self) -> html.Div:
        return html.H1(children='Hello from Speaking Eye 👋')

    def run(self) -> None:
        # TODO: change port from 8050 (Dash default) to the first free port
        self.app.run_server()

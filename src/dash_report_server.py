import logging

import dash_html_components as html
from dash import Dash
from pydash import get


class DashReportServer:
    def __init__(self, logger: logging.Logger):
        # TODO: use static file
        external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
        self.app = Dash(__name__, external_stylesheets=external_stylesheets)

        logging.getLogger('werkzeug').setLevel(logging.WARNING)
        self.app.logger = logger

        self.app.title = 'Speaking Eye Reports'
        self.app.layout = self.__get_layout()

    def __get_layout(self) -> html.Div:
        return html.H1(children='Hello from Speaking Eye 👋')

    def run(self) -> None:
        # TODO: read port from config
        self.app.run_server(port=3838)

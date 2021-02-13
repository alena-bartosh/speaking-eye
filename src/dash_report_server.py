import logging
from datetime import date
from typing import Dict

import dash_core_components as dcc
import dash_html_components as html
from dash import Dash
from pydash import get

from activity_reader import ActivityReader
from application_info_matcher import ApplicationInfoMatcher


class DashReportServer:
    def __init__(self,
                 logger: logging.Logger,
                 app_config: Dict,
                 application_info_matcher: ApplicationInfoMatcher,
                 activity_reader: ActivityReader) -> None:
        # TODO: use static file
        external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
        self.app = Dash(__name__, external_stylesheets=external_stylesheets)

        logging.getLogger('werkzeug').setLevel(logging.WARNING)
        self.app.logger = logger

        self.app.title = 'Speaking Eye Reports'
        self.port = get(app_config, 'dash_report_server_port') or 3838

        self.application_info_matcher = application_info_matcher
        self.activity_reader = activity_reader

        self.app.layout = self.__get_layout()

    def __get_layout(self) -> html.Div:
        # TODO: calculate min_date_allowed from dest files with raw data

        return html.Div([
            html.H1(children='Hello from Speaking Eye 👋'),
            dcc.DatePickerSingle(
                display_format='YYYY-MM-DD',
                first_day_of_week=1,
                date=date.today()
            ),
        ])

    def run(self) -> None:
        self.app.run_server(port=self.port)

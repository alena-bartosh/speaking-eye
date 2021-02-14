import logging
from datetime import date, datetime
from enum import Enum
from typing import Dict, Optional

import dash_core_components as dcc
import dash_html_components as html
from dash import Dash
from dash.dependencies import Input, Output
from pydash import get

from activity_reader import ActivityReader
from activity_stat_holder import ActivityStatHolder, ActivityStatHolderItemsType
from files_provider import FilesProvider


class ElementId(Enum):
    DATE_PICKER = 'date-picker'
    REPORT_OUTPUT = 'report-output'


class DashReportServer:
    def __init__(self,
                 logger: logging.Logger,
                 app_config: Dict,
                 activity_reader: ActivityReader,
                 files_provider: FilesProvider) -> None:
        # TODO: use static file
        external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
        self.app = Dash(__name__, external_stylesheets=external_stylesheets)

        logging.getLogger('werkzeug').setLevel(logging.WARNING)
        self.app.logger = logger

        self.app.title = 'Speaking Eye Reports'
        self.port = get(app_config, 'dash_report_server_port') or 3838

        self.activity_reader = activity_reader
        self.files_provider = files_provider

        self.app.layout = self.__get_layout()

    def __get_layout(self) -> html.Div:
        # TODO: calculate min_date_allowed from dest files with raw data

        return html.Div([
            html.H1(children='Hello from Speaking Eye 👋'),
            dcc.DatePickerSingle(
                id=ElementId.DATE_PICKER.value,
                display_format='YYYY-MM-DD',
                first_day_of_week=1,
                date=date.today()
            ),
            html.Div(id=ElementId.REPORT_OUTPUT.value)
        ])

    def __get_report(self, report_date: date) -> ActivityStatHolderItemsType:
        activities = self.activity_reader.read(self.files_provider.get_raw_data_file_path(report_date))
        holder = ActivityStatHolder(activities)

        return holder.items()

    def __get_report_html(self, report: ActivityStatHolderItemsType) -> html.Div:
        # TODO: Add plot or table view
        report_items = [html.Div([html.Div(title), html.Div(f'{stat.work_time}')]) for (title, stat) in report]

        return html.Div(report_items)

    def run(self) -> None:
        @self.app.callback(
            Output(ElementId.REPORT_OUTPUT.value, 'children'),
            Input(ElementId.DATE_PICKER.value, 'date'))
        def handle_date_picker_change(date_value: Optional[str]) -> Optional[str]:
            # TODO: localization

            # NOTE: If could not parse date or field is empty then date_value will be None
            if date_value is None:
                return None

            report_date = datetime.strptime(date_value, '%Y-%m-%d').date()

            report = self.__get_report(report_date)

            return self.__get_report_html(report)

        self.app.run_server(port=self.port)

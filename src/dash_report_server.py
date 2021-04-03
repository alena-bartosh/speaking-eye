import logging
from datetime import date, datetime, timedelta
from enum import Enum
from typing import Dict, Optional

import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
from dash import Dash
from dash.dependencies import Input, Output
from pydash import get

from activity_reader import ActivityReader
from activity_stat_holder import ActivityStatHolder
from config_reader import ConfigReader
from datetime_formatter import DatetimeFormatter
from files_provider import FilesProvider
from special_application_info_title import SpecialApplicationInfoTitle


class ElementId(Enum):
    DATE_PICKER = 'date-picker'
    REPORT_OUTPUT = 'report-output'


class DashReportServer:
    def __init__(self,
                 logger: logging.Logger,
                 # TODO: replace with config_reader
                 app_config: Dict,
                 app_config_reader: ConfigReader,
                 activity_reader: ActivityReader,
                 files_provider: FilesProvider) -> None:
        # TODO: use static file
        external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
        self.app = Dash(__name__, external_stylesheets=external_stylesheets)

        logging.getLogger('werkzeug').setLevel(logging.WARNING)
        self.app.logger = logger

        self.app.title = 'Speaking Eye Reports'
        self.port = get(app_config, 'dash_report_server_port') or 3838

        self.work_time_limit = app_config_reader.get_work_time_limit()
        self.distracting_apps_mins = app_config_reader.get_distracting_apps_mins()

        self.activity_reader = activity_reader
        self.files_provider = files_provider

        self.app.layout = self.__get_layout()

    def __get_activity_stat_holder(self, activity_date: date) -> ActivityStatHolder:
        """Get ActivityStatHolder with all collected activities for specific date"""
        file_path = self.files_provider.get_raw_data_file_path(activity_date)
        activities = self.activity_reader.read(file_path)
        holder = ActivityStatHolder(activities)
        matcher = self.activity_reader.matcher

        holder.initialize_stats(matcher.detailed_app_infos)
        holder.initialize_stats(matcher.distracting_app_infos)

        return holder

    def __get_layout(self) -> html.Div:
        # TODO: calculate min_date_allowed from dest files with raw data

        return html.Div([
            dcc.DatePickerSingle(
                id=ElementId.DATE_PICKER.value,
                display_format='YYYY-MM-DD',
                first_day_of_week=1,
                date=date.today()
            ),
            html.Div(id=ElementId.REPORT_OUTPUT.value)
        ])

    def __get_report(self, activity_stat_holder: ActivityStatHolder, report_date: date) -> pd.DataFrame:
        report_data = {title: stat.work_time for title, stat in activity_stat_holder.items()}

        report = pd.DataFrame().from_dict(report_data, orient='index').reset_index()
        # TODO: use enum for column names
        report.columns = ['title', 'work_time']
        report = report.loc[report['work_time'].gt(timedelta(0))]
        report['date'] = report_date
        report['work_time_str'] = report['work_time'].astype(str)

        return report

    def __get_report_html(self, activity_stat_holder: ActivityStatHolder, report: pd.DataFrame) -> html.Div:
        if report.empty:
            return html.Div('No data for this day using current config!')

        # TODO: add text labels to pie -- find "text" property for px.pie like in go.Pie
        #       https://plotly.com/python/hover-text-and-formatting/

        figure = px.pie(report,
                        values='work_time',
                        names='title',
                        # TODO: format "work_time_str" column
                        hover_data=['work_time_str'])

        format_time = DatetimeFormatter.format_time_without_seconds

        break_time = activity_stat_holder[SpecialApplicationInfoTitle.BREAK_TIME.value].work_time
        formatted_break_time = format_time(break_time)
        formatted_work_time = format_time(activity_stat_holder.total_work_time - break_time)
        formatted_total_work_time = format_time(activity_stat_holder.total_work_time)
        formatted_work_time_limit = format_time(timedelta(hours=self.work_time_limit))
        distracting_app_infos = self.activity_reader.matcher.distracting_app_infos
        distracting_app_titles = [app_info.title for app_info in distracting_app_infos]
        distracting_time = activity_stat_holder.get_group_work_time(distracting_app_titles)
        formatted_distracting_time = format_time(distracting_time)

        return html.Div([
            html.Div(f'Expected work time: {formatted_work_time_limit}'),
            html.Div(f'Total work time: {formatted_total_work_time}'),
            # TODO: show as a html hint
            html.Div('Total work time = real work time + breaks + distracting activities'),
            html.Div(f'Total work time: {formatted_work_time} + {formatted_break_time} '
                     f'+ {formatted_distracting_time} = {formatted_total_work_time}'),
            dcc.Graph(figure=figure)
        ])

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
            activity_stat_holder = self.__get_activity_stat_holder(report_date)
            report = self.__get_report(activity_stat_holder, report_date)

            return self.__get_report_html(activity_stat_holder, report)

        self.app.run_server(port=self.port)

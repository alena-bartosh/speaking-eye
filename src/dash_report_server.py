import logging
import re
from datetime import date, datetime, timedelta
from enum import Enum
from random import choice
from typing import Optional

import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
from dash import Dash
from dash.dependencies import Input, Output

from activity_reader import ActivityReader
from activity_stat_holder import ActivityStatHolder
from config_reader import ConfigReader
from datetime_formatter import DatetimeFormatter
from files_provider import FilesProvider
from special_application_info_title import SpecialApplicationInfoTitle

COLORS_SEQUENTIALS = [
    px.colors.sequential.Viridis,
    px.colors.sequential.GnBu,
    px.colors.sequential.RdBu,
    px.colors.sequential.deep,
    px.colors.sequential.dense,
]


class ElementId(Enum):
    DATE_PICKER = 'date-picker'
    REPORT_OUTPUT = 'report-output'


class DashReportServer:
    def __init__(self,
                 logger: logging.Logger,
                 app_config_reader: ConfigReader,
                 activity_reader: ActivityReader,
                 files_provider: FilesProvider) -> None:
        self.app = Dash(__name__, assets_folder='../assets')

        logging.getLogger('werkzeug').setLevel(logging.WARNING)
        self.app.logger = logger

        self.app.title = 'Speaking Eye Reports'
        self.host = app_config_reader.get_report_server_host()
        self.port = app_config_reader.get_report_server_port()

        self.work_time_limit = app_config_reader.get_work_time_limit()
        self.distracting_apps_mins = app_config_reader.get_distracting_apps_mins()

        self.activity_reader = activity_reader
        self.files_provider = files_provider

        self.colors = choice(COLORS_SEQUENTIALS)

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

        # from timedelta as a string extract only time
        date_re = re.compile(r'.*([\d]{2}):([\d]{2}):([\d]{2}).*')
        report['work_time_str'] = report['work_time'].astype(str).str.replace(date_re, r'\1:\2:\3')

        return report

    def __get_report_html(self, activity_stat_holder: ActivityStatHolder, report: pd.DataFrame) -> html.Div:
        if report.empty:
            return html.Div('No data for this day using current config!')

        figure = px.pie(report,
                        values='work_time',
                        names='title',
                        custom_data=['work_time_str'],
                        color_discrete_sequence=self.colors)
        figure.update(layout_showlegend=False)

        figure.update_traces(textposition='inside',
                             hovertemplate='%{label} | %{customdata}',
                             textinfo='percent+label')

        figure.update_layout(
            hoverlabel=dict(
                bgcolor='white',
                font_size=14,
                font_family='Rockwell',
            )
        )

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
            html.H3(children='Work time'),
            html.Table(
                # headers
                [html.Tr([html.Th(col) for col in [
                    'Expected', 'Actual', 'Pure work',
                    'Breaks', 'Distracting activities'
                ]])] +
                # body
                [html.Tr([html.Td(time) for time in [
                    formatted_work_time_limit, formatted_total_work_time, formatted_work_time,
                    formatted_break_time, formatted_distracting_time
                ]])]
            ),
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

        self.app.run_server(self.host, self.port)

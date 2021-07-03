import logging
import re
from datetime import date, datetime, timedelta
from enum import Enum
from random import choice
from typing import List, Optional, Tuple

import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
from dash import Dash
from dash.dependencies import Input, Output
from pydash import some

from activity_reader import ActivityReader
from activity_stat_holder import ActivityStatHolder
from config_reader import ConfigReader
from datetime_formatter import DatetimeFormatter
from datetime_helper import DatetimeHelper
from files_provider import FilesProvider
from localizator import Localizator
from special_application_info_title import SpecialApplicationInfoTitle

COLORS_SEQUENTIALS = [
    px.colors.sequential.Viridis,
    px.colors.sequential.GnBu,
    px.colors.sequential.deep,
    px.colors.sequential.dense,
]


class ElementId(Enum):
    DATE_PICKER = 'date-picker'
    REPORT_OUTPUT = 'report-output'


GetActivityStatHolderResultType = Tuple[
    ActivityStatHolder,
    int,  # active_days_count
]


class DashReportServer:
    def __init__(self,
                 logger: logging.Logger,
                 app_config_reader: ConfigReader,
                 activity_reader: ActivityReader,
                 files_provider: FilesProvider,
                 localizator: Localizator) -> None:
        self.app = Dash(__name__, assets_folder='../assets')

        logging.getLogger('werkzeug').setLevel(logging.WARNING)
        logging.getLogger('parse').setLevel(logging.WARNING)
        self.app.logger = logger

        self.localizator = localizator
        self.app.title = self.localizator.get('report_server.tab_title')

        self.host = app_config_reader.get_report_server_host()
        self.port = app_config_reader.get_report_server_port()

        self.work_time_limit = app_config_reader.get_work_time_limit()
        self.distracting_apps_mins = app_config_reader.get_distracting_apps_mins()

        self.ignore_weekends = app_config_reader.get_report_server_ignore_weekends()

        self.activity_reader = activity_reader
        self.files_provider = files_provider

        self.colors = choice(COLORS_SEQUENTIALS)

        self.app.layout = self.__get_layout()

    def __get_activity_stat_holder(self, report_dates: List[date]) -> GetActivityStatHolderResultType:
        """Get ActivityStatHolder with all collected activities for specific dates"""
        active_days_count = 0
        all_activities = []
        for report_date in report_dates:
            is_weekend = report_date.weekday() > 4

            if self.ignore_weekends and is_weekend:
                continue

            file_path = self.files_provider.get_raw_data_file_path(report_date)
            activities = self.activity_reader.read(file_path)

            no_activities_for_date = len(activities) == 0

            if no_activities_for_date:
                continue

            no_work_activities_for_date = not some(activities, lambda activity: activity.is_work_time)

            if no_work_activities_for_date:
                continue

            active_days_count += 1
            all_activities.extend(activities)

        holder = ActivityStatHolder(all_activities)
        matcher = self.activity_reader.matcher

        holder.initialize_stats(matcher.detailed_app_infos)
        holder.initialize_stats(matcher.distracting_app_infos)

        return holder, active_days_count

    def __get_layout(self) -> html.Div:
        today = date.today()

        return html.Div(
            [
                html.H3(self.localizator.get('report_server.page_title')),
                dcc.DatePickerRange(
                    id=ElementId.DATE_PICKER.value,
                    display_format='YYYY-MM-DD',
                    first_day_of_week=1,
                    min_date_allowed=self.files_provider.get_date_of_first_raw_data_file(),
                    max_date_allowed=today + timedelta(days=1),
                    initial_visible_month=today,
                    # NOTE: allow to select the single date for start & end
                    minimum_nights=0,
                    start_date=today,
                    end_date=today,
                    updatemode='bothdates',
                ),
                dcc.Loading(
                    [html.Div(id=ElementId.REPORT_OUTPUT.value)],
                    type='graph',
                    color=choice(self.colors)
                ),
            ],
            style=dict(display='flex', flexDirection='column', alignItems='center'),
        )

    def __get_report(self, activity_stat_holder: ActivityStatHolder, active_days_count: int) -> pd.DataFrame:
        report_data = {title: stat.work_time for title, stat in activity_stat_holder.items()}

        report = pd.DataFrame().from_dict(report_data, orient='index').reset_index()
        # TODO: use enum for column names
        report.columns = ['title', 'work_time']
        report['work_time'] = pd.to_timedelta(report['work_time'])

        report = report.loc[report['work_time'].gt(timedelta(0))]
        report['mean_work_time'] = report['work_time'] / active_days_count

        # from timedelta as a string extract only time
        time_re = re.compile(r'.*([\d]{2}):([\d]{2}):([\d]{2}).*')
        report['mean_work_time_str'] = report['mean_work_time'].astype(str).str.replace(time_re, r'\1:\2:\3')

        return report

    def __get_report_html(self, activity_stat_holder: ActivityStatHolder,
                          report: pd.DataFrame, active_days_count: int) -> html.Div:
        if report.empty:
            return html.Div(self.localizator.get('report_server.no_data'))

        figure = px.pie(report,
                        values='mean_work_time',
                        names='title',
                        custom_data=['mean_work_time_str'],
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

        distracting_app_infos = self.activity_reader.matcher.distracting_app_infos
        distracting_app_titles = [app_info.title for app_info in distracting_app_infos]

        break_time = activity_stat_holder[SpecialApplicationInfoTitle.BREAK_TIME.value].work_time
        mean_break_time = break_time / active_days_count
        mean_total_work_time = activity_stat_holder.total_work_time / active_days_count
        distracting_time = activity_stat_holder.get_group_work_time(distracting_app_titles)
        mean_distracting_time = distracting_time / active_days_count
        mean_pure_work_time = mean_total_work_time - mean_break_time - mean_distracting_time

        format_time = DatetimeFormatter.format_time_without_seconds

        return html.Div([
            html.Table(
                # headers
                [html.Tr([html.Th(col) for col in [
                    self.localizator.get('report_server.expected_col'),
                    self.localizator.get('report_server.actual_col'),
                    self.localizator.get('report_server.pure_work_col'),
                    self.localizator.get('report_server.breaks_col'),
                    self.localizator.get('report_server.distracting_col'),
                ]])] +
                # body
                [html.Tr([html.Td(time) for time in [
                    format_time(timedelta(hours=self.work_time_limit)),
                    format_time(mean_total_work_time),
                    format_time(mean_pure_work_time),
                    format_time(mean_break_time),
                    format_time(mean_distracting_time)
                ]])]
            ),
            html.Div(
                [
                    self.localizator.get('report_server.average_text'),
                    html.B(f'{active_days_count} ', style=dict(color='darkcyan')),
                    self.localizator.get('report_server.days_text'),
                ],
                style=dict(textAlign='center')
            ),
            dcc.Graph(figure=figure)
        ])

    def run(self) -> None:
        @self.app.callback(  # type: ignore[misc]
            Output(ElementId.REPORT_OUTPUT.value, 'children'),
            [
                Input(ElementId.DATE_PICKER.value, 'start_date'),
                Input(ElementId.DATE_PICKER.value, 'end_date'),
            ]
        )
        def handle_date_picker_change(start_date_value: str,
                                      end_date_value: str) -> Optional[html.Div]:
            try:
                start_date = datetime.strptime(start_date_value, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date_value, '%Y-%m-%d').date()
                report_dates = DatetimeHelper.get_dates_between(start_date, end_date)

                activity_stat_holder, active_days_count = self.__get_activity_stat_holder(report_dates)
                report = self.__get_report(activity_stat_holder, active_days_count)

                return self.__get_report_html(activity_stat_holder, report, active_days_count)

            except Exception as err:
                return html.Div(self.localizator.get('report_server.error', err=str(err)),
                                style={'textAlign': 'center'})

        self.app.run_server(self.host, self.port)

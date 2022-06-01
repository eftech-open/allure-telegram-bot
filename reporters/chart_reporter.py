import os
import uuid
import emoji
import matplotlib.pyplot as plot
from tools.dates import form_nowdate, form_timedelta


class ChartReporter:
    """
    Pie chart reporter
    """

    def __init__(self):
        self._allure_url = os.environ.get('ALLURE_URL')
        self._allure_project = os.environ.get('ALLURE_PROJECT')
        self._report_delta = os.environ.get('REPORT_TIMEDELTA')
        self._report_critical = os.environ.get('REPORT_CRITICAL_PERCENT')
        self._report_path = os.environ.get('REPORT_CHART_PATH')

    def _form_status(self, passed, broken, failed) -> dict:
        return {"passed": passed, "failed": failed, "broken": broken}

    def _form_file_path(self):
        return f"{self._report_path}{form_nowdate()}{uuid.uuid4()}.png"

    def _form_time_interval(self) -> str:
        time_from = form_timedelta(minutes=int(self._report_delta))
        return f"I found unsuccessful launch in the period from {time_from} по {form_nowdate()}"

    def _create_chart(self, passed, broken, failed) -> str:
        statuses = self._form_status(passed, broken, failed)
        labels, sizes, colors = list(), list(), list()
        for key, value in statuses.items():
            if value > 0:
                labels.append(key.upper())
                sizes.append(value)
                if key == "passed":
                    colors.append('#96cc64')
                elif key == "failed":
                    colors.append('#fd5a3e')
                elif key == "broken":
                    colors.append('#ffd050')

        plot.pie(
            x=sizes,
            colors=colors,
            autopct=lambda p: '{:,.0f}'.format(p * sum(sizes) / 100),
            startangle=120,
            pctdistance=0.85,
            textprops=dict(rotation_mode='anchor', va='center', ha='center'),
            labeldistance=1.2
        )
        plot.legend(labels, loc="upper left")
        centre_circle = plot.Circle((0, 0), 0.70, fc='white')
        fig = plot.gcf()
        fig.gca().add_artist(centre_circle)

        plot.axis('equal')
        plot.tight_layout()

        file_path = self._form_file_path()

        plot.savefig(file_path, dpi=300)
        plot.close()

        return file_path

    def _create_info_message(self, summary: dict, start_info_message: str, get_defects: bool = False) -> tuple:
        passed, failed, broken = 0, 0, 0

        alarm_emoji = emoji.emojize(':rotating_light:', use_aliases=True)
        info_message = f"{alarm_emoji} {start_info_message} {alarm_emoji}\n"

        launch_with_failed_tests = ""
        launch_with_broken_tests = ""
        launch_defects = set()

        for key, value in summary.items():
            launch_url = f"\- [{value['name'].replace('.', ':')}]({{self._allure_url}}/launch/{key})\n"
            statistic = summary[key]['statistic']

            for status in statistic:
                if status['status'] == 'passed':
                    passed = passed + status['count']
                elif status['status'] == 'broken':
                    broken = broken + status['count']
                    launch_with_broken_tests = launch_with_broken_tests + launch_url
                elif status['status'] == 'failed':
                    failed = failed + status['count']
                    launch_with_failed_tests = launch_with_failed_tests + launch_url

            if get_defects:
                defects = summary[key].get('defects')
                if defects:
                    for defect in defects:
                        defect_name = defect["name"]
                        defect_id = defect["id"]
                        defect_url = f"\- [{defect_name}]" \
                                     f"({self._allure_url}/project/{self._allure_project}/defects/{defect_id})\n"
                        launch_defects.add(defect_url)

        if failed == 0 and broken == 0:
            info_message = "All tests have passed"
        else:
            if launch_with_failed_tests != "":
                info_message = info_message + "\nLaunches with FAILED status:\n" + launch_with_failed_tests
            if launch_with_broken_tests != "":
                info_message = info_message + "\nLaunches with BROKEN status:\n" + launch_with_broken_tests
            if len(launch_defects) > 0:
                unpacked_launch_defects = ""
                for defect in launch_defects:
                    unpacked_launch_defects += defect
                info_message = info_message + "\nDefects:\n" + unpacked_launch_defects

        return passed, failed, broken, info_message

    def _count_statistic(self, summary: dict) -> dict:
        filtered_summary = dict()
        for key, value in summary.items():
            statistic = summary[key]['statistic']
            passed, failed, broken = 0, 0, 0
            for status in statistic:
                if status['status'] == 'passed':
                    passed = status['count']
                elif status['status'] == 'broken':
                    broken = status['count']
                elif status['status'] == 'failed':
                    failed = status['count']
            if (100 / (passed + broken + failed)) * (broken + failed) > int(self._report_critical):
                filtered_summary[key] = value
        return filtered_summary

    def generate_full_report(self, summary: dict) -> dict:
        message = self._form_time_interval()
        passed, failed, broken, info_message = self._create_info_message(
            summary=summary,
            start_info_message=message,
            get_defects=True
        )
        file_path = self._create_chart(passed, broken, failed)
        return {'file': file_path, 'message': info_message}

    def generate_critical_report(self, summary: dict) -> dict:
        filtered_summary = self._count_statistic(summary)
        message = f"{self._form_time_interval()} with critical {self._report_critical}%"
        passed, failed, broken, info_message = self._create_info_message(
            summary=filtered_summary,
            start_info_message=message,
            get_defects=True
        )
        file_path = self._create_chart(passed, broken, failed)
        return {'file': file_path, 'message': info_message}


reporter = ChartReporter()

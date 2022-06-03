import os
import json
import base64
import logging
from time import sleep

from dotenv import load_dotenv
from tools.dates import form_timedelta, change_date_pattern, change_to_timestamp
from tools.http_client import http_client

load_dotenv()


class AllureAdapter:
    """
    Allure TestOps API adapter
    """

    def __init__(self):
        self._allure_url = os.environ.get('ALLURE_URL')
        self._allure_project = os.environ.get('ALLURE_PROJECT')
        self._allure_token = os.environ.get('ALLURE_USER_TOKEN')
        self._timedelta = os.environ.get('REPORT_TIMEDELTA')
        self._token = None
        self._headers = None

    @staticmethod
    def _encode_request(request: dict) -> str:
        format_list = [request.copy()]
        decode = json.dumps(format_list)
        return base64.b64encode(decode.encode()).decode()

    def _form_search_query(self, request_id: str, request_type: str, time_from: str = None) -> dict:
        if not time_from:
            time_from = form_timedelta(minutes=int(self._timedelta), pattern="%d/%m/%Y %H:%M:%S")
        to_date = change_date_pattern(date_string=time_from, pattern="%d/%m/%Y %H:%M:%S")
        time_value = change_to_timestamp(date_string=to_date)
        return {
            "id": request_id,
            "type": request_type,
            "value": time_value
        }

    """
    Authorization methods
    """

    def login_with_token(self) -> None:
        response_token = http_client(base_url=self._allure_url).post(
            endpoint='/api/uaa/oauth/token',
            data={
                'token': self._allure_token,
                'grant_type': 'apitoken',
                'scope': 'openid'
            }
        )
        self._token = response_token.json()['access_token']
        self._headers = {'Authorization': 'Bearer ' + self._token}

    """
    Get launch data methods
    """

    def get_last_launches(self) -> list:
        launch_query = self._form_search_query(request_id='createdAfter', request_type='long')
        search_list = self._encode_request(launch_query)
        last_launches = http_client(base_url=self._allure_url).get(
            headers=self._headers,
            endpoint='/api/rs/launch',
            params={
                'projectId': self._allure_project,
                'page': 0,
                'preview': 'true',
                'search': search_list,
                'size': 100
            }
        )
        return json.loads(last_launches.text)['content']

    def get_launch_defects(self, allure_launches: dict) -> dict:
        launch_results = dict()
        for key, value in allure_launches.items():
            if value['status'] == "finished":
                defects_job_info = http_client(base_url=self._allure_url).get(
                    headers=self._headers,
                    endpoint=f'/api/rs/launch/{key}/defect'
                )
                if json.loads(defects_job_info.text)['content']:
                    defects = json.loads(defects_job_info.text)['content']
                    for defect in defects:
                        defect.pop('closed')
                        defect.pop('count')
                    launch_results[key] = {'defects': defects}
        return launch_results

    def get_launch_statistic(self, allure_launches: dict) -> dict:
        statistic = dict()
        for key, value in allure_launches.items():
            if value['status'] == "finished":
                result = http_client(base_url=self._allure_url).get(
                    headers=self._headers,
                    endpoint=f'/api/rs/launch/{key}/statistic',
                )
                launch = json.loads(result.text)
                statistic[key] = {'statistic': launch}
        return statistic

    """
    Parse launch data methods
    """

    def parse_launches_with_id(self, data: list) -> tuple:
        launches = dict()
        for item in data:
            launches[item.get("id")] = dict()
            launches[item.get("id")]['status'] = item.get("id")
            launches[item.get("id")]['name'] = item.get("name")
        id_launch = list({int(item["id"]) for item in data})
        return launches, id_launch

    def parse_launch_results(self, launch_results: dict) -> dict:
        results_modify = dict()
        for key, value in launch_results.items():
            test_case_results = []
            for item in value:
                test_case = dict()
                test_case["test_case_id"] = item.get("testCaseId")
                test_case["test_case_launch_id"] = item.get("id")
                test_case["name"] = item.get("name")
                test_case["status"] = item.get("status")
                test_case_results.append(test_case)
            results_modify[key] = test_case_results
        return results_modify

    """
    Методы анализа результатов запусков
    """

    def analyze_results(self, allure_launches: dict) -> dict:
        launch_results = dict()
        for key, value in allure_launches.items():
            if value['status'] == "finished":
                job_info = http_client(base_url=self._allure_url).get(
                    headers=self._headers,
                    endpoint='/api/rs/testresulttree/leaf',
                    params={
                        'launchId': key,
                        'size': 100
                    }
                )
                launch_result = json.loads(job_info.text)['content']
                launch_results[key] = launch_result
        return launch_results

    @staticmethod
    def compare_results(launches: dict, pipeline_statuses: dict) -> dict:
        for key, value in launches.items():
            launches[key]['status'] = pipeline_statuses[value['status']]
        return launches

    @staticmethod
    def compare_processed_launches(launch_summary: dict, processed_launches: list) -> dict:
        for item in processed_launches:
            launch_summary.pop(item, None)
        return launch_summary

    """
    Form report methods
    """

    def form_summary(self, compared_launches: dict, launch_results: dict, statistic: dict,
                     defects: dict) -> dict:
        summary = dict()
        for key, value in launch_results.items():
            summary[key] = dict()
        for key, value in launch_results.items():
            summary[key]['summary'] = value
        for key, value in compared_launches.items():
            summary[key]['name'] = compared_launches[key]['name']
        for key, value in statistic.items():
            summary[key]['statistic'] = statistic[key]['statistic']
        for key, value in defects.items():
            summary[key]['defects'] = defects[key]['defects']
        return summary

    """
    Launch status methods
    """

    def get_launch_status(self, launch_id: int) -> str:
        launch_info = http_client(base_url=self._allure_url).get(
            headers=self._headers,
            endpoint=f'/api/rs/launch/{launch_id}/job'
        )
        return json.loads(launch_info.text)[0].get('stage')

    def get_launch_error(self, launch_id: int) -> str:
        launch_info = http_client(base_url=self._allure_url).get(
            headers=self._headers,
            endpoint=f'/api/rs/launch/{launch_id}/job'
        )
        return json.loads(launch_info.text)[0].get('errorMessage')

    def wait_launch_status(self, launch_id: list, retries: int = 50, interval: int = 10) -> dict:
        statuses = dict()
        for launch in launch_id:
            while retries > 0:
                launch_status = self.get_launch_status(launch)
                if launch_status in ["finished", "run_failure"]:
                    statuses.update({launch: launch_status})
                    break
                else:
                    logging.debug(f"Waiting for launch '{self._allure_url}/launch/{launch}' finished status")
                    sleep(interval)
                    retries -= 1
                    continue
        return statuses


allure = AllureAdapter()

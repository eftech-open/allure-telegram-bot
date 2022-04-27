import os
import logging
from telegram import Update
from telegram.ext import CallbackContext
from typing import Optional
from bot import mongo_persistence, allure

"""
Subscriptions
"""


def subscribe_all(context: CallbackContext, chat_id) -> None:
    context.dispatcher.chat_data[chat_id]["subscription"] = 'all'
    logging.info(f"'{chat_id}' has subscribed in full report")


def subscribe_critical(context: CallbackContext, chat_id) -> None:
    context.dispatcher.chat_data[chat_id]["subscription"] = 'critical'
    logging.info(f"'{chat_id}' has subscribed in critical report")


def unsubscribe(context: CallbackContext, chat_id) -> None:
    context.dispatcher.chat_data[chat_id]["subscription"] = False
    logging.info(f"'{chat_id}' has unsubscribed")


def set_chat_info(update: Update, context: CallbackContext, chat_id) -> None:
    if update.effective_chat.type == 'group':
        context.dispatcher.chat_data[chat_id]["title"] = update.effective_chat.title
        logging.info(f"Group '{chat_id}': title - {update.effective_chat.title}")

    elif update.effective_chat.type == 'private':
        context.dispatcher.chat_data[chat_id]["username"] = update.effective_chat.username
        logging.info(f"Private '{chat_id}': username - {update.effective_chat.username}")


"""
Launches
"""


def collect_launch_statistic() -> Optional[dict]:
    cleaner = os.environ.get('CLEAR_DB_LAUNCHES')
    allure.login_with_token()
    launches = allure.get_last_launches()

    if (len(launches)) > 0:
        allure_launches, id_launches = allure.parse_launches_with_id(launches)
        allure_statuses = allure.wait_launch_status(id_launches)
        compared_allure_launches = allure.compare_results(allure_launches, allure_statuses)

        launch_results = allure.analyze_results(compared_allure_launches)
        parsed_launch_results = allure.parse_launch_results(launch_results)

        launch_statistic = allure.get_launch_statistic(compared_allure_launches)
        launch_defects = allure.get_launch_defects(compared_allure_launches)

        summary = allure.form_summary(compared_allure_launches, parsed_launch_results, launch_statistic,
                                      launch_defects)

        if cleaner == 'True':
            processed_launches = mongo_persistence.get_launch_data()
            summary = allure.compare_processed_launches(summary, processed_launches)
            mongo_persistence.update_launch_data(summary)

        return summary
    else:
        return


"""
Cleanup
"""


def clean_processed_launches(_) -> None:
    mongo_persistence.drop_table()
    logging.info("Table 'launch_data' has dropped")


def clean_tmp(_) -> None:
    chart_path = os.environ.get('REPORT_CHART_PATH')
    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../', chart_path)
    for root, dirs, files in os.walk(path):
        for file in files:
            if '.png' in file:
                os.remove(path + file)
    logging.info(f"Directory '{chart_path}' has cleared")

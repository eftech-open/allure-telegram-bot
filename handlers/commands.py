import os
import logging
from telegram import Update, parsemode
from telegram.error import Unauthorized
from telegram.ext import CallbackContext
from handlers.utils import collect_launch_statistic, unsubscribe, subscribe_all, set_chat_info, subscribe_critical
from reporters.chart_reporter import reporter

report_critical = os.environ.get('REPORT_CRITICAL_PERCENT')


def start(update: Update, context: CallbackContext) -> None:
    from_user = update.message.from_user.name
    message = f"Hey, {from_user}!\n" \
              f"Enter /help for commands list"
    update.message.reply_text(message)


def help_info(update: Update, context: CallbackContext) -> None:
    message = "Enter /notify_all to activate notifications to all notification \n" \
              "Enter /notify_critical to activate notifications for critical notifications\n" \
              "Enter /remove_notify to deactivate all notifications\n"
    update.message.reply_text(message)


def remove_notify(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    subscription = context.dispatcher.chat_data[chat_id]["subscription"]

    if subscription or subscription == 'all' or subscription == 'critical':
        text = 'Notifications deactivated'
        unsubscribe(context, chat_id)
    elif not subscription:
        text = 'You have not any active notifications'
    else:
        text = 'Command execution error'
    update.message.reply_text(text)


def notify_all(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    subscription = context.dispatcher.chat_data[chat_id].get("subscription")

    if not subscription:
        subscribe_all(context, chat_id)
        set_chat_info(update, context, chat_id)
        text = 'You have already subscribed for all notifications!'
    elif subscription == 'critical':
        subscribe_all(context, chat_id)
        set_chat_info(update, context, chat_id)
        text = f'You have changed subscriptions from critical > {report_critical}% to all!'
    elif subscription == 'all':
        text = 'You have already subscribed for all notifications!'
    else:
        text = 'Command execution error'
    update.message.reply_text(text)


def notify_critical(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    subscription = context.dispatcher.chat_data[chat_id].get("subscription")

    if not subscription:
        subscribe_critical(context, chat_id)
        set_chat_info(update, context, chat_id)
        text = f'You have subscribed to \'critical\' with > {report_critical}%'
    elif subscription == 'all':
        subscribe_critical(context, chat_id)
        set_chat_info(update, context, chat_id)
        text = f'Subscription changed to \'critical\' with > {report_critical}%'
    elif subscription == 'critical':
        text = f'You have already subscribed to \'critical\' with > {report_critical}%'
    else:
        text = 'Command execution error'
    update.message.reply_text(text)


def perform_notify(context: CallbackContext) -> None:
    summary = collect_launch_statistic()
    if summary != {}:
        full_report = reporter.generate_full_report(summary)
        critical_report = reporter.generate_critical_report(summary)
        all_subs = []
        critical_subs = []
        for key in context.dispatcher.chat_data.keys():
            subscription = context.dispatcher.chat_data[key].get("subscription")
            if subscription == 'all':
                all_subs.append(key)
            elif subscription == 'critical':
                critical_subs.append(key)

        if "Все тесты прошли успешно" not in critical_report["message"]:
            for chat_id in critical_subs:
                try:
                    context.bot.send_photo(
                        chat_id=chat_id,
                        photo=open(critical_report['file'], 'rb'),
                        caption=critical_report["message"],
                        parse_mode=parsemode.ParseMode.MARKDOWN_V2
                    )

                    logging.debug(f"Message send to '{chat_id}' with 'critical' subscription")
                except Unauthorized:
                    unsubscribe(context, chat_id)
        else:
            logging.debug("Найденные запуски не содержат критическое кол-во упавших тестов")

        if "Все тесты прошли успешно" not in full_report["message"]:
            for chat_id in all_subs:
                try:
                    context.bot.send_photo(
                        chat_id=chat_id,
                        photo=open(full_report['file'], 'rb'),
                        caption=full_report["message"],
                        parse_mode=parsemode.ParseMode.MARKDOWN_V2
                    )

                    logging.debug(f"Message send to '{chat_id}' with 'all' subscription")
                except Unauthorized:
                    unsubscribe(context, chat_id)
        else:
            logging.debug("All tests in launch are passed")
    else:
        logging.debug("New launches not found")

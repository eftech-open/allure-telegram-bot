import os
import logging
from telegram import Update, parsemode
from telegram.error import Unauthorized
from telegram.ext import CallbackContext
from handlers.utils import collect_launch_statistic, unsubscribe, subscribe_all, set_chat_info, subscribe_critical
from reporters.chart import reporter

report_critical = os.environ.get('REPORT_CRITICAL_PERCENT')


def start(update: Update, context: CallbackContext) -> None:
    from_user = update.message.from_user.name
    message = f"Hey, {from_user}!\n" \
              f"Send /help for commands list"
    update.message.reply_text(message)


def help_info(update: Update, context: CallbackContext) -> None:
    message = "Send /notify_all to activate notifications to all notification \n" \
              "Send /notify_critical to activate notifications for critical notifications\n" \
              "Send /remove_notify to deactivate all notifications\n"
    update.message.reply_text(message)


def remove_notify(update: Update, context: CallbackContext) -> None:
    """
    Disabling notifications
    """
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
    """
    Subscribe to all launch notification
    """
    chat_id = update.message.chat_id
    subscription = context.dispatcher.chat_data[chat_id].get("subscription")

    if not subscription:
        subscribe_all(context, chat_id)
        set_chat_info(update, context, chat_id)
        text = 'You have subscribed for all notifications!'
    elif subscription == 'critical':
        subscribe_all(context, chat_id)
        set_chat_info(update, context, chat_id)
        text = f'Done! You have changed subscriptions from critical > {report_critical}% to all!'
    elif subscription == 'all':
        text = 'Oops! You have already subscribed for all notifications!'
    else:
        text = 'Command execution error'
    update.message.reply_text(text)


def notify_critical(update: Update, context: CallbackContext) -> None:
    """
    Subscribe to critical launch notification
    """
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
    """
    Sending a message to a bot
    :param context: context
    """
    summary = collect_launch_statistic()
    if summary != {}:
        all_subs = []
        critical_subs = []
        for key in context.dispatcher.chat_data.keys():
            subscription = context.dispatcher.chat_data[key].get("subscription")
            if subscription == 'all':
                all_subs.append(key)
            elif subscription == 'critical':
                critical_subs.append(key)

        report = reporter.generate_report(summary)

        if (report["status"] == "failure") and (len(critical_subs) > 0):
            _send_report(report_file=report['file_critical'], report_message=report['message_critical'], context=context,
                         subs=critical_subs, subscription=subscription)
        else:
            logging.debug("The number of failed tests does not exceed a critical value")

        if (report["status"] == "failure") and (len(all_subs) > 0):
            _send_report(report_file=report['file_all'], report_message=report['message_all'], context=context,
                         subs=all_subs, subscription=subscription)
        else:
            logging.debug("All tests in launch are passed")

    else:
        logging.debug("New launches not found")


def _send_report(report_file: str, report_message: str, context: CallbackContext, subs: list,
                 subscription: str) -> None:
    """
    Send report
    :param report_file: the path to the generated launch picture
    :param report_message: message text
    :param context: context
    :param subs: list of subscribers
    :param subscription: type subscription
    """
    for chat_id in subs:
        try:
            context.bot.send_photo(
                chat_id=chat_id,
                photo=open(report_file, 'rb'),
                caption=report_message,
                parse_mode=parsemode.ParseMode.MARKDOWN_V2
            )
        except Unauthorized as error:
            logging.info(error.message)
            unsubscribe(context, chat_id)

        logging.debug(f"Message send to '{chat_id}' with '{subscription}' subscription")

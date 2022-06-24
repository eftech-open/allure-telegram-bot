import os
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv
from datetime import time
from handlers.utils import clean_processed_launches, clean_tmp
from handlers.commands import start, help_info, remove_notify, perform_notify, notify_critical, notify_all

from logging import config
from pytz import timezone
from persistence.mongo import mongo_persistence
from telegram import Update
from telegram.ext import Updater, CommandHandler

load_dotenv()

config.fileConfig(fname='logging.conf', disable_existing_loggers=True)


def main() -> None:
    updater = Updater(
        token=os.environ.get('BOT_TOKEN'),
        persistence=mongo_persistence
    )

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler(command="start", callback=start))
    dispatcher.add_handler(CommandHandler(command="help_info", callback=help_info))
    dispatcher.add_handler(CommandHandler(command="notify_all", callback=notify_all))
    dispatcher.add_handler(CommandHandler(command="notify_critical", callback=notify_critical))
    dispatcher.add_handler(CommandHandler(command="remove_notify", callback=remove_notify))

    dispatcher.job_queue.run_repeating(
        callback=perform_notify,
        interval=int(os.environ.get("REPORT_INTERVAL")),
        first=10
    )
    dispatcher.job_queue.run_daily(
        callback=clean_processed_launches,
        time=time(hour=23, minute=00, tzinfo=timezone('Europe/Moscow'))
    )
    dispatcher.job_queue.run_custom(
        callback=clean_tmp,
        job_kwargs={
            'trigger': CronTrigger.from_crontab(
                expr=os.environ.get('CLEAR_DATE_TMP'),
                timezone=os.environ.get('TIMEZONE')
            ),
            'max_instances': 3
        }
    )

    updater.start_polling(allowed_updates=Update.ALL_TYPES)
    updater.idle()


if __name__ == '__main__':
    main()

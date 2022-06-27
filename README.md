# Allure Telegram Bot

Telegram bot for Allure TestOps

## Requirements

* Python 3.8+
* MongoDB 5.0+

## Features

- Allure TestOps compatibility
- Subscriptions
- Mongo persistence
- Pie chart report
- Detailed logger

## How it works

1. User / group subscribes to launch information: all or critical
2. The bot checks new launches in the program every 20 minutes
3. The bot notifies the user / group of new launches

## Supporter Commands

* /help - shows list of commands
* /notify_all - subscribes to all launches
* /notify_critical - subscribes to critical launches according percentage of failed tests
* /remove_notify - unsubscribes from all launches

## Deployment

Deployment is available both through the launch of the repository and through the docker image

1. Download repository or docker image

   via repository:

    ```bash
    git clone https://github.com/eftech-open/allure-telegram-bot.git && cd allure-telegram-bot
    ```

   via docker image:

    ```bash
    docker pull eftech-open/allure-telegram-bot:master
    ```

2. Generate .env-file with required variables

    ```bash
    python3 setup_bot.py
    ```

3. Run bot

    via repository:
    
    ```bash
    python3 bot.py
    ```

    via docker image:

    ```bash
    docker run -d --env-file ./.env eftech-open/allure-telegram-bot:master
    ```
   
    via docker-compose:
    
    ```bash
    docker-compose -f docker-compose.yml up
    ```

### Variables

The following variables are available for launching and configuring the bot

| Variables               | Description                                                 | Default         |
|-------------------------|-------------------------------------------------------------|-----------------|
| ALLURE_PROJECT          | Allure TestOps project ID                                   | Not set         |
| ALLURE_URL              | Allure TestOps URL                                          | Not set         |
| ALLURE_TOKEN            | Allure TestOps user API_token                               | Not set         |
| BOT_TOKEN               | Telegram bot token                                          | Not set         |
| MONGO_HOST              | MongoDB host address                                        | `mongo_db`      |
| MONGO_PORT              | MongoDB port                                                | `27017`         |
| MONGO_DATABASE          | MongoDB database                                            | `allure_bot`    |
| REPORT_INTERVAL         | Frequency of checking for new launches (minutes)            | `20`            |
| REPORT_TIMEDELTA        | Search for new launches in the last minutes                 | `200`           |
| REPORT_CHART_PATH       | Temporary image storage directory                           | `./tmp/`        |
| REPORT_CRITICAL_PERCENT | Percentage of failed tests in run for critical notification | `50`            |
| TIMEZONE                | Time zone for cron jobs                                     | `UTC`           |
| CLEAR_DB_LAUNCHES       | Clearing report images                                      | `True`          |
| CLEAR_DATE_TMP          | Cron interval for clearing report images                    | `59 23 */5 * *` |

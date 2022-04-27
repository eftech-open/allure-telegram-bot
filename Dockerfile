FROM python:3.9.12-buster

# Update recommends
RUN apt update && apt install --no-install-recommends -y curl build-essential

# Python configuration
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.1.3
ENV PATH="/root/.poetry/bin:$PATH"

# Bot configuration
ENV ALLURE_PROJECT "127.0.0.1"
ENV ALLURE_URL "http://127.0.0.1"
ENV ALLURE_USER_TOKEN ""
ENV BOT_TOKEN ""
ENV MONGO_HOST "127.0.0.1"
ENV MONGO_PORT 27017
ENV MONGO_DATABASE "allure_bot"
ENV REPORT_INTERVAL "360"
ENV REPORT_TIMEDELTA "60"
ENV REPORT_CHART_PATH "./tmp/"
ENV REPORT_CRITICAL_PERCENT "50"
ENV TIMEZONE "MSK"
ENV CLEAR_DB_LAUNCHES "True"
ENV CLEAR_DATE_TMP "59 23 */2 * *"

# Package manager setup
COPY poetry.lock pyproject.toml /
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
RUN poetry config virtualenvs.create false && poetry install

# Bot setup
COPY . ./notification_bot
WORKDIR /notification_bot

ENTRYPOINT [ "python3", "bot.py"]

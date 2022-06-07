FROM python:3.9.13-slim

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

# Package manager setup
COPY poetry.lock pyproject.toml /
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
RUN poetry config virtualenvs.create false && poetry install

# Bot setup
COPY . ./allure_telegram_bot
WORKDIR /allure_telegram_bot

ENTRYPOINT [ "python3", "bot.py"]

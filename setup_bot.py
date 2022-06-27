from os import path
from click import command, echo, option, STRING, INT


@command()
@option("--allure_url", prompt="Allure TestOps URL", type=STRING, help='URL like https://<url>')
@option("--allure_project", prompt="Allure TestOps project ID", type=INT, help='Project ID')
@option("--allure_user_token", prompt="Allure TestOps user token", type=STRING, help='User API-token')
@option("--bot_token", prompt="Bot token", type=STRING, help='Issued by BotFather')
@option("--mongo_host", prompt="Mongo host", default='mongo_db', type=STRING,
        help='IP address or container name, default \'mongo_db\'')
@option("--mongo_port", prompt="Mongo port", default=27017, type=INT, help='Database port, default \'27017\'')
@option("--mongo_database", prompt="Mongo database", default='allure_bot', type=STRING,
        help='Database name, default \'allure_bot\'')
def generate_env_file(allure_project, allure_url, allure_user_token, bot_token, mongo_host, mongo_port,
                      mongo_database):
    """
    Generates environment file with variables
    """

    echo("Setting environment parameters for the bot")

    def allure_parameters(project, url, user_token):
        return "# Allure TestOps\n" \
               f'ALLURE_PROJECT="{project}"\n' \
               f'ALLURE_URL="{url}"\n' \
               f'ALLURE_USER_TOKEN="{user_token}"\n\n'

    def bot_parameters(token):
        return '# Bot\n' \
               f'BOT_TOKEN="{token}"\n\n'

    def mongo_parameters(host, port, database):
        return '# DataBase\n' \
               f'MONGO_HOST="{host}"\n' \
               f'MONGO_PORT="{port}"\n' \
               f'MONGO_DATABASE="{database}"\n\n'

    def report_parameters():
        return '# Report settings\n' \
               f'REPORT_INTERVAL="20"\n' \
               f'REPORT_TIMEDELTA="200"\n' \
               f'REPORT_CHART_PATH="./tmp/"\n' \
               f'REPORT_CRITICAL_PERCENT="50"\n\n'

    def rest_parameters():
        return '# Rest settings\n' \
               f'TIMEZONE="UTC"\n' \
               f'CLEAR_DB_LAUNCHES="True"\n' \
               f'CLEAR_DATE_TMP="59 23 */5 * *"\n'

    allure = allure_parameters(allure_project, allure_url, allure_user_token)
    bot = bot_parameters(bot_token)
    mongo = mongo_parameters(mongo_host, mongo_port, mongo_database)
    report = report_parameters()
    rest = rest_parameters()

    with open(".env", "w") as f:
        f.writelines([allure, bot, mongo, report, rest])

    echo(f"Environment file has been generated and stored in '{path.abspath(path.dirname(__file__))}/.env'")


if __name__ == "__main__":
    generate_env_file()

from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler
import command_names as cnames
import controller
import logger
import os

__TOKEN_FILE_PATH = '.token'


def read_token() -> str:
    if os.path.isfile(__TOKEN_FILE_PATH):
        try:
            with open(__TOKEN_FILE_PATH, 'r') as file:
                data = file.read().strip()
                if len(data) == 0:
                    return
                return data
        except OSError:
            return
    else:
        try:
            with open(__TOKEN_FILE_PATH, 'w') as _:
                pass
        except OSError:
            pass


tg_token = read_token()
if tg_token is None:
    print(f"! ОШИБКА: Не удалось прочитать токен из файла {__TOKEN_FILE_PATH}")
    exit()


app = ApplicationBuilder().token(tg_token).build()

app.add_handler(CommandHandler(cnames.START_CMD[1:], controller.start))
app.add_handler(CommandHandler(cnames.MENU_CMD[1:], controller.menu))
app.add_handler(CommandHandler(cnames.TIME_CMD[1:], controller.time))
app.add_handler(CommandHandler(cnames.GAME_CMD[1:], controller.game))
app.add_handler(CommandHandler(cnames.SURRENDER_CMD[1:], controller.surrender))
app.add_handler(CommandHandler(cnames.WHO_CMD[1:], controller.who))
app.add_handler(CommandHandler(cnames.SCORE_CMD[1:], controller.score))
app.add_handler(CommandHandler('error', controller.error))

answers_filter = controller.get_user_answers_filter()
app.add_handler(MessageHandler(answers_filter, controller.process_user_answer))

logger.start_logging()
app.run_polling()
logger.stop_logging()

from datetime import datetime
import inspect
from sys import stderr
from telegram import Update
import os

LOG_PATH = 'logs/'
LOG_FILENAME_BLANK = 'log-{}.csv'

log_file = None


def start_logging(console_out=True):
    global log_file
    if log_file:
        return

    if not os.path.exists(LOG_PATH):
        os.makedirs(LOG_PATH)

    today_date_str = datetime.now().strftime('%Y-%m-%d')
    log_file_path = LOG_FILENAME_BLANK.format(today_date_str)
    log_file_path = os.path.join(LOG_PATH, log_file_path)

    try:
        log_msg = f'\n{datetime.now().strftime("%H:%M:%S")};\tSTART LOGGING\n'
        log_file = open(log_file_path, 'a')
        log_file.write(log_msg)
        if console_out:
            print(log_msg)
    except OSError:
        log_file = None
        print('Ошибка: Не удалось запустить логирование!', file=stderr)


def stop_logging(console_out=True):
    global log_file
    if log_file:
        log_msg = f'\n{datetime.now().strftime("%H:%M:%S")};\tSTOP LOGGING\n'
        log_file.write(log_msg)
        log_file.close()
        log_file = None
        if console_out:
            print(log_msg)


def log(update: Update, error_msg=None, console_out=True) -> None:
    global log_file
    if log_file is None:
        return

    caller_name = inspect.stack()[1].function
    log_data = []
    log_data.append(datetime.now().strftime("%H:%M:%S"))
    log_data.append(update.effective_user.id)
    log_data.append(update.effective_user.full_name)
    log_data.append(caller_name.upper())
    log_data.append(update.message.text)
    if error_msg:
        log_data.append('ERROR: ' + error_msg)

    log_msg = ';\t'.join(map(str, log_data))
    log_file.write(log_msg + '\n')
    log_file.flush()
    if console_out:
        print(log_msg)


def _test():
    print(datetime.now().strftime('%Y-%m-%d'))
    print('☻️'.encode('unicode_escape'))
    # print(ord(u"☻️"))
    print('\u263b\ufe0f')
    # start_logging()
    # stop_logging()


if __name__ == "__main__":
    _test()

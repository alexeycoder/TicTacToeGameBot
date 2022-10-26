from datetime import datetime
import random
from entities.cell_state import CellState
from telegram.helpers import escape_markdown
from renderer import DeskRenderer as dr
import command_names as cnames

__SMILEY = '\u263b\ufe0f'


__HELLO_MSG = 'Привет, {}. Я бот Бусинка ' + __SMILEY + \
    ', небинарная персона. Приятно познакомиться!\n' \
    'Хочешь сыграть со мной в крестики-нолики?' \
    ' Разумеется хочешь, иначе и быть не может! \U0001F924' \
    ' Чтобы начать игру набери команду\n' \
    f'{cnames.GAME_CMD} (\U0001F448 или нажми на неё)'

__HELLO_EXISTING_USER_MSG = 'Привет, {}. Чё как! ' + __SMILEY + \
    '\nЗахочешь сыграть \u2014 командуй ' + cnames.GAME_CMD + \
    '\nЖду с нетерпением...'

__MENU_MSG = 'Доступные команды:' \
    f'\n{cnames.MENU_CMD} \u2014 посмотреть данный список команд;' \
    f'\n{cnames.WHO_CMD} \u2014 показать пользователей онлайн;' \
    f'\n{cnames.SCORE_CMD} \u2014 узнать игровой счёт;' \
    f'\n{cnames.TIME_CMD} \u2014 узнать текущее время;' \
    f'\n{cnames.GAME_CMD} \u2014 начать игру;' \
    f'\n{cnames.SURRENDER_CMD} \u2014 прервать игру, \u2014 будет засчитано поражение.'

__GAME_STARTED_MSG = '\U0001F3C1 Начинаем игру. Ура! \U0001F3C1'

__USER_WIN_COMMENTS = ['Хотя мне кажется не обошлось без мухлежа с твоей стороны \U0001F914',
                       'Сегодня просто высокое атмосферное давление \U0001F486, поэтому не могу сказать что твоя победа была честной.',
                       'Не обольщайся. Просто всю игру меня отвлекали телефонные мошенники \U0001F47F А может это твоих рук дело?',
                       'От такого количества чая всю игру приходилось бегать в туалет \U0001F63E Тут уж было не до победы \U0001F648',
                       'Я совсем даже не переживаю. Зато по поеданию креветок \U0001F364 мне нет равных!']

__AI_TURN_COMMENTS = ['И это самый шикарный ход за игру! Осталось сдобрить его бокалом шампанского \U0001F942',
                      'Это чудесный ход. Не печалься, такое мастерство приходит не сразу \U0001F393, если вообще приходит...',
                      'И нет сомнения, что это лучший ход, ведь не зря же Луна сегодня в нужной фазе \U0001F31B',
                      'Удивительно, насколько гениальные ходы мне удаётся делать \U0001F525']

__USER_TURN_COMMENTS = ['\U0001F610 Такс такс такс... \U0001F6AC',
                        '\U0001F611 Не уверены что так можно, но ладно... \U0001F927',
                        '\U0001F639 Это чо! Кто так ходит, тебе не нужна победа?! Да ну ладно... ',
                        'Тебе раньше никто не говорил про твои странности. Вот этот ход щас был очень странным \U0001F9D0',
                        'Зачем так давить кнопку, мы же не на ринге \U0001F93C Расслабься, это всего лишь игра.']

__ESC_EXCL = escape_markdown('!', version=2)
__ESC_DOT = escape_markdown('.', version=2)
__ESC_HYPH = escape_markdown('-', version=2)


def to_md_compatible(text: str) -> str:
    return text.replace('!', __ESC_EXCL) \
        .replace('.', __ESC_DOT) \
        .replace('-', __ESC_HYPH)


def get_users_online_view_md(names_lst):
    def to_raw_md_repr(txt):
        return escape_markdown(txt, version=2)

    md_names_lst = list(map(to_raw_md_repr, names_lst))

    view_md = '_Игроки онлайн:_\n'
    if len(md_names_lst) > 0:
        view_md += '\U0001F633 '
    view_md += '\n\U0001F633 '.join(md_names_lst)
    view_md += '\n... _а вообще шпийонить нехорошо_ \U0001F607'

    return to_md_compatible(view_md)


def get_desk_view_md(desk):
    return to_md_compatible('```\n' + dr.get_representation(desk) + '```')


def get_menu_view_txt() -> str:
    return __MENU_MSG


def get_start_view_txt(user_name, new_user=True) -> str:
    if new_user:
        return __HELLO_MSG.format(user_name) + '\n\n' + get_menu_view_txt()
    else:
        return __HELLO_EXISTING_USER_MSG.format(user_name) \
            + '\n\nНапоминаю, что ты можешь использовать\n' \
            + get_menu_view_txt()


def get_current_time_view_md(time: datetime) -> str:
    return to_md_compatible(f'\u23F3 Текущее время: *{time.strftime("%H:%M:%S")} МСК*')


def get_unfinished_game_notice(user_name):
    return f'{user_name}, как же так,' \
        ' у нас осталась незавершённая игра.' \
        ' Продолжаем!..'


def get_score_view_md(wins: int, loss: int, total: int) -> str:
    view_md = '__Твой текущий счёт:__\n'

    if total <= 0:
        view_md += 'Мы пока-ещё не играли вместе \U0001F62D'
    else:
        view_md += f'_Всего сыграно игр:_ *{total}*\n' \
            f'_Выиграно:_ *{wins}*\n' \
            f'_Проиграно:_ *{loss}*\n'
        if wins > loss:
            view_md += 'Ништяк! \U0001F44D \U0001F46F'
        else:
            view_md += 'Ахаха! \U0001F479 Старайся лучше \U0001F393\U0001F485'

    return to_md_compatible(view_md)


def get_lets_start_view_txt() -> str:
    return __GAME_STARTED_MSG


def get_toss_result_view_md(user_mark: CellState) -> str:
    view_md = '_Жеребъёвка первого хода:_\n'

    if user_mark == CellState.X:
        view_md += 'Тебе выпали *крестики*, а значит и право первого хода.\n' \
            f'Ну и ладно, мне более идут круглые формы {__SMILEY},' \
            ' так что нолики \u2014 моя тема. Я обязательно выиграю!'
    else:
        view_md += f'Тебе выпали *нолики*, и право первого хода достаётся мне {__SMILEY}\n' \
            'Что ты дуешься, как нолик. Таков результат честной жеребьёвки. Ты же мне веришь?!'

    return to_md_compatible(view_md)


def get_ai_turn_info_view_md(cell_index: int) -> str:
    view_md = f'Мной сделан ход в ячейку нумер *{cell_index+1}* \U0001F92B\n'
    view_md += random.choice(__AI_TURN_COMMENTS)

    return to_md_compatible(view_md)


def get_user_turn_info_view_md() -> str:
    view_md = random.choice(__USER_TURN_COMMENTS)
    return to_md_compatible(view_md)


def get_keyboard_matrix_view(desk: list[CellState]) -> list[list[str]]:
    def cell_state_repr(cell_state: CellState, cell_index: int):
        if cell_state == CellState.EMPTY:
            return str(cell_index+1)
        elif cell_state == CellState.O:
            return dr.O_SYMBOL
        else:
            return dr.X_SYMBOL

    desk_str_repr = list(map(cell_state_repr, desk, range(9)))
    keyboard_matrix = [desk_str_repr[:3],
                       desk_str_repr[3:6],
                       desk_str_repr[6:]]
    return keyboard_matrix


def __mark_to_sign_name_pl(mark: CellState):
    return 'Нолики' if mark == CellState.O else 'Крестики'


def get_user_turn_prompt_view_txt(user_mark: CellState):
    user_sign_name = __mark_to_sign_name_pl(user_mark)
    view_txt = f'{user_sign_name}, твоя очередь! Ждёмс... \U0001F9D0' \
        f'\nНапоминаю: ты всегда можешь сдаться \U0001F449 {cnames.SURRENDER_CMD}'
    return view_txt


def get_congratulations_view_md(winner_mark: CellState, ai_wins=True, user_wins=False) -> str:
    sign_name = __mark_to_sign_name_pl(winner_mark)
    view_md = '__Игра окончена__\n'
    if ai_wins:
        view_md += f'{__SMILEY} Победили {sign_name}, ура-ура! \U0001F37E \U0001F389' \
            + 'Разве кто-то ожидал иного исхода. Конечно же победа за мной! \U0001F607'
    elif user_wins:
        view_md += f'{__SMILEY} Победили {sign_name}. Поздравляю с победой. Нате грамоту \U0001F4C3\n'
        view_md += random.choice(__USER_WIN_COMMENTS)
    else:
        view_md += 'Ничья! \U0001F91D Считай, тебе крупно повезло! \U0001F916'

    view_md += f'\n\U0001F4DC {cnames.MENU_CMD} \U0001F448'

    return to_md_compatible(view_md)


def get_generic_error_view_txt() -> str:
    return '\u2757 Произошла ошибка. Пожалуйста обратитесь к администратору.' \
        f' Я {__SMILEY} тут совершенно ни при чём \U0001F47E'

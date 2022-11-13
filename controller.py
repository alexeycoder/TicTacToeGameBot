from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, filters
from entities.game_stage import GameStage
from renderer import DeskRenderer as dr
import command_names as cnames
import logger
import view
import model


def get_user_answers_filter():
    allowed_answers_lst = [str(i+1) for i in range(9)] + \
        [dr.O_SYMBOL, dr.X_SYMBOL]
    allowed_answers_str = '|'.join(allowed_answers_lst)
    return filters.Regex(f"^({allowed_answers_str})$")


async def notify_user_on_error(update: Update, context: ContextTypes.DEFAULT_TYPE, error_msg) -> None:
    logger.log(update)
    await update.message.reply_text(error_msg)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await notify_user_on_error(update, context, view.get_generic_error_view_txt())


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.log(update)
    telegram_user = update.message.from_user
    is_new = model.is_new_user(telegram_user.id)
    if is_new:
        model.add_new_user(telegram_user.id, telegram_user.full_name)
    else:
        model.update_user_activity(telegram_user.id)

    view_txt = view.get_start_view_txt(telegram_user.first_name, is_new)
    await update.message.reply_text(view_txt)


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.log(update)
    view_txt = view.get_menu_view_txt()
    await update.message.reply_text(view_txt)


async def time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.log(update)
    view_md = view.get_current_time_view_md(datetime.now())
    await update.message.reply_markdown_v2(view_md)


async def score(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.log(update)
    uid = update.effective_user.id
    if model.is_new_user(uid):
        await update.message.reply_text(f'Очевидно что мы ещё не играли.\n'
                                        f'Чтобы познакомиться, используй команду {cnames.START_CMD} \U0001F448')
        return

    score = model.get_user_score(uid)
    score_view_md = view.get_score_view_md(*score)
    await update.message.reply_markdown_v2(score_view_md)


async def game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.log(update)
    telegram_user = update.effective_user
    uid = telegram_user.id
    if model.is_new_user(uid):
        model.add_new_user(uid, telegram_user.full_name)

    game_stage = model.get_user_game_stage(uid)
    if game_stage != GameStage.NOT_STARTED and game_stage != GameStage.GAME_OVER:
        uname = update.effective_user.first_name
        await update.message.reply_text(view.get_unfinished_game_notice(uname))
        await auto_turn(update, context)
        return

    user_mark = model.toss_whos_first(uid)

    # score = model.get_user_score(uid)
    # score_view_md = view.get_score_view_md(*score)
    # await update.message.reply_markdown_v2(score_view_md)
    await update.message.reply_text(view.get_lets_start_view_txt())
    await update.message.reply_markdown_v2(view.get_toss_result_view_md(user_mark))

    # если пользователь ходит первым, то надо явно показать исходное пустое поле
    if model.get_user_game_stage(uid) == GameStage.USER_TURN:
        desk = model.get_user_game_desk(uid)
        await update.message.reply_markdown_v2(view.get_desk_view_md(desk))

    await auto_turn(update, context)


async def auto_turn(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = update.effective_user.id

    # non-recognized users are not allowed here:
    if model.is_new_user(uid):
        logger.log(
            update, context, error_msg=f'Возможная уязвимость: Позьзователь {uid} оказался в {auto_turn.__name__} минуя обязятельные стадии.')
        await start(update, context)
        return

    game_stage = model.get_user_game_stage(uid)
    if game_stage == GameStage.AI_TURN:
        await _ai_turn(update, context)
    elif game_stage == GameStage.USER_TURN:
        await _user_turn(update, context)
    elif game_stage == GameStage.GAME_OVER:
        await _game_over(update, context)


async def _ai_turn(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.log(update)
    uid = update.effective_user.id
    chosen_cell_index = model.do_ai_turn(uid)
    desk = model.get_user_game_desk(uid)
    await update.message.reply_markdown_v2(view.get_desk_view_md(desk))
    await update.message.reply_markdown_v2(view.get_ai_turn_info_view_md(chosen_cell_index))

    await auto_turn(update, context)


async def _user_turn(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.log(update)
    uid = update.effective_user.id
    mark = model.get_user_game_mark(uid)
    desk = model.get_user_game_desk(uid)
    prompt_view_txt = view.get_user_turn_prompt_view_txt(mark)
    reply_keyboard = view.get_keyboard_matrix_view(desk)
    await update.message.reply_text(
        prompt_view_txt,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, resize_keyboard=True, one_time_keyboard=True,
            input_field_placeholder="Твой ход (выбери номер свободной ячейки)?"),
    )


async def process_user_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.log(update)

    uid = update.effective_user.id
    if model.is_new_user(uid):
        await update.message.reply_text('\U0001F4DB Ноу-ноу. Стоп телега!'
                                        ' Прежде чем разбрасываться ходами надо познакомиться... \U0001F504',
                                        reply_markup=ReplyKeyboardRemove())
        await start(update, context)
        return

    if model.get_user_game_stage(uid) != GameStage.USER_TURN:
        await update.message.reply_text('\U0001F47F Чо такоэ! Кулхацкер?!\n'
                                        f'Жми {cnames.START_CMD} \U0001F448чтобы начать играть по правилам \U0001F63C',
                                        reply_markup=ReplyKeyboardRemove())
        return

    answer = update.message.text
    chosen_cell_index = model.get_cell_index_if_answer_valid(uid, answer)
    if chosen_cell_index is None:
        await update.message.reply_text('\U0001F608 Ай-яй-яй! Кому-то надо протереть пенсне и попробовать ещё разочек.'
                                        ' Выбирай незанятую ячейку! \U0001F63C',
                                        reply_markup=ReplyKeyboardRemove())
        await _user_turn(update, context)
        return

    model.do_user_turn(uid, chosen_cell_index)
    desk = model.get_user_game_desk(uid)
    await update.message.reply_markdown_v2(view.get_desk_view_md(desk), reply_markup=ReplyKeyboardRemove())

    if model.get_user_game_stage(uid) != GameStage.GAME_OVER:
        await update.message.reply_markdown_v2(view.get_user_turn_info_view_md())

    await auto_turn(update, context)


async def _game_over(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.log(update)

    uid = update.effective_user.id
    is_user_winner, winner_mark = model.last_winner_info(uid)
    is_ai_winner = is_user_winner is not None and not is_user_winner
    congrats_view_md = view.get_congratulations_view_md(
        winner_mark, ai_wins=is_ai_winner, user_wins=is_user_winner or False)
    model.reset_stage(uid)
    await update.message.reply_markdown_v2(congrats_view_md, reply_markup=ReplyKeyboardRemove())


async def surrender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.log(update)
    uid = update.effective_user.id

    if model.is_new_user(uid):
        await update.message.reply_text('\U0001F9DA Погоди сдаваться, мы ведь даже ещё не закомы... ')
        await start(update, context)
        return

    if model.user_surrenders(uid):
        await update.message.reply_text('То-то же! Сдаться \u2014 правильный выбор. Проигрыш засчитан \U0001F483'
                                        f'\n\U0001F4DC {cnames.SCORE_CMD} \U0001F448'
                                        f'\n\U0001F4DC {cnames.MENU_CMD} \U0001F448',
                                        reply_markup=ReplyKeyboardRemove())
    else:
        await update.message.reply_text(f'Ну ты штоо! Вот так прям сразу?'
                                        f' Мы же ещё даже не начали играть...\nЖми {cnames.GAME_CMD} \U0001F448')

    model.reset_stage(uid)


async def who(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    "Показывает список юзверей онлайн."
    logger.log(update)
    uid = update.effective_user.id
    if model.is_new_user(uid):
        await update.message.reply_text('Прежде чем подглядывать за другими, давай познакомимся...')
        await start(update, context)
        return

    model.update_user_activity(uid)

    names_lst = model.get_users_online()
    view_md = view.get_users_online_view_md(names_lst)
    await update.message.reply_markdown_v2(view_md)

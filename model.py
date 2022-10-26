import random
from entities.cell_state import CellState
from entities.game_stage import GameStage
from entities.user_game_state import UserGameState
from entities import game_desk


states: dict[int, UserGameState] = {}


def is_new_user(user_id: int) -> bool:
    return user_id not in states


def add_new_user(user_id: int, user_name: str):
    states[user_id] = UserGameState(user_id, user_name)


def _get_user_game_state(user_id: int) -> UserGameState:
    user_game_state = states.get(user_id)
    return user_game_state


def update_user_activity(user_id: int):
    user_game_state = _get_user_game_state(user_id)
    user_game_state._update_last_activity()


def get_user_game_mark(user_id: int):
    user_game_state = _get_user_game_state(user_id)
    return user_game_state.get_user_mark()


def get_user_game_desk(user_id: int):
    user_game_state = _get_user_game_state(user_id)
    return user_game_state.get_desk()


def get_user_game_stage(user_id: int):
    user_game_state = _get_user_game_state(user_id)
    return user_game_state.get_stage()


def get_user_score(user_id: int):
    user_game_state = _get_user_game_state(user_id)
    return user_game_state.get_score()


def __check_for_winner_and_handle(user_game_state: UserGameState):
    desk = user_game_state.get_desk()
    winner_tuple = game_desk.check_for_winner(desk)
    if winner_tuple:
        (winner_mark, _) = winner_tuple
        user_game_state.set_game_over(winner_mark)


def last_winner_info(user_id: int) -> tuple[(bool | None), CellState]:
    user_game_state = _get_user_game_state(user_id)
    is_user_winner = user_game_state.is_user_last_winner()
    winner_mark = user_game_state.get_last_winner_mark()
    return (is_user_winner, winner_mark)


def toss_whos_first(user_id: int) -> CellState:
    "Возвращает значок игрока-человека."
    user_game_state = _get_user_game_state(user_id)
    user_game_state.start_game()

    gamers_marks = (CellState.O, CellState.X)
    gamer_mark = random.choice(gamers_marks)
    user_game_state.set_user_mark(gamer_mark)
    if gamer_mark == CellState.X:
        user_game_state.set_user_turn()
    else:
        user_game_state.set_ai_turn()

    return user_game_state.get_user_mark()


def do_ai_turn(user_id: int) -> int:
    user_game_state = _get_user_game_state(user_id)

    user_game_state.set_ai_turn()

    ai_mark = user_game_state.get_ai_mark()
    desk = user_game_state.get_desk()
    chosen_index = game_desk.do_ai_turn(desk, ai_mark)

    user_game_state.set_user_turn()
    __check_for_winner_and_handle(user_game_state)

    return chosen_index


def user_surrenders(user_id: int) -> bool:
    user_game_state = _get_user_game_state(user_id)
    stages_alowed_to_surrender = (GameStage.AI_TURN,
                                  GameStage.USER_TURN,
                                  GameStage.TOSS)
    if user_game_state.get_stage() in stages_alowed_to_surrender:
        user_game_state.set_game_over(user_game_state.get_ai_mark())
        return True
    return False


def get_cell_index_if_answer_valid(user_id: int, user_answer: str) -> int:
    if not user_answer.isdigit():
        return
    try:
        cell_index = int(user_answer) - 1
        desk = get_user_game_desk(user_id)
        cell_value = desk[cell_index]
        if cell_value == CellState.EMPTY:
            return cell_index
    except ValueError:
        return


def do_user_turn(user_id: int, cell_index: int) -> int:
    user_game_state = _get_user_game_state(user_id)
    # stage must already be 'user turn' here, naturally
    # cell_index must already be valid here (existent and empty)
    user_mark = user_game_state.get_user_mark()
    desk = user_game_state.get_desk()
    desk[cell_index] = user_mark

    user_game_state.set_ai_turn()
    __check_for_winner_and_handle(user_game_state)

    return cell_index


def reset_stage(user_id):
    user_game_state = _get_user_game_state(user_id)
    user_game_state.reset_stage()


def get_users_online() -> list[str]:
    gamers_online = filter(lambda ugs: ugs.is_online(), states.values())
    names_lst = list(map(lambda ugs: ugs.user_name, gamers_online))
    return names_lst


def __do_tests():
    global states
    states = {123: UserGameState(123)}
    print(is_new_user(555))
    print(is_new_user(123))


if __name__ == "__main__":
    __do_tests()

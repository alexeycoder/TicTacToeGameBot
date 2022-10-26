from datetime import datetime
from entities.cell_state import CellState
from entities.game_stage import GameStage
from entities import game_desk


class UserGameState:
    MAX_TIMEOUT_SECONDS = 30 * 60

    def __init__(self, user_id, user_name) -> None:
        self.user_id = user_id
        self.user_name = user_name
        self._game_stage = GameStage.NOT_STARTED
        self._desk = game_desk.new_empty_desk()
        self._wins_count = 0
        self._loss_count = 0
        self._total_count = 0

        self._user_mark = None
        self._ai_mark = None

        self._last_winner_mark = None
        self._user_is_last_winner = None

        self._update_last_activity()

    def _update_last_activity(self):
        self._last_activity = datetime.now()

    def is_online(self):
        return (datetime.now()-self._last_activity).total_seconds() < UserGameState.MAX_TIMEOUT_SECONDS

    def get_desk(self) -> list[CellState]:
        self._update_last_activity()
        return self._desk

    def get_stage(self) -> GameStage:
        self._update_last_activity()
        return self._game_stage

    def start_game(self):
        self._update_last_activity()
        self._game_stage = GameStage.TOSS

    def set_user_mark(self, mark: CellState):
        if mark == CellState.EMPTY:
            raise ValueError('Ошибка: Следует назначить корректный значок.')
        self._user_mark = mark
        self._ai_mark = ({CellState.O, CellState.X} - {mark}).pop()

    def get_user_mark(self):
        return self._user_mark

    def get_ai_mark(self):
        return self._ai_mark

    def get_last_winner_mark(self):
        return self._last_winner_mark

    def is_user_last_winner(self):
        return self._user_is_last_winner

    def __make_sure_mark_is_valid(self):
        if self._user_mark is None:
            raise TypeError(
                'Ошибка: Значок игрока должен быть назначен до первого хода!')

    def set_ai_turn(self):
        self._update_last_activity()
        self.__make_sure_mark_is_valid()
        self._game_stage = GameStage.AI_TURN

    def set_user_turn(self):
        self._update_last_activity()
        self.__make_sure_mark_is_valid()
        self._game_stage = GameStage.USER_TURN

    def set_game_over(self, winner_mark):
        self._update_last_activity()

        self._total_count += 1
        self._last_winner_mark = winner_mark
        if winner_mark == self._user_mark:
            self._user_is_last_winner = True
            self._wins_count += 1
        elif winner_mark == self._ai_mark:
            self._loss_count += 1
            self._user_is_last_winner = False
        else:
            self._user_is_last_winner = None

        self._game_stage = GameStage.GAME_OVER

    def reset_stage(self):
        if self._game_stage == GameStage.GAME_OVER:
            self._game_stage = GameStage.NOT_STARTED
            self._desk = game_desk.new_empty_desk()

    def get_score(self) -> tuple[int, int, int]:
        return (self._wins_count, self._loss_count, self._total_count)

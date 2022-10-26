from enum import Enum


class GameStage(Enum):
    NOT_STARTED = 0
    TOSS = 1
    USER_TURN = 2
    AI_TURN = 3
    GAME_OVER = 4

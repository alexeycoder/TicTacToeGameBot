import random
from entities.cell_state import CellState


__DIM = 3

horizontals = tuple(tuple(range(__DIM*row, __DIM * (row+1)))
                    for row in range(__DIM))
verticals = tuple(tuple(range(col, col+__DIM*(__DIM-1)+1, __DIM))
                  for col in range(__DIM))
diag_main = tuple(i * __DIM+i for i in range(__DIM))
diag_minor = tuple(i for i in
                   range(__DIM-1, __DIM*(__DIM-1)+1, __DIM-1))

scanlines = horizontals + verticals + (diag_main, diag_minor)


def new_empty_desk():
    return [CellState.EMPTY] * (__DIM*__DIM)


def check_for_winner(desk) -> tuple[CellState, tuple[int]]:
    """Вернёт кортеж, если есть победитель либо ничья,
    в противном случае вернёт None
    """
    noone_can_win = True
    for scanline in scanlines:
        states = {desk[i] for i in scanline}
        if len(states - {CellState.EMPTY}) != 2:
            noone_can_win = False
        if len(states) == 1 and states != {CellState.EMPTY}:
            winner = list(states)[0]
            return (winner, scanline)

    if noone_can_win or desk.count(CellState.EMPTY) == 0:
        return (CellState.EMPTY, None)

    return


def do_ai_turn_stupid(desk, ai_mark) -> int:
    empty_cells_indexes = [i for i, v in
                           enumerate(desk) if v == CellState.EMPTY]

    chosen_index = random.choice(empty_cells_indexes)
    desk[chosen_index] = ai_mark
    return chosen_index


def __get_empty_indices_of_max_filled_line(desk, cell_state: CellState):
    # ищем те пересечения, где заполнено по максимуму только одним значком,
    # но при этом есть хотя бы одна пустая ячейка
    # возвращаем индексы для найденных пустот (подойдёт и для полей > 3x3)

    max_filled_cells = 0
    found_line = None
    for scanline in scanlines:
        scanline_values = [desk[idx] for idx in scanline]

        scanline_values_set = set(scanline_values)
        if len(scanline_values_set) != 2:
            continue

        empty_count = scanline_values.count(CellState.EMPTY)
        if empty_count == 0:
            continue

        filled_count = scanline_values.count(cell_state)
        if filled_count > max_filled_cells:
            max_filled_cells = filled_count
            found_line = scanline

    if found_line is None:
        return

    empty_cells_indices = [i for i in found_line if desk[i] == CellState.EMPTY]
    return empty_cells_indices


def do_ai_turn(desk, ai_mark: CellState) -> int:
    user_mark = ({CellState.O, CellState.X}-{ai_mark}).pop()

    ai_empty_indices = __get_empty_indices_of_max_filled_line(desk, ai_mark)
    user_empty_indices = __get_empty_indices_of_max_filled_line(
        desk, user_mark)

    ai_weight = -1 if ai_empty_indices is None else len(ai_empty_indices)
    user_weight = -1 if user_empty_indices is None else len(user_empty_indices)

    if ai_weight == 1:  # just one step to win
        i = ai_empty_indices[0]
        desk[i] = ai_mark
        return i

    preferable_indices = ai_empty_indices if ai_weight < user_weight else user_empty_indices

    if preferable_indices is None:
        preferable_indices = [i for i, v in
                              enumerate(desk) if v == CellState.EMPTY]

    i = random.choice(preferable_indices)
    desk[i] = ai_mark
    return i

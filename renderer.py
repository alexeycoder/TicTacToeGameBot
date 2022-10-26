from entities.cell_state import CellState

# class TableSymb:
#     HORIZ = '\u2550'
#     VERT = '\u2551'

#     TOP_LEFT = '\u2554'
#     TOP_RIGHT = '\u2557'
#     TOP_TO_VERT = '\u2566'

#     BTM_LEFT = '\u255a'
#     BTM_RIGHT = '\u255d'
#     BTM_TO_VERT = '\u2569'

#     LEFT_TO_HORIZ = '\u2560'
#     RIGHT_TO_HORIZ = '\u2563'

#     CROSS = '\u256c'


class TableSymb:
    HORIZ = '\u2500'
    VERT = '\u2502'

    TOP_LEFT = '\u250c'
    TOP_RIGHT = '\u2510'
    TOP_TO_VERT = '\u252c'

    BTM_LEFT = '\u2514'
    BTM_RIGHT = '\u2518'
    BTM_TO_VERT = '\u2534'

    LEFT_TO_HORIZ = '\u251c'
    RIGHT_TO_HORIZ = '\u2524'

    CROSS = '\u253c'


__test_desk = [CellState.EMPTY for _ in range(3 * 3)]
__test_desk[0] = CellState.X
__test_desk[4] = CellState.X
__test_desk[8] = CellState.X
__test_desk[2] = CellState.O
__test_desk[6] = CellState.O


class DeskRenderer:
    X_SYMBOL = 'X'
    O_SYMBOL = 'O'
    __CELL_PADDING = 1

    __SPACE_HEAVY = '\u2591'
    __SPACE_EMPTY = '\u2504'

    __test_desk = [CellState.EMPTY for _ in range(3 * 3)]

    def __init__(self) -> None:
        DeskRenderer.__test_desk[0] = CellState.X
        DeskRenderer.__test_desk[4] = CellState.X
        DeskRenderer.__test_desk[8] = CellState.X
        DeskRenderer.__test_desk[2] = CellState.O
        DeskRenderer.__test_desk[6] = CellState.O

    @ staticmethod
    def __get_cell_string(cell_value, cell_number, h_size, placeholder_mode=False):

        # cell_value = desk[index]
        cell_string = ' ' * h_size
        if cell_value == CellState.EMPTY:
            if not placeholder_mode:
                cell_string = str(cell_number).center(
                    h_size, DeskRenderer.__SPACE_EMPTY)
        else:
            # gamer_idx = cell_value.value
            if not placeholder_mode:
                cell_string = DeskRenderer.X_SYMBOL.center(h_size, DeskRenderer.__SPACE_HEAVY) \
                    if cell_value == CellState.X \
                    else DeskRenderer.O_SYMBOL.center(h_size, DeskRenderer.__SPACE_HEAVY)
                cell_string = cell_string

        return cell_string

    @ staticmethod
    def __print_row(desk: list[CellState], dim, index_from, cell_h_size):

        mids_plus_one = dim - 1
        hoziz_line = TableSymb.HORIZ * cell_h_size

        value_line = TableSymb.VERT
        for i in range(index_from, index_from + dim):
            cell_value = desk[i]
            value_line += DeskRenderer.__get_cell_string(cell_value, i+1, cell_h_size) \
                + TableSymb.VERT

        placeholder_line = TableSymb.VERT
        for i in range(index_from, index_from + dim):
            cell_value = desk[i]
            placeholder_line += DeskRenderer.__get_cell_string(cell_value, i+1, cell_h_size, True) \
                + TableSymb.VERT

        upper_frame = ''
        bottom_frame = ''
        if index_from == 0:
            upper_frame = TableSymb.TOP_LEFT + hoziz_line \
                + mids_plus_one * (TableSymb.TOP_TO_VERT + hoziz_line) \
                + TableSymb.TOP_RIGHT
        else:
            upper_frame = TableSymb.LEFT_TO_HORIZ + hoziz_line \
                + mids_plus_one * (TableSymb.CROSS + hoziz_line) \
                + TableSymb.RIGHT_TO_HORIZ

            if index_from == dim*(dim-1):
                bottom_frame = TableSymb.BTM_LEFT + hoziz_line \
                    + mids_plus_one * (TableSymb.BTM_TO_VERT + hoziz_line) \
                    + TableSymb.BTM_RIGHT

        new_line = '\n'

        row_repr = upper_frame + \
            new_line + value_line
        # row_repr = upper_frame + \
        #     new_line + placeholder_line + \
        #     new_line + value_line + \
        #     new_line + placeholder_line
        if bottom_frame != '':
            row_repr += new_line + bottom_frame

        return row_repr

    @ staticmethod
    def get_representation(desk: list[CellState] = None):
        if desk is None:
            desk = DeskRenderer.__test_desk

        cells_count = len(desk)
        dim = round(cells_count**0.5)

        last_cell_number = cells_count
        cell_h_size = len(str(last_cell_number))+2*DeskRenderer.__CELL_PADDING
        if cell_h_size % 2 == 0:
            cell_h_size -= 1

        new_line = '\n'
        desk_repr = ''
        for row_index in range(dim):
            cell_index_from = row_index * dim
            desk_repr += DeskRenderer.__print_row(
                desk, dim, cell_index_from, cell_h_size) + new_line

        return desk_repr  # .replace(' ', DeskRenderer.__SPACE)


desk_rendered = DeskRenderer()

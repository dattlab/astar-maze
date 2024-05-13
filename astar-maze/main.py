from maze_generator import Maze, Agent, COLOR
from queue import PriorityQueue


def a_star(input_maze):
    start_pos = (input_maze.rows, input_maze.cols)

    # Make the g(n) for every cell infinity
    g_score = {cell: float("inf") for cell in input_maze.grid}
    g_score[start_pos] = 0

    # Make the f(n) for every cell infinity temporarily
    f_score = {cell: float("inf") for cell in input_maze.grid}
    # f(start) = h(start) + g(start) = h(start) + 0
    f_score[start_pos] = h(start_pos, (1, 1))

    _open = PriorityQueue()
    # First entry in the Priority Queue is the starting cell
    # f(n), h(n), (x, y)
    _open.put((h(start_pos, (1, 1)), h(start_pos, (1, 1)), start_pos))

    astar_path = {}
    search_path = [start_pos]
    while not _open.empty():
        curr_cell = _open.get()[2]  # get the coordinates of the first entry in prio queue
        search_path.append(curr_cell)

        if curr_cell == (1, 1):
            # end the loop when the current cell is the goal
            break

        # else, explore all available neighbors
        for direction in "ESNW":
            # if the cell in direction d is open
            if input_maze.maze_map[curr_cell][direction] == True:
                if direction == "E": child_cell = (curr_cell[0], curr_cell[1] + 1)
                if direction == "W": child_cell = (curr_cell[0], curr_cell[1] - 1)
                if direction == "N": child_cell = (curr_cell[0] - 1, curr_cell[1])
                if direction == "S": child_cell = (curr_cell[0] + 1, curr_cell[1])

                # get the f(n) of child cell
                temp_g_score = g_score[curr_cell] + 1
                temp_f_score = temp_g_score + h(child_cell, (1, 1))

                # substitute the computed f(n) from the current f(n) of
                # child cell (which is infinity) if it is lower
                if temp_f_score < f_score[child_cell]:
                    g_score[child_cell] = temp_g_score
                    f_score[child_cell] = temp_f_score
                    _open.put(
                        ((temp_f_score, h(child_cell, (1, 1)), child_cell))
                    )

                    # make the child cell the current cell
                    astar_path[child_cell] = curr_cell

    forward_path = {}
    cell = (1, 1)
    while cell != start_pos:
        forward_path[astar_path[cell]] = cell
        cell = astar_path[cell]

    return search_path, forward_path


def h(c1, c2):
    """Returns the Manhattan distance between
       cell 1 and cell 2, making it the value
       of the heuristics"""
    x1, y1 = c1
    x2, y2 = c2

    return abs(x1 - x2) + abs(y1 - y2)


def print_path(_path, is_search=False):
    if is_search:
        _path = _path[1:]
    for coord in _path:
        print(f"-> {coord}")
    print()


def main() -> None:
    m = Maze(8, 8)
    m.create_maze(load_maze="../sample_map.csv")

    search_path, forward_path = a_star(m)

    search_agent = Agent(m, footprints=True, filled=True)
    forward_agent = Agent(m, footprints=True, color=COLOR.red)

    print("SEARCH PATH: ")
    print_path(search_path, True)

    print("FORWARD PATH: ")
    print_path(forward_path)

    m.trace_path({search_agent: search_path}, delay=200)
    m.trace_path({forward_agent: forward_path}, delay=200)

    m.run()


if __name__ == "__main__":
    main()

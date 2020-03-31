class Cell:
    """
    Object represents a cell on the game board.
    It contains:
    -a position variable, representing its indices.
    -a neighbours variable representing neighbouring cells
    -a has_peg variable, denoting if it is filled or not
    """

    def __init__(self, i, j, has_peg):
        self.position = (i, j)
        #either none (0), player 1 or player 2 peg
        self.has_peg = has_peg
        self.neighbours = {}


    def __repr__(self):
        return str(self.position[0]) + "-" + str(self.position[1])


class DiamondCell(Cell):

    def __init__(self, i, j, has_peg=0):
        super().__init__(i, j, has_peg)

    def add_neighbours(self, board):
        """
        Creates neighbour relationships for diamond board cells as described in hex-board-games.pdf
        """
        i,j = self.position
        if j - 1 >= 0:
            self.neighbours[(0,-1)] = board[i][j-1]
        if j + 1 < len(board[i]):
            self.neighbours[(0,1)] = board[i][j+1]
        if i - 1 >=0:
            self.neighbours[(-1, 0)] = board[i-1][j]
            if len(board[i]) > j+1:
                self.neighbours[(-1, 1)] = board[i-1][j+1]
        if i + 1 < len(board):
            self.neighbours[(1,0)] = board[i+1][j]
            if j - 1 >= 0:
                self.neighbours[(1,-1)] = board[i+1][j-1]

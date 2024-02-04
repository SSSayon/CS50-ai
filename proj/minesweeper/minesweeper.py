import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if self.count == len(self.cells):
            return self.cells
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        self.cells.discard(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def infer(self) -> bool:
        print("infer")
        new_knowledges = []
        old_knowledges = []
        for i in range(len(self.knowledge)):
            for j in range(i + 1, len(self.knowledge)):

                flag = False
                ii, jj = 0, 0
                if self.knowledge[i].cells > self.knowledge[j].cells:
                    ii, jj = i, j
                    flag = True
                elif self.knowledge[j].cells > self.knowledge[i].cells:
                    ii, jj = j, i
                    flag = True
                if not flag:
                    continue
                
                new_knowledge = Sentence(self.knowledge[ii].cells - self.knowledge[jj].cells, 
                                            self.knowledge[ii].count - self.knowledge[jj].count)
                
                old_knowledges.append(self.knowledge[ii])
                if new_knowledge not in self.knowledge and new_knowledge not in new_knowledges:
                    new_knowledges.append(new_knowledge)

        for old_knowledge in old_knowledges:
            while old_knowledge in self.knowledge:
                self.knowledge.remove(old_knowledge)
        if not new_knowledges:
            return False
        for new_knowledge in new_knowledges:
            self.knowledge.append(new_knowledge)

        return True
        
    def conclude(self) -> bool:
        print("conclude")
        new_mines = set()
        new_safes = set()
        used_knowledge = []
        for sentence in self.knowledge:
            if sentence.known_mines():
                new_mines |= sentence.known_mines()
                used_knowledge.append(sentence)
            if sentence.known_safes():
                new_safes |= sentence.known_safes()
                used_knowledge.append(sentence)

        if not new_mines and not new_safes:
            return False

        for sentence in used_knowledge:
            while sentence in self.knowledge:
                self.knowledge.remove(sentence)
        for mine in new_mines:
            self.mark_mine(mine)
        for safe in new_safes:
            self.mark_safe(safe)

        return True

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        self.moves_made.add(cell)
        self.mark_safe(cell)

        x, y = cell
        nbrs = set()
        for i in range(-1, 2):
            for j in range(-1, 2):
                if x + i < 0 or x + i >= self.height or y + j < 0 or y + j >= self.width or (i == 0 and j == 0):
                    continue
                nbrs.add((x + i, y + j))
        nbrs = nbrs - self.safes
        num_mines = count - len(nbrs & self.mines)
        nbrs = nbrs - self.mines
        if num_mines == len(nbrs):  # ---
            self.mines |= nbrs        # |
            for mine in nbrs:         # | 
                self.mark_mine(mine)  #  \ conclude
        elif num_mines == 0:          #  / in advance
            self.safes |= nbrs        # |
            for safe in nbrs:         # |
                self.mark_safe(safe)  # -
        else:
            self.knowledge.append(Sentence(nbrs, num_mines))

        while any([self.infer(), self.conclude()]):
            pass

        # self.debug()
        # print("-----------------------")

    # def debug(self):
    #     for sentence in self.knowledge:
    #         print(f"{sentence.cells} = {sentence.count}")

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        # print("-----------------------")
        # self.debug()
        safe_moves = self.safes - self.moves_made
        if not safe_moves:
            return None
        return safe_moves.pop()

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        # print("-----------------------")
        # self.debug()
        all_cells = set([(i, j) for i in range(self.height) for j in range(self.width)])
        random_moves = all_cells - self.moves_made - self.mines
        if not random_moves:
            return None
        return random_moves.pop()

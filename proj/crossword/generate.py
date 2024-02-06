import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword: Crossword = crossword
        self.domains: dict[Variable, set[str]] = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.domains:
            domain = set()
            for word in self.domains[var]:
                if len(word) == var.length:
                    domain.add(word)
            self.domains[var] = domain

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        if self.crossword.overlaps[x, y] is None:
            return False

        i, j = self.crossword.overlaps[x, y]
        flag = False
        domain = set()
        for wordX in self.domains[x]:
            flag2 = False
            for wordY in self.domains[y]:
                if wordX[i] == wordY[j]:
                    flag2 = True
                    break
            if flag2:
                domain.add(wordX)
            else:
                flag = True
        
        self.domains[x] = domain
        return flag

    def ac3(self, arcs: list[Variable] = None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs is None:
            arcs = list(self.crossword.overlaps.keys())

        while arcs:
            x, y = arcs.pop()
            if self.revise(x, y):
                if not self.domains[x]:
                    return False
                for z in self.crossword.neighbors(x):
                    if z != y:
                        arcs.append((z, x))
        
        return True

    def assignment_complete(self, assignment: dict[Variable, str]):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        return len(assignment) == len(self.domains)

    def consistent(self, assignment: dict[Variable, str]):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for var, word in assignment.items():
            if var.length != len(word):
                return False
            
        for vars, poss in self.crossword.overlaps.items():
            if poss:
                x, y = vars
                i, j = poss
                if x in assignment and y in assignment:
                    if assignment[x][i] != assignment[y][j]:
                        return False
            
        return len(assignment) == len(set(assignment.values()))

    def order_domain_values(self, var: Variable, assignment: dict[Variable, str]):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        domain: list[tuple[Variable, int]] = list()
        nbrs = set(i for i in self.crossword.neighbors(var) if i not in assignment)
        for word in self.domains[var]:
            cnt = 0
            for y in nbrs:
                i, j = self.crossword.overlaps[var, y]
                for wordY in self.domains[y]:
                    if word[i] != wordY[j]:
                        cnt += 1
            domain.append((word, cnt))

        domain.sort(key=lambda item: item[1])
        return [item[0] for item in domain]

    def select_unassigned_variable(self, assignment: dict[Variable, str]):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned = self.domains.keys() - assignment.keys()
        chosen = unassigned.pop()
        for var in unassigned:
            if len(self.domains[var]) > len(self.domains[chosen]):
                continue
            elif len(self.domains[var]) < len(self.domains[chosen]):
                chosen = var
            elif len(self.crossword.neighbors(var)) > len(self.crossword.neighbors(chosen)):
                chosen = var

        return chosen

    def backtrack(self, assignment: dict[Variable, str]):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        
        var = self.select_unassigned_variable(assignment)
        domain = self.order_domain_values(var, assignment)
        for word in domain:
            new_assignment = assignment.copy()
            new_assignment[var] = word
            if self.consistent(new_assignment):
                backup_domains = self.domains.copy()
                self.domains[var] = set([word])
                arcs = list()
                for nbr in self.crossword.neighbors(var):
                    arcs.append((nbr, var))
                if self.ac3(arcs):
                    result = self.backtrack(new_assignment)
                    if result:
                        return result
                self.domains = backup_domains

        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
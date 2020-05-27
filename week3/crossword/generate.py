import sys

from crossword import *
from operator import itemgetter

class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
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
                        w, h = draw.textsize(letters[i][j], font=font)
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
        for domain in self.domains:
            for word in self.domains[domain].copy():
                if len(word) != domain.length:
                    self.domains[domain].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        overlaps = self.crossword.overlaps

        # If there is an overlap of x and y
        if overlaps[x, y] != None:
            for X in self.domains[x].copy():
                is_correspondance = False
                for Y in self.domains[y]:
                    # if there is at least one correspondance for word X in Y
                    if X[overlaps[x, y][0]] == Y[overlaps[x, y][1]]:
                        is_correspondance = True
                        break
                
                # if there is no corresponding value for X in Y remove X from domains[x]
                if not is_correspondance:
                    self.domains[x].remove(X)
                    revised = True
        return revised


    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs == None:
            queue = list()
            for i in self.domains:
                for j in self.crossword.neighbors(i):
                    queue.append([i, j])
        else:
            queue = arcs
        
        while len(queue) > 0:
            x, y = queue[0]
            queue.remove(queue[0])
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                for z in self.crossword.neighbors(x):
                    if z != y:
                        queue.append([z, x])
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for var in self.crossword.variables:
            if var not in assignment:
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # check for lenght consistency
        for var in assignment:
            if len(assignment[var]) != var.length:
                return False

        # check for unicity
        values = assignment.values()
        if len(set(values)) != len(values):
            return False

        # check for overlap consistency
        overlaps = self.crossword.overlaps
        for overlap in overlaps:
            if overlaps[overlap] != None:
                if overlap[0] in assignment and overlap[1] in assignment:
                    first_word = assignment[overlap[0]]
                    second_word = assignment[overlap[1]]

                    # if two words overlap and have different letter for same cell
                    if first_word[overlaps[overlap][0]] != second_word[overlaps[overlap][1]]:
                        return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        constraintsList = {}
        for word in self.domains[var]:
            # unassigned neighbors 
            neighbors = self.crossword.neighbors(var) - set(assignment.keys())

            # counter for how many neighbors are ruled out by word
            count = 0
            for neighbor in neighbors:
                overlap = self.crossword.overlaps[var, neighbor]

                # if there is an overlap between word and neighbor
                if overlap != None:
                    for neighbord_word in self.domains[neighbor]:

                        # if word rule out neighbor increment counter
                        if word[overlap[0]] != neighbord_word[overlap[1]]:
                            count += 1
            constraintsList[word] = count
        
        # sort word in domains[var] by number of ruled out neighbors ascending
        sorted_words = sorted(constraintsList, key=constraintsList.get)
        return sorted_words

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned = list()

        # for each unassigned variable, add to list variable and domain's length
        # domain's length = number of remaining values in variable's domain
        for var in self.crossword.variables:
            if var not in assignment:
                unassigned.append([var, len(self.domains[var])])
        
        # order list by domain's length ascending
        ordered = sorted(unassigned, key=itemgetter(1))

        # get variables with minimum number of remaining values in their domain
        min_unassigned = [u[0] for u in ordered if u[1] == ordered[0][1]]

        # if several variables have minimum number of remaining values in their domain
        # order them by highest degree (= how many neighbors they got)
        if len(min_unassigned) > 1:
            high_degree = list()
            for min_u in min_unassigned:
                high_degree.append([min_u, len(self.crossword.neighbors(min_u))])

            ordered = sorted(high_degree, key=itemgetter(1), reverse=True)
        
        #return first variable
        return ordered[0][0]



    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # if assignment is complete, end of puzzle
        if self.assignment_complete(assignment):
            return assignment
        else:
            # get unassigned variable
            var = self.select_unassigned_variable(assignment)
            for value in self.order_domain_values(var, assignment):

                # add variable and new value to assignment
                assignment.update({var: value})

                # if updated assignment is consistent
                if self.consistent(assignment):

                    # next step
                    result = self.backtrack(assignment)
                    if result != None:
                        return result

            # if no assignment is possible remove variable from assignment
            assignment.remove(var)
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

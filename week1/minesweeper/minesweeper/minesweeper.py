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
        if len(self.cells == True) == self.count:
            return self.cells
        elif self.count == 0:
            return None

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        elif len(self.cells == True) == len(self.cells):
            return None

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count = self.count - 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


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
        for sentence in self.knowledge.copy():
            sentence.mark_mine(cell)
            #If the sentence is now empty, remove it from the knowledge base
            if (sentence.cells) == 0:
                self.knowledge.remove(sentence)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)
            #If the sentence is now empty, remove it from the knowledge base
            if len(sentence.cells) == 0:
                self.knowledge.remove(sentence)

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

        #Mark cell as mode made and mark it as safe
        self.moves_made.add(cell)
        self.mark_safe(cell)

        #Get surroundings cells (mines and unknowns)
        surroundings = self.get_surrounding_cells(cell)
        if len(surroundings) > 0 :
            for surrounding in surroundings.copy():
                #If surrounding cell is a known mine, update the sentence
                if surrounding in self.mines:
                    count = count - 1
                    surroundings.remove(surrounding)
            newSentence = Sentence(surroundings, count)

            #If the sentence not in knowledge base, add it
            if newSentence not in self.knowledge and len(newSentence.cells) > 0:
                self.knowledge.append(newSentence)
                self.process_knowledge(surroundings, count)

                #Look for subsets in the knowledge base
                for sentence in self.knowledge.copy() :
                    if sentence != newSentence and len(sentence.cells) > 0:
                        #There is a subset of the new sentence in the knowledge base
                        if sentence.cells.issubset(newSentence.cells) and sentence != newSentence :
                            newCount = newSentence.count - sentence.count
                            subSet = newSentence.cells.difference(sentence.cells)
                            self.knowledge.append(Sentence(subSet, newCount))
                            #Remove the now useless sentence from knowledge base
                            if newSentence in self.knowledge:
                                self.knowledge.remove(newSentence)
                            #Update the knowledge base
                            self.process_knowledge(subSet, newCount)

                        #The new sentence is a subset of a sentence in the knowledge base
                        elif newSentence.cells.issubset(sentence.cells) and sentence != newSentence:
                            newCount = sentence.count - newSentence.count
                            subSet = sentence.cells.difference(newSentence.cells)
                            self.knowledge.append(Sentence(subSet, newCount))
                            #Remove the now useless sentence from knowledge base
                            if sentence in self.knowledge:
                                self.knowledge.remove(sentence)
                            #Update the knowledge base
                            self.process_knowledge(subSet, newCount)
                            
        #Clean knowledge base of sentences with no cell left
        self.clean_knowledge()
        
    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for safe in self.safes:
            if safe not in self.moves_made and safe not in self.mines:
                return safe    
        return None
        



    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        notChosen = True
        while notChosen and len(self.moves_made) < self.height * self.width - len(self.mines):
            i = random.randint(0, self.height - 1)
            j = random.randint(0, self.width - 1)
            if (i, j) not in self.moves_made and (i, j) not in self.mines:
                notChosen = False
                return (i, j)
        return None

    def get_surrounding_cells(self, cell):
        (i, j) = cell
        surroundings = set()
        for k in range(i - 1, i + 2):
            for l in range(j - 1, j + 2):
                if (k >= 0 and k < self.height and l >= 0 and l < self.width) and not(k == i and l == j) and (k, l) not in self.moves_made and (k, l) not in self.safes:
                        surroundings.add((k,l))
        
        return surroundings

    #If, for a given sentence, there is no mine (count = 0), then mark all remaining cells as safe
    #If, the number of mines is equal to the number of cells in the sentence, mark all cells as mines
    def process_knowledge(self, cells, count):
        if count == 0:
            for cell in cells.copy():
                self.mark_safe(cell)
        elif count == len(cells):
            for cell in cells.copy():
                self.mark_mine(cell)
            


    #Remove empty knowledge and update knowledge
    def clean_knowledge(self):
        for knowledge in self.knowledge:
            if len(knowledge.cells) == 0:
                self.knowledge.remove(knowledge)
            else:
                self.process_knowledge(knowledge.cells, knowledge.count)

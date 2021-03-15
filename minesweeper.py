import itertools
import random

import logging

logging.basicConfig(filename='logs.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s - %(message)s')


class Minesweeper:
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


class Sentence:
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

        self.mines = set()
        self.safes = set()

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.cells == other.cells and self.count == other.count
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        return self.mines

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        return self.safes

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1
        self.mines.add(cell)

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """

        if cell in self.cells:
            self.cells.remove(cell)
        self.safes.add(cell)


class MinesweeperAI:
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()
        self.history = []

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def load_safes_and_mines_from_a_sentence_to_everywhere(self, sentence):  # utility function
        """
        spread safes and mines from concrete sentence to everywhere
        """
        for safe in sentence.safes:
            self.mark_safe_global(safe)
        for mine in sentence.mines:
            self.mark_mine_global(mine)

    def load_safes_and_mines_from_sentence_to_AI(self, sentence):
        """Load safes and mines from sentece to AI"""
        for safe in sentence.safes:
            self.mark_safe(safe)
        for mine in sentence.mines:
            self.mark_mine(mine)

    def mark_mine(self, cell):
        """Marks a cell as a mine for AI"""
        self.mines.add(cell)

    def mark_safe(self, cell):
        """Marks a cell as a safe for AI"""
        self.safes.add(cell)

    def mark_safe_for_AI_and_sentence(self, cell, sentence):
        """Marks a cell as a safe for AI and sentence"""
        self.mark_safe(cell)
        sentence.mark_safe(cell)

    def mark_mine_for_AI_and_sentence(self, cell, sentence):
        """Marks a cell as a safe for AI and sentence"""
        self.mark_mine(cell)
        sentence.mark_mine(cell)

    def mark_mine_global(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe_global(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def update_sentence_according_to_AI_info(self, sentence):
        for safe in self.safes:
            sentence.mark_safe(safe)
        for mine in self.mines:
            sentence.mark_mine(mine)

    def get_neighbours(self, cell):  # utility function
        """ Get set of neighbours of the cell """
        logging.info("get_neighbours")

        neighbours = set()
        y, x = cell
        for i in range(y - 1, y + 2):
            for j in range(x - 1, x + 2):
                if 0 <= j < self.width and 0 <= i < self.height:
                    neighbours.add((i, j))
        neighbours.remove(cell)
        return neighbours

    def infer_from_single_sentence_without_combining(self, sentence):
        if not bool(sentence.cells):
            return  # check. should not be any need

        inferred_something = False
        # inferred using count = len
        if sentence.count == len(sentence.cells):
            inferred_something = True
            print("inferred using count = len |comment->", sentence)
            for cell in tuple(sentence.cells):
                self.mark_mine_for_AI_and_sentence(cell, sentence)

        # inferred using count = 0
        if sentence.count == 0:
            inferred_something = True
            print("inferred using count = 0 |comment->", sentence)
            for cell in tuple(sentence.cells):
                self.mark_safe_for_AI_and_sentence(cell, sentence)

        # if something changed spread everywhere
        if inferred_something:
            self.load_safes_and_mines_from_sentence_to_AI(sentence)

    def infer_from_all_sentences_without_combining_them_and_give_results_to_AI(self):  # utility function
        """Try to infer from all sentences without combining different sentences and if got results  and spread them"""
        for sentence in tuple(self.knowledge):
            self.get_shortened_sentence_and_try_inference(sentence)

    def process_and_add_sentence_to_knowledge(self, s):
        s = self.get_shortened_sentence_and_try_inference(s)
        if len(s.cells) == 0:
            return

        sub_ss = self.sub_sentence_generation_from_single_sentence_againist_knowledge(s)
        self.knowledge.append(s)  # add out sentence

        if len(sub_ss) != 0:  # add sub sentence if possible to generate
            self.knowledge.extend(sub_ss)

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
        logging.info("add_knowledge")
        self.history.append(cell)  # no need, for debugging
        self.moves_made.add(cell)  # 1
        self.mark_safe(cell)  # 2
        cells = self.get_neighbours(cell)
        s = Sentence(cells, count)
        self.process_and_add_sentence_to_knowledge(s)
        self.infer_from_all_sentences_without_combining_them_and_give_results_to_AI()

        # 4,5

        # self.sub_sentence_addition_to_knowledgebase()
        self.sub_sentence_generation_from_single_sentence_againist_knowledge(sentence1=s)
        logging.info("add_knowledge ended")

    # check     aghr

    def try_get_shortened_sentence_or_False(self, sentence):
        """ return sentence based on known safes and mines"""

        if not sentence.cells:
            return False

        safe_cells = sentence.cells.intersection(self.safes)
        mine_cells = sentence.cells.intersection(self.mines)

        if not bool(safe_cells) and not bool(mine_cells):  # if both empty stop
            return False

        # construct new sentence and update with latest 'news'.
        new_sentence_cells = sentence.cells.difference(mine_cells, safe_cells)

        if not bool(new_sentence_cells):  # no need for empty one
            return False
        new_sentence_count = sentence.count - len(mine_cells)

        s = Sentence(new_sentence_cells, new_sentence_count)

        if s == sentence:
            return False
        return s

    def get_shortened_sentence_and_try_inference(self, sentence):
        s = self.try_get_shortened_sentence_or_False(sentence)
        if s != False:
            sentence = s
        self.infer_from_single_sentence_without_combining(sentence)
        return sentence

    def add_new_shortened_Sentence_if_possible(self, sentence):
        """add sentence based on known safes and mines"""
        s = self.get_shortened_sentence_and_try_inference(sentence)
        self.knowledge.append(s)

    def sub_sentence_generation_from_single_sentence_againist_knowledge(self, sentence1):
        results = []
        sentence1 = self.get_shortened_sentence_and_try_inference(sentence1)

        for sentence2 in self.knowledge:
            if sentence2 == sentence1:
                continue

            if not sentence1.cells or not sentence2.cells:  # if count also = 0, cells is empty nothing to do here.
                continue

            sentence2 = self.get_shortened_sentence_and_try_inference(sentence2)

            found_subset = False

            if sentence2.cells.issubset(sentence1.cells):
                cells = sentence1.cells.difference(sentence2.cells)
                count = sentence1.count - sentence2.count

                if not bool(cells):
                    continue  # validate so that it is not shortened sentence
                found_subset = True

            if sentence1.cells.issubset(sentence2.cells):
                cells = sentence2.cells.difference(sentence1.cells)
                count = sentence2.count - sentence1.count

                if not bool(cells):
                    continue  # validate so that it is not shortened sentence
                found_subset = True

            if found_subset:
                s = Sentence(cells, count)
                results.append(s)
                logging.info(f"sub_sentence_addition_to_knowledgebase   {s}  ")

        if not bool(results):
            return False
        return results

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        logging.info("make_safe_move")
        safes = self.safes
        moves_made = self.moves_made

        safe_moves = safes.difference(moves_made)  # -mines not neccessary

        if safe_moves:
            return safe_moves.pop()
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """

        ys = range(self.height)
        xs = range(self.width)
        options = set((y, x) for x in xs for y in ys).difference(self.moves_made, self.mines)

        return random.choice(tuple(options))

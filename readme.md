```
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
```

```
class MinesweeperAI:

    Minesweeper game player   

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

```

infer_without_combination_of_sentences

populate_safes_and_mines_from_all_sentences_to_all for sentence in knowledge-base:

populate_safes_and_mines_from_a_sentences_to_all

mark_mine mark_safe get_neighbours add_knowledge

```
shorten_Sentence_if_possible(self, cells, count):         --> Don't add a new sentence, shorten in place 
    by using result from other sentences (safes and mines) we can shorten number of possible cells where mines may be.

        if not cells or not count:
            return

        safe_cells = cells.intersection(self.safes)
        mine_cells = cells.intersection(self.mines)

        if not safe_cells or not mine_cells:
            return

        new_sentence_count = count - len(mine_cells)
        new_sentence_cells = cells.difference(safe_cells, mine_cells)
        # up -> all this code is preparation for #3

        if new_sentence_count:  # 3
            s = Sentence(new_sentence_cells, new_sentence_count)
            self.knowledge.append(s)

```

```
sub_sentence_addition_to_knowledgebase
    for all sentences
        for all sentences
            if sentence1 != sentence 2
                if sentence2.cells.is_subset(sentence1.cells)
                    then sentence2 is sub-set of sentence1, so we can generate 1 more sentence a-b = c:
                    new Sentence(cells = (sentence1.cells - sentence2.cells),  count = (sentence1.count - sentence2.count) )
                    add the new sentence to knowledge-base
```

```
make_safe_move
    all_board.intersection(safe cells).difference(moves made)
    return None if empty
```

```
make_random_move
    all_board.difference(moves made, mines known)
```
from collections import Counter
from random import randrange as rnd, shuffle

WORDS_REVERSE = 1
LETTERS_REVERSE = 2

LOSS_LOWER = 1
LOSS_UPPER = 2
LOSS_PUNCT = 4
LOSS_SPACE = 8


class Cipher:
    def __init__(self, word_order=0, loss_type=0):
        self.word_order = word_order
        self.loss_type = loss_type
        self.table = {}

    @staticmethod
    def split_words(text):
        # There is no good way to do this :-P
        for w in text.split():
            if w[:1] in '([*':
                yield w[:1]
                w = w[1:]
            if w[-1:] in ',;:.?!)]':
                yield w[:-1]
                yield w[-1:]
            else:
                yield w

    @staticmethod
    def join_words(words):
        # Bug
        return ' '.join(words)

    def apply_reorder(self, text):
        if self.word_order & WORDS_REVERSE:
            # extremely lame, we should parse input text better than this
            words = Cipher.split_words(text)
            text = Cipher.join_words(words[::-1])
        if self.word_order & LETTERS_REVERSE:
            # extremely lame
            # unclear how this should interact with capitalized words
            words = Cipher.split_words(text)
            text = Cipher.join_words(word[::-1] for word in words)
        return text

    def apply_loss(self, text):
        ty = self.loss_type
        if ty & LOSS_LOWER:
            text = text.lower()
        elif ty & LOSS_UPPER:
            text = text.upper()

        if ty & LOSS_PUNCT:
            text = ''.join(c for c in text if c.isalnum() or c.isspace())
        if ty & LOSS_SPACE:
            text = ''.join(c for c in text if not c.isspace())

        return text

    def apply_table(self, text):
        return ''.join(self.table.get(c, c) for c in text)

    def encode(self, text):
        text = self.apply_reorder(text)
        text = self.apply_loss(text)
        text = self.apply_table(text)
        return text


def random_cipher_for_text(text):
    loss_type = 0
    if rnd(3) != 0:
        loss_type |= LOSS_UPPER
    if rnd(2) != 0:
        loss_type |= LOSS_PUNCT
    if rnd(2) != 0:
        loss_type |= LOSS_SPACE
    cipher = Cipher(loss_type=loss_type)

    freq = Counter(text.lower())
    letters = [c for c in freq if c.isalpha() and freq[c] >= 2]
    shuffle(letters)
    max_pairs = min(len(letters) // 2, 5)
    for i in range(rnd(1, max_pairs + 1)):
        a, b = letters[2 * i:2 * (i + 1)]
        cipher.table[a] = b
        cipher.table[b] = a
        cipher.table[a.upper()] = b.upper()
        cipher.table[b.upper()] = a.upper()

    letters = letters[2 * max_pairs:]
    SYMS = '@#$%&<>'  # TODO filter out junk already present in text
    if not any(c.isdigit() for c in text):
        if rnd(3) == 0:
            SYMS = '0123456789'
        elif rnd(4) == 0:
            SYMS += '0123456789'
    max_syms = min(len(letters), len(SYMS))
    num_syms = rnd(0, max_syms + 1)
    for a, b in zip(letters[:num_syms], SYMS):
        cipher.table[a] = b
        cipher.table[a.upper()] = b
    return cipher 


if __name__ == '__main__':
    import sys
    text = sys.stdin.read()
    for _ in range(5):
        c = random_cipher_for_text(text)
        print(c.encode(text).strip())

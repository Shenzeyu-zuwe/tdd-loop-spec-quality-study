

class BoyerMooreSearch:
    """
    his is a class that implements the Boyer-Moore algorithm for string searching, which is used to find occurrences of a pattern within a given text.
    """

    def __init__(self, text, pattern):
        """
        Initializes the BoyerMooreSearch class with the given text and pattern.
        :param text: The text to be searched, str.
        :param pattern: The pattern to be searched for, str.
        """
        self.text, self.pattern = text, pattern
        self.textLen, self.patLen = len(text), len(pattern)

    def match_in_pattern(self, char):
        """
        Finds the rightmost occurrence of a character in the pattern.
        :param char: The character to be searched for, str.
        :return: The index of the rightmost occurrence of the character in the pattern, int.
        >>> boyerMooreSearch = BoyerMooreSearch("ABAABA", "AB")
        >>> boyerMooreSearch.match_in_pattern("A")
        0

        """
        return self.pattern.rfind(char)

    def mismatch_in_text(self, currentPos):
        """
        Determines the position of the first dismatch between the pattern and the text.
        :param currentPos: The current position in the text, int.
        :return: The position of the first dismatch between the pattern and the text, int,otherwise -1.
        >>> boyerMooreSearch = BoyerMooreSearch("ABAABA", "ABC")
        >>> boyerMooreSearch.mismatch_in_text(0)
        2

        """
        if not self.pattern or currentPos + self.patLen > self.textLen:
            return -1

        for i in range(self.patLen - 1, -1, -1):
            if self.text[currentPos + i] != self.pattern[i]:
                return currentPos + i

        return -1

    def bad_character_heuristic(self):
        """
        Finds all occurrences of the pattern in the text.
        :return: A list of all positions of the pattern in the text, list.
        >>> boyerMooreSearch = BoyerMooreSearch("ABAABA", "AB")
        >>> boyerMooreSearch.bad_character_heuristic()
        [0, 3]

        """
        if not self.pattern:
            return list(range(self.textLen + 1))

        results = []
        currentPos = 0

        while currentPos + self.patLen <= self.textLen:
            mismatchPos = self.mismatch_in_text(currentPos)

            if mismatchPos == -1:
                results.append(currentPos)
                currentPos += 1
            else:
                mismatchChar = self.text[mismatchPos]
                patternIdx = self.match_in_pattern(mismatchChar)

                if patternIdx == -1:
                    shift = mismatchPos - currentPos + 1
                else:
                    shift = mismatchPos - currentPos - patternIdx
                    if shift <= 0:
                        shift = 1

                currentPos += shift

        return results

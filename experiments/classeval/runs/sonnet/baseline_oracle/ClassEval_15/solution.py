class BoyerMooreSearch:
    def __init__(self, text, pattern):
        self.text, self.pattern = text, pattern
        self.textLen, self.patLen = len(text), len(pattern)

    def match_in_pattern(self, char):
        for i in range(self.patLen - 1, -1, -1):
            if self.pattern[i] == char:
                return i
        return -1

    def mismatch_in_text(self, currentPos):
        for i in range(self.patLen - 1, -1, -1):
            if self.pattern[i] != self.text[currentPos + i]:
                return currentPos + i
        return -1

    def bad_character_heuristic(self):
        positions = []
        if self.patLen == 0:
            return list(range(self.textLen + 1))
        i = 0
        while i <= self.textLen - self.patLen:
            mismatch = self.mismatch_in_text(i)
            if mismatch == -1:
                positions.append(i)
                i += 1
            else:
                bad_char = self.text[mismatch]
                char_pos = self.match_in_pattern(bad_char)
                shift = mismatch - (i + char_pos) if char_pos != -1 else mismatch - i + 1
                i += max(1, shift)
        return positions
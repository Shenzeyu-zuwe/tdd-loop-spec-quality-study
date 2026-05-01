import re

class AutomaticGuitarSimulator:
    def __init__(self, text) -> None:
        self.play_text = text

    def interpret(self, display=False):
        play_list = []
        if not self.play_text or not self.play_text.strip():
            return play_list
        for token in self.play_text.split():
            m = re.match(r'^([A-Za-z]+)(\d+)$', token)
            if m:
                chord, tune = m.group(1), m.group(2)
                if display:
                    self.display(chord, tune)
                play_list.append({'Chord': chord, 'Tune': tune})
        return play_list

    def display(self, key, value):
        result = f"Normal Guitar Playing -- Chord: {key}, Play Tune: {value}"
        print(result)
        return result

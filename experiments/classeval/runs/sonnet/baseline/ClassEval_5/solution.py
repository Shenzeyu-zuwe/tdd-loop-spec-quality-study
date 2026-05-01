class AutomaticGuitarSimulator:
    def __init__(self, text) -> None:
        self.play_text = text

    def interpret(self, display=False):
        if not self.play_text or not self.play_text.strip():
            return []
        play_list = []
        for item in self.play_text.split():
            chord = ''
            tune = ''
            for i, ch in enumerate(item):
                if ch.isdigit():
                    chord = item[:i]
                    tune = item[i:]
                    break
            play_list.append({'Chord': chord, 'Tune': tune})
            if display:
                self.display(chord, tune)
        return play_list

    def display(self, key, value):
        result = f"Normal Guitar Playing -- Chord: {key}, Play Tune: {value}"
        print(result)
        return result
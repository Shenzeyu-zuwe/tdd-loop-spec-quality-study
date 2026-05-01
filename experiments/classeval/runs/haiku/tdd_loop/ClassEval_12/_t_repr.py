import sys
sys.path.insert(0, '.')
import random
from solution import BlackjackGame

black_jack_game = BlackjackGame()
print(repr(black_jack_game.check_winner(['QD', '9D', 'JC', 'QH', 'AS'], ['QD', '9D', 'JC', 'QH', '2S'])))

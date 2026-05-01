import sys
sys.path.insert(0, '.')
import random
from solution import BlackjackGame

black_jack_game = BlackjackGame()
print(black_jack_game.calculate_hand_value(['QD', '9D', 'JC', 'QH', 'AS']))

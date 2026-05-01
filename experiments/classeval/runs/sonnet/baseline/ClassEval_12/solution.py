import random

class BlackjackGame:
    def __init__(self):
        self.deck = self.create_deck()
        self.player_hand = []
        self.dealer_hand = []

    def create_deck(self):
        suits = ['S', 'H', 'D', 'C']
        ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        deck = [rank + suit for suit in suits for rank in ranks]
        random.shuffle(deck)
        return deck

    def calculate_hand_value(self, hand):
        value = 0
        aces = 0
        for card in hand:
            rank = card[:-1]
            if rank in ('J', 'Q', 'K'):
                value += 10
            elif rank == 'A':
                value += 11
                aces += 1
            else:
                value += int(rank)
        while value > 21 and aces:
            value -= 10
            aces -= 1
        return value

    def check_winner(self, player_hand, dealer_hand):
        p = self.calculate_hand_value(player_hand)
        d = self.calculate_hand_value(dealer_hand)
        if p <= 21 and d <= 21:
            return 'Player wins' if p >= d else 'Dealer wins'
        else:
            return 'Player wins' if p <= d else 'Dealer wins'
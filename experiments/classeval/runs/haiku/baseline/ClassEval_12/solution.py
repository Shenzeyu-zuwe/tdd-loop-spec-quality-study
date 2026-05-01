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
        total = 0
        aces = 0
        
        for card in hand:
            rank = card[:-1]
            
            if rank == 'A':
                total += 11
                aces += 1
            elif rank in ['J', 'Q', 'K']:
                total += 10
            else:
                total += int(rank)
        
        while total > 21 and aces > 0:
            total -= 10
            aces -= 1
        
        return total

    def check_winner(self, player_hand, dealer_hand):
        player_value = self.calculate_hand_value(player_hand)
        dealer_value = self.calculate_hand_value(dealer_hand)
        
        if player_value <= 21 and dealer_value <= 21:
            if player_value > dealer_value:
                return 'Player wins'
            else:
                return 'Dealer wins'
        else:
            if player_value > dealer_value:
                return 'Dealer wins'
            else:
                return 'Player wins'
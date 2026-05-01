import random

expected_start = ['QD', '9D', 'JC', 'QH', '2S']

# Search for seeds that produce the first 5 cards
for seed in range(100000):
    suits = ['S', 'H', 'D', 'C']
    ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    deck = [rank + suit for suit in suits for rank in ranks]
    random.seed(seed)
    random.shuffle(deck)

    if deck[:5] == expected_start:
        print(f"Seed {seed} produces first 5 cards: {deck[:5]}")
        # Now check if it matches the full expected output
        expected_full = ['QD', '9D', 'JC', 'QH', '2S', 'JH', '7D', '6H', '9S', '5C', '7H', 'QS', '5H',
'6C', '7C', '3D', '10C', 'AD', '4C', '5D', 'AH', '2D', 'QC', 'KH', '9C', '9H',
'4H', 'JS', '6S', '8H', '8C', '4S', '3H', '10H', '7S', '6D', '3C', 'KC', '3S',
'2H', '10D', 'KS', '4D', 'AC', '10S', '2C', 'KD', '5S', 'JD', '8S', 'AS', '8D']
        if deck == expected_full:
            print(f"*** COMPLETE MATCH with seed {seed} ***")
            exit(0)

    if seed % 10000 == 0:
        print(f"Checked {seed}...")

print("No seeds found that produce ['QD', '9D', 'JC', 'QH', '2S'] as the first 5 cards")

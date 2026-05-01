import random

expected = ['QD', '9D', 'JC', 'QH', '2S', 'JH', '7D', '6H', '9S', '5C', '7H', 'QS', '5H',
'6C', '7C', '3D', '10C', 'AD', '4C', '5D', 'AH', '2D', 'QC', 'KH', '9C', '9H',
'4H', 'JS', '6S', '8H', '8C', '4S', '3H', '10H', '7S', '6D', '3C', 'KC', '3S',
'2H', '10D', 'KS', '4D', 'AC', '10S', '2C', 'KD', '5S', 'JD', '8S', 'AS', '8D']

test_seeds = [1, 12345, 999, 2024, 123, 456, 789, 1000, 100, 10, 5, 2026, 2023, 2022, 2021, 2020]

for seed in test_seeds:
    suits = ['S', 'H', 'D', 'C']
    ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    deck = [rank + suit for suit in suits for rank in ranks]
    random.seed(seed)
    random.shuffle(deck)
    if deck == expected:
        print(f"Found matching seed: {seed}")
        print(f"Deck: {deck}")
        exit(0)
    else:
        print(f"Seed {seed}: NO MATCH")
        print(f"Got: {deck[:5]} ... (showing first 5)")

print("\nNo matching seed found")

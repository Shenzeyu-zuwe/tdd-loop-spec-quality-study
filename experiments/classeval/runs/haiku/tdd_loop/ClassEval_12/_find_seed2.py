import random

expected = ['QD', '9D', 'JC', 'QH', '2S', 'JH', '7D', '6H', '9S', '5C', '7H', 'QS', '5H',
'6C', '7C', '3D', '10C', 'AD', '4C', '5D', 'AH', '2D', 'QC', 'KH', '9C', '9H',
'4H', 'JS', '6S', '8H', '8C', '4S', '3H', '10H', '7S', '6D', '3C', 'KC', '3S',
'2H', '10D', 'KS', '4D', 'AC', '10S', '2C', 'KD', '5S', 'JD', '8S', 'AS', '8D']

# Try different suit and rank orders
suit_orders = [
    ['S', 'H', 'D', 'C'],
    ['C', 'D', 'H', 'S'],
    ['S', 'D', 'H', 'C'],
    ['H', 'D', 'C', 'S'],
]

rank_orders = [
    ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'],
    ['K', 'Q', 'J', '10', '9', '8', '7', '6', '5', '4', '3', '2', 'A'],
]

loop_orders = [
    'suits_outer',  # [rank + suit for suit in suits for rank in ranks]
    'ranks_outer',  # [rank + suit for rank in ranks for suit in suits]
]

for loop_order in loop_orders:
    for suits in suit_orders:
        for ranks in rank_orders:
            for seed in range(2000):
                if loop_order == 'suits_outer':
                    deck = [rank + suit for suit in suits for rank in ranks]
                else:
                    deck = [rank + suit for rank in ranks for suit in suits]

                random.seed(seed)
                random.shuffle(deck)
                if deck == expected:
                    print(f"Found! loop_order={loop_order}, suits={suits}, ranks={ranks}, seed={seed}")
                    exit(0)

print("Not found in any configuration")

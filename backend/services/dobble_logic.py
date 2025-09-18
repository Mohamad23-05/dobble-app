# services/dobble_logic.py
from typing import Optional, Dict

VALID_ORDERS = [2, 3, 4, 5, 7]


def get_params(
        n: Optional[int] = None,
        symbols_per_card: Optional[int] = None,
        num_cards: Optional[int] = None,
) -> Optional[Dict[str, int]]:
    # choose based on which argument was provided
    if n is not None:
        if n in VALID_ORDERS:
            return {
                "n": n,
                "symbols_per_card": n + 1,
                "num_cards": n ** 2 + n + 1,
            }
        return None

    if symbols_per_card is not None:
        n_calc = symbols_per_card - 1
        if n_calc in VALID_ORDERS:
            return {
                "n": n_calc,
                "symbols_per_card": symbols_per_card,
                "num_cards": n_calc ** 2 + n_calc + 1,
            }
        return None

    if num_cards is not None:
        for possible_n in VALID_ORDERS:
            if possible_n ** 2 + possible_n + 1 == num_cards:
                return {
                    "n": possible_n,
                    "symbols_per_card": possible_n + 1,
                    "num_cards": num_cards,
                }
        return None

    # nothing provided
    return None


def generate_projective_plane(n: int):
    """
    Returns the cards (blocks) of a projective plane of order n.
    Ensures that 0 appears in the first (n+1) cards.
    """
    cards = []

    # First card: 0..n
    cards.append(list(range(n + 1)))

    # Next n cards, all contain 0
    for j in range(n):
        card = [0]
        for k in range(n):
            value = n + 1 + n * j + k
            card.append(value)
        cards.append(card)

    # Remaining n*n cards
    for i in range(n):
        for j in range(n):
            card = [i + 1]
            for k in range(n):
                value = n + 1 + n * k + ((i * k + j) % n)
                card.append(value)
            cards.append(card)

    return cards

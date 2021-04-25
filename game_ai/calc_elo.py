import math
from typing import Any


def calc_elo_rating_diff(win: int, lose: int) -> Any:
    if win == 0 or lose == 0:
        return None

    n = win + lose
    p_hat = win / n

    # 正規分布の信頼区間95%
    z = 1.96
    v = math.sqrt(p_hat * (1 - p_hat) / n)

    p_low = max(p_hat - z * v, 1e-9)
    p_high = min(p_hat + z * v, 1.0 - 1e-9)
    elo_rating_low = -400 * math.log10(1/p_low-1)
    elo_rating_high = -400 * math.log10(1/p_high-1)
    elo_rating = -400 * math.log10(1/p_hat-1)

    return elo_rating, elo_rating_low, elo_rating_high

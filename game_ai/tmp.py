import argparse
import math
from typing import Any

import samurai_dataset

# from struct import *


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

    return elo_rating_low, elo_rating, elo_rating_high


def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--file0", help="")
    parser.add_argument("--file1", help="")
    parser.add_argument("--output", help="")
    parser.add_argument("--model", help="", choices=['samurai', 'dog'])

    args = parser.parse_args()

    dataset0 = samurai_dataset.SamuraiDataset(args.file0, args.model)
    dataset1 = samurai_dataset.SamuraiDataset(args.file1, args.model)

    len_dataset0 = len(dataset0)
    len_dataset1 = len(dataset1)
    win_count = 0

    for i in range(0, len_dataset0, 2):
        _, actual_result, _, _, _, _, _ = dataset0[i]
        win_count += actual_result
        # print(actual_result)

    for i in range(1, len_dataset1, 2):
        _, actual_result, _, _, _, _, _ = dataset1[i]
        win_count += actual_result

    lose_count = len_dataset0 / 2 + len_dataset1 / 2 - win_count
    # print(win_count, lose_count)

    elo_low, elo, elo_high = calc_elo_rating_diff(win_count, lose_count)
    print(f'elo {elo}: [{elo_low}, {elo_high}]')

    with open(args.output, mode='w') as f:
        f.write(f'elo {elo}: [{elo_low}, {elo_high}]')


if __name__ == '__main__':
    main()

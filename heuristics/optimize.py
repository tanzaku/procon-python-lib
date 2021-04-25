#!/usr/bin/env python3

from typing import Dict
import optuna
import matplotlib.pyplot as plt

import subprocess
import sys
import re
import time

import argparse

parser = argparse.ArgumentParser(description='')
# parser.add_argument('-p', '--parallel', action='store_true')
# args = parser.parse_args()

score_pattern = re.compile(r'^(?:.*Score = )?(-?[0-9.]+).*$')

OBJECTIVE_PARAMS = {
    ('repeat', 'suggest_int', 1, 1),
    ('start-temp-100', 'suggest_uniform', 0.0, 0.15),
    ('transition0-rate-100', 'suggest_int', 0, 5),
    ('transition1-rate-100', 'suggest_int', 0, 5),
    ('transition2-rate-100', 'suggest_int', 0, 5),
    ('start-temp-150', 'suggest_uniform', 0.0, 0.15),
    ('transition0-rate-150', 'suggest_int', 0, 5),
    ('transition1-rate-150', 'suggest_int', 0, 5),
    ('transition2-rate-150', 'suggest_int', 0, 5),
    ('start-temp-200', 'suggest_uniform', 0.0, 0.15),
    ('transition0-rate-200', 'suggest_int', 0, 5),
    ('transition1-rate-200', 'suggest_int', 0, 5),
    ('transition2-rate-200', 'suggest_int', 0, 5),
}

def run_test(params: Dict):
    param_arg = ' '.join([f'--{k} {v}' for k, v in params.items()])

    cmd = f'par --target local --commands "target/release/ahc001 --fix-iteration {param_arg} < {{INPUT}}" --variables "INPUT=OPEN_DIR(tools/in)"'
    # cmd = f'par --target local --commands "echo {param_arg} {{INPUT}}" --variables "INPUT=OPEN_DIR(tools/in)"'
    proc = subprocess.run(cmd, shell=True,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.DEVNULL)

    scores = []
    text = proc.stdout.decode().strip()

    print(cmd)

    if proc.returncode != 0:
        print('Execute failed...')
        sys.exit(1)

    for line in text.splitlines():
        match = score_pattern.match(line)
        # print('text', line, match)
        if match is not None:
            score_str = match.groups()[0]
            score = float(score_str)
            scores.append(score)

    if len(scores) == 0:
        print(text)
        print('Parsing score failed...')
        sys.exit(1)

    score = sum(scores)
    # return sum(map(lambda x: x[1], scores))
    return score


def objective(trial):
    def obj_to_param(obj):
        if obj[1] == 'suggest_int':
            return trial.suggest_int(obj[0], obj[2], obj[3])
        if obj[1] == 'suggest_uniform':
            return trial.suggest_uniform(obj[0], obj[2], obj[3])
        if obj[1] == 'suggest_loguniform':
            return trial.suggest_loguniform(obj[0], obj[2], obj[3])
        raise Exception

    params = {obj[0]: obj_to_param(obj) for obj in OBJECTIVE_PARAMS}

    # 評価値を返す(デフォルトで最小化するようになっている)
    return run_test(params)


if __name__ == '__main__':
    subprocess.run(f'cargo build --release', shell=True).check_returncode()

    study_name = f'ahc001-study'

    # studyオブジェクト生成
    study = optuna.create_study(study_name=study_name,
                                storage=f'sqlite:///./optuna_study.db',
                                direction='maximize',
                                load_if_exists=True)

    # 最適化実行
    study.optimize(objective, n_trials=50, n_jobs=5)

    trial = study.best_trial
    print(f'trial.value : {trial.value}')
    for key, value in trial.params.items():
        print(f'{key}: {value}')

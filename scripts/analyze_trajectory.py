#!/usr/bin/env python3
import argparse
import csv
from math import sqrt


def load(path):
    with open(path, newline='') as f:
        return list(csv.DictReader(f))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('trajectory_csv')
    ap.add_argument('--goal', nargs=3, type=float, default=(0.0, 0.0, 2.0))
    args = ap.parse_args()

    rows = load(args.trajectory_csv)
    if len(rows) < 2:
        raise SystemExit('Need at least two samples')

    pts = [(float(r['x']), float(r['y']), float(r['z'])) for r in rows]
    ts = [float(r['time_s']) for r in rows]
    path_length = sum(sqrt(sum((b[i] - a[i]) ** 2 for i in range(3))) for a, b in zip(pts[:-1], pts[1:]))
    final = pts[-1]
    goal = tuple(args.goal)
    final_error = sqrt(sum((final[i] - goal[i]) ** 2 for i in range(3)))

    print(f'samples: {len(rows)}')
    print(f'duration_s: {ts[-1] - ts[0]:.3f}')
    print(f'path_length_m: {path_length:.3f}')
    print(f'final_position_error_m: {final_error:.3f}')


if __name__ == '__main__':
    main()

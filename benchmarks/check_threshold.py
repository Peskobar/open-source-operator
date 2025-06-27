import argparse
import csv
import json
import sys


def read_results(path: str):
    if path.endswith(".json"):
        with open(path) as f:
            return json.load(f)
    rows = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            row["success"] = str(row["success"]).lower() == "true"
            rows.append(row)
    return rows


def main(path: str, threshold: float = 0.9) -> None:
    rows = read_results(path)
    if not rows:
        print("No results found")
        sys.exit(1)
    success_rate = sum(1 for r in rows if r["success"]) / len(rows)
    if success_rate < threshold:
        print(f"Success rate {success_rate:.2f} below threshold {threshold}")
        sys.exit(1)
    print(f"Success rate {success_rate:.2f} OK")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("--threshold", type=float, default=0.9)
    args = parser.parse_args()
    main(args.path, args.threshold)

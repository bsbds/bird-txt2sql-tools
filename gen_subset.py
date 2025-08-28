import json
import argparse
import random
from collections import defaultdict

def main():
    parser = argparse.ArgumentParser(description="Create a subset of evaluation data.")
    parser.add_argument("--json_path", default="./mini_dev_sqlite.json", help="Path to the input JSON file.")
    parser.add_argument("--sql_path", default="./mini_dev_sqlite_gold.sql", help="Path to the input SQL file.")
    parser.add_argument("--output_json", default="./mini_dev_sqlite_subset.json", help="Path for the output JSON subset.")
    parser.add_argument("--output_sql", default="./mini_dev_sqlite_gold_subset.sql", help="Path for the output SQL subset.")
    parser.add_argument("--simple", type=int, default=10, help="Number of simple queries to select.")
    parser.add_argument("--moderate", type=int, default=10, help="Number of moderate queries to select.")
    parser.add_argument("--challenging", type=int, default=10, help="Number of challenging queries to select.")
    parser.add_argument("--seed", type=int, default=133, help="Random seed for sampling.")

    args = parser.parse_args()
    random.seed(args.seed)

    # Load JSON data
    with open(args.json_path, 'r') as f:
        json_data = json.load(f)
    
    # Load SQL lines
    with open(args.sql_path, 'r') as f:
        sql_lines = [line.strip() for line in f if line.strip()]
    
    if len(json_data) != len(sql_lines):
        raise ValueError("JSON and SQL file must have the same number of entries.")
    
    # Group by difficulty
    grouped = defaultdict(list)
    for idx, item in enumerate(json_data):
        grouped[item["difficulty"]].append((idx, item))
    
    # Sample entries
    selected_indices = set()
    for diff, count in [("simple", args.simple), ("moderate", args.moderate), ("challenging", args.challenging)]:
        available = grouped.get(diff, [])
        if len(available) < count:
            print(f"Warning: Requested {count} {diff} samples, but only {len(available)} available.")
        samples = random.sample(available, min(count, len(available)))
        selected_indices.update(idx for idx, _ in samples)
    
    # Sort indices to preserve order
    sorted_indices = sorted(selected_indices)
    
    # Create subsets
    subset_json = [json_data[i] for i in sorted_indices]
    subset_sql = [sql_lines[i] for i in sorted_indices]
    
    # Write outputs
    with open(args.output_json, 'w') as f:
        json.dump(subset_json, f, indent=2)
    with open(args.output_sql, 'w') as f:
        f.write("\n".join(subset_sql) + "\n")
    
    print(f"Created subset with {len(subset_json)} entries.")
    print(f"- Simple: {len([x for x in subset_json if x['difficulty']=='simple'])}")
    print(f"- Moderate: {len([x for x in subset_json if x['difficulty']=='moderate'])}")
    print(f"- Challenging: {len([x for x in subset_json if x['difficulty']=='challenging'])}")

if __name__ == "__main__":
    main()


#!/usr/bin/env python3
import sys

category_counts = {}

for line in sys.stdin:
    fields = line.strip().split("\t")

    if not fields:
        continue

    if fields[0] == "STUDENT":
        print(line.strip())

    elif fields[0] == "CATEGORY" and len(fields) == 3:
        category = fields[1]
        count = int(fields[2])

        category_counts[category] = (
            category_counts.get(category, 0) + count
        )

for category, count in sorted(category_counts.items()):
    print(f"SUMMARY\t{category}\t{count}")

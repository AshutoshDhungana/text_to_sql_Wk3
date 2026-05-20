"""Quick test script for the decomposition parser."""
from sql_generator import parse_decomposition

decs = parse_decomposition()
print(f"Parsed {len(decs)} decompositions")
for i, dec in enumerate(decs[:3]):
    print(f"\nQ{i+1}: {dec.get('Intent', '')}")
    print(f"  Tables: {dec.get('Tables', '')}")
    print(f"  Columns: {dec.get('Columns', '')}")

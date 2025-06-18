import pandas as pd

# Load the Excel with two header rows
df = pd.read_excel("test.xlsx", header=[0, 1])

# Iterate over each row
for index, row in df.iterrows():
    print(f"\n--- Row {index + 1} ---")
    for (main_header, sub_header), value in row.items():
        print(f"{main_header} -> {sub_header} = {value}")

import pandas as pd

df = pd.read_csv('this.csv')

# Helper function to format values for SQL
def format_sql_value(value):
    if pd.isna(value):
        return "NULL"
    elif isinstance(value, str):
        return "'{}'".format(value.replace("'", "''"))
    else:
        return str(value)

table_name = "custom_field_value"
columns = [
    'id', 'int_value', 'dec_value', 'char_value', 'date_value',
    'field_definition_id', 'text_style', 'table_header_id',
    'description', 'name', 'parent_field_value_id'
]

batch_size = 500  # Adjust based on your environment's limits
insert_statements = []

for start in range(0, len(df), batch_size):
    batch_df = df.iloc[start:start+batch_size]
    values_sql = []
    for _, row in batch_df.iterrows():
        values = [format_sql_value(row[col]) for col in columns]
        values_sql.append(f"({', '.join(values)})")
    
    insert_sql = (
        f"INSERT INTO {table_name} (\n    {', '.join(columns)}\n) VALUES\n" +
        ",\n".join(values_sql) +
        ";"
    )
    insert_statements.append(insert_sql)

sql_file_path = "insert_custom_field_value.sql"
with open(sql_file_path, "w", encoding='utf-8') as f:
    f.write("\n\n".join(insert_statements))

print(f"SQL insert file generated: {sql_file_path}")

import csv

# Input CSV file
csv_file = "/Users/omkaram/Downloads/query_result_2025-09-13T18_56_38.638216Z.csv"

# Output SQL file
sql_file = "./helper_scripts/insert_app.txt"

table_name = "application"

with open(csv_file, newline="", encoding="utf-8") as infile, open(sql_file, "w", encoding="utf-8") as outfile:
    reader = csv.DictReader(infile)

    for row in reader:
        # Escape single quotes in strings
        def esc(val):
            if val is None or val.strip() == "":
                return "NULL"
            return "'" + val.replace("'", "''") + "'"

        query = f"""
INSERT INTO {table_name} 
(id, spool_id, status, ifi_id, created_at, updated_at, request_id)
VALUES (
    {esc(row['ID'])},
    {esc(row['Spool ID'])},
    {esc(row['Status'])},
    {row['I Fi ID'] if row['I Fi ID'] else 'NULL'},
    {esc(row['Created At'])},
    {esc(row['Updated At'])},
    {esc(row['Request ID'])}
);
"""
        outfile.write(query)

print(f"Insert queries written to {sql_file}")

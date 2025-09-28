import csv
import json


csv_file = "/Users/omkaram/Downloads/stage_1.csv"

# Output SQL file
sql_file = "./helper_scripts/insert_stage.txt"

table_name = "application_stage"

with open(csv_file, newline="", encoding="utf-8") as infile, open(sql_file, "w", encoding="utf-8") as outfile:
    reader = csv.DictReader(infile)
    
    for row in reader:
        # Escape single quotes in strings
        def esc(val):
            if val is None or val.strip() == "":
                return "NULL"
            return "'" + val.replace("'", "''") + "'"

        # Handle JSON fields (result, details)
        def jsonb_field(val):
            if val is None or val.strip() == "":
                return "'{}'::jsonb"
            try:
                json.loads(val)  # validate JSON
                return "'" + val.replace("'", "''") + "'::jsonb"
            except json.JSONDecodeError:
                return "'{}'::jsonb"

        result_val = jsonb_field(row.get("Result", ""))
        details_val = jsonb_field(row.get("Details", ""))

        # Prepare query
        query = f"""
INSERT INTO {table_name} 
(id, application_id, name, status, result, created_at, updated_at, ifi_id, details, reason_code, reason_description)
VALUES (
    {esc(row['ID'])},
    {esc(row['Application ID'])},
    {esc(row['Name'])},
    {esc(row['Status'])},
    {result_val},
    {esc(row['Created At'])},
    {esc(row['Updated At'])},
    {row['I Fi ID'] if row['I Fi ID'] else 'NULL'},
    {details_val},
    {esc(row['Reason Code'])},
    {esc(row['Reason Description'])}
);
"""
        outfile.write(query)

print(f"Insert queries written to {sql_file}")

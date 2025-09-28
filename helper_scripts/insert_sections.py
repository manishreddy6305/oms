import csv
import json

# Input CSV file
csv_file = "/Users/omkaram/Downloads/section_1.csv"

# Output SQL file
sql_file = "./helper_scripts/insert_sections.txt"

table_name = "application_section"

with open(csv_file, newline="", encoding="utf-8") as infile, open(sql_file, "w", encoding="utf-8") as outfile:
    reader = csv.DictReader(infile)
    
    for row in reader:
        # Escape single quotes in strings
        def esc(val):
            if val is None or val == "":
                return "NULL"
            return "'" + val.replace("'", "''") + "'"

        # Convert JSON field
        details = row.get("Details", "")
        if details.strip() == "":
            details_val = "'{}'::jsonb"
        else:
            try:
                json.loads(details)  # validate
                details_val = "'" + details.replace("'", "''") + "'::jsonb"
            except json.JSONDecodeError:
                # fallback: treat as empty json
                details_val = "'{}'::jsonb"

        # Prepare query
        query = f"""
INSERT INTO {table_name} 
(id, application_id, name, type, details, created_at, updated_at, ifi_id)
VALUES (
    {esc(row['ID'])},
    {esc(row['Application ID'])},
    {esc(row['Name'])},
    {esc(row['Type'])},
    {details_val},
    {esc(row['Created At'])},
    {esc(row['Updated At'])},
    {row['I Fi ID'] if row['I Fi ID'] else 'NULL'}
);
"""
        outfile.write(query)

print(f"Insert queries written to {sql_file}")

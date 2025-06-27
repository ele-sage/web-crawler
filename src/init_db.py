import sqlite3
import os
import csv

# Increase CSV field size limit to max
csv.field_size_limit(2147483647)

def get_csv_headers(csv_path):
    """Reads the first line of a CSV file and returns the headers."""
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        return next(reader)

def sanitize_name(name):
    """Sanitizes a column name for SQL by quoting it."""
    return f'"{name.replace('"', '""')}"'

def create_table_from_csv_headers(cursor, table_name, headers, foreign_keys=None):
    """
    Generates and executes a CREATE TABLE statement from a list of headers.
    - All columns are created as TEXT, except for 'ID'.
    - 'ID' is assumed to be the INTEGER PRIMARY KEY.
    - foreign_keys is a list of strings like 'FOREIGN KEY (Column) REFERENCES OtherTable(OtherColumn)'
    """
    column_definitions = []
    for header in headers:
        sanitized = sanitize_name(header)
        if header.upper() == 'ID':
            column_definitions.append(f'{sanitized} INTEGER PRIMARY KEY')
        else:
            column_definitions.append(f'{sanitized} TEXT')
    
    if foreign_keys:
        column_definitions.extend(foreign_keys)

    create_sql = f"CREATE TABLE IF NOT EXISTS {sanitize_name(table_name)} ({', '.join(column_definitions)})"
    
    cursor.execute(create_sql)
    print(f"Table '{table_name}' created successfully.")

def populate_table_from_csv(conn, cursor, table_name, csv_path):
    """Populates a table from a CSV file, skipping the header."""
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = [sanitize_name(h) for h in next(reader)]
        
        for i, row in enumerate(reader, 1):
            if not row:
                print(f"Warning: Skipping empty row {i+1} in {os.path.basename(csv_path)}")
                continue
            if len(row) != len(headers):
                print(f"Error: Row {i+1} in {os.path.basename(csv_path)} has {len(row)} values, but {len(headers)} were expected. Skipping row.")
                continue

            placeholders = ', '.join(['?'] * len(headers))
            insert_sql = f"INSERT INTO {sanitize_name(table_name)} ({', '.join(headers)}) VALUES ({placeholders})"
            
            try:
                cursor.execute(insert_sql, row)
            except sqlite3.Error as e:
                print(f"Error inserting row {i+1} from {os.path.basename(csv_path)}: {e}")

    conn.commit()
    print(f"Table '{table_name}' populated from {os.path.basename(csv_path)}.")


def main():
    """Main function to initialize the database."""
    base_dir = os.path.dirname(__file__)
    db_path = os.path.join(base_dir, '..', 'data', 'enrichment.sqlite')
    debtors_csv_path = os.path.join(base_dir, '..', 'data', 'Debtors.csv')
    files_csv_path = os.path.join(base_dir, '..', 'data', 'Files.csv')

    if not os.path.exists(debtors_csv_path):
        print(f"Error: Cannot find {debtors_csv_path}")
        return
    if not os.path.exists(files_csv_path):
        print(f"Error: Cannot find {files_csv_path}")
        return

    # --- Database setup ---
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Removed existing database at {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # --- Drop existing tables (for good measure) ---
        cursor.execute('DROP TABLE IF EXISTS Files')
        cursor.execute('DROP TABLE IF EXISTS EnrichmentData')
        cursor.execute('DROP TABLE IF EXISTS Debtors')
        print("Dropped existing tables.")

        # --- Create tables from CSV headers ---
        print("Creating tables...")
        debtors_headers = get_csv_headers(debtors_csv_path)
        files_headers = get_csv_headers(files_csv_path)

        create_table_from_csv_headers(cursor, 'Debtors', debtors_headers)
        
        files_foreign_keys = [
            'FOREIGN KEY (DebtorID) REFERENCES Debtors(ID)'
        ]
        create_table_from_csv_headers(cursor, 'Files', files_headers, foreign_keys=files_foreign_keys)

        # --- Create EnrichmentData table ---
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS EnrichmentData (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            debtor_id INTEGER,
            operational_status TEXT,
            extracted_owners TEXT,
            extracted_phones TEXT,
            extracted_emails TEXT,
            extracted_addresses TEXT,
            relevant_urls TEXT,
            FOREIGN KEY (debtor_id) REFERENCES Debtors(ID)
        )
        ''')
        print("Table 'EnrichmentData' created.")

        # --- Populate tables ---
        print("Populating tables...")
        populate_table_from_csv(conn, cursor, 'Debtors', debtors_csv_path)
        populate_table_from_csv(conn, cursor, 'Files', files_csv_path)

        # --- Create indexes ---
        print("Creating indexes...")
        cursor.execute('CREATE INDEX IF NOT EXISTS IX_Debtors_FirsNameLastNameNumber ON Debtors (FirstName, LastName, Number)')
        cursor.execute('CREATE INDEX IF NOT EXISTS IX_Debtors_FirsNameLastName ON Debtors (FirstName, LastName)')
        cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS IX_Debtors_Number ON Debtors (Number)')
        cursor.execute('CREATE INDEX IF NOT EXISTS IX_Debtors_CityID ON Debtors (CityID)')
        
        cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS IX_Files_Number ON Files (Number)')
        cursor.execute('CREATE INDEX IF NOT EXISTS IX_Files_Customer ON Files (CustomerID)')
        cursor.execute('CREATE INDEX IF NOT EXISTS IX_Files_Debtor ON Files (DebtorID)')
        cursor.execute('CREATE INDEX IF NOT EXISTS IX_Files_FileState ON Files (FileStateID)')
        cursor.execute('CREATE INDEX IF NOT EXISTS IX_Files_Manager ON Files (ManagerID)')
        print("Indexes created successfully.")

    except sqlite3.Error as e:
        print(f"A database error occurred: {e}")
    except FileNotFoundError as e:
        print(f"An error occurred: {e}. Make sure the CSV files are in the data directory.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        conn.close()
        print(f"Database initialization complete. Database is at {db_path}")

if __name__ == "__main__":
    main()

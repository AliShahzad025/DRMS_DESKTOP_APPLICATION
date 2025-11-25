import mysql.connector
from config.settings import DB_CONFIG

try:
    connection = mysql.connector.connect(**DB_CONFIG)
    print("✅ Connection successful!")
    print(f"Connected to database: {connection.database}")
    
    cursor = connection.cursor()
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()
    
    print(f"\nTables in database:")
    for table in tables:
        print(f"  - {table[0]}")
    
    connection.close()
    
except mysql.connector.Error as e:
    print(f"❌ Connection failed!")
    print(f"Error: {e}")
    print("\nCheck:")
    print("  1. MySQL server is running")
    print("  2. Username and password are correct")
    print("  3. Database name exists")
    print(f"  4. Current config: {DB_CONFIG}")
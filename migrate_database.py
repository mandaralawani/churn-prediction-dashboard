"""
Database Migration Script
Migrate data from local PostgreSQL to cloud database (ElephantSQL/Supabase)
"""

import pandas as pd
from sqlalchemy import create_engine
import sys

def migrate_database():
    """Migrate database from local to cloud"""
    
    print("="*60)
    print("DATABASE MIGRATION SCRIPT")
    print("="*60)
    print()
    
    # Source database (local)
    print("📥 Source: Local PostgreSQL")
    source_password = input("Enter your LOCAL postgres password: ")
    source_url = f'postgresql://postgres:learn@localhost/churn_db'
    
    # Destination database (cloud)
    print("\n📤 Destination: Cloud Database")
    print("Paste your cloud database URL (ElephantSQL/Supabase)")
    print("Format: postgresql://username:password@host:port/database")
    dest_url = input("Cloud database URL: ").strip()
    
    if not dest_url.startswith('postgresql://'):
        print("❌ Error: URL must start with 'postgresql://'")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("Starting migration...")
    print("="*60)
    
    try:
        # Connect to source
        print("\n1️⃣ Connecting to local database...")
        source_engine = create_engine(source_url)
        source_engine.connect()
        print("   ✅ Connected to local database")
        
        # Connect to destination
        print("\n2️⃣ Connecting to cloud database...")
        dest_engine = create_engine(dest_url)
        dest_engine.connect()
        print("   ✅ Connected to cloud database")
        
        # Migrate customers table
        print("\n3️⃣ Migrating 'customers' table...")
        df_customers = pd.read_sql('SELECT * FROM customers', source_engine)
        print(f"   📊 Found {len(df_customers)} customer records")
        
        df_customers.to_sql('customers', dest_engine, if_exists='replace', index=False)
        print(f"   ✅ Migrated {len(df_customers)} customers")
        
        # Migrate ml_features (as table, not view)
        print("\n4️⃣ Migrating 'ml_features' view as table...")
        df_ml = pd.read_sql('SELECT * FROM ml_features', source_engine)
        print(f"   📊 Found {len(df_ml)} feature records")
        
        df_ml.to_sql('ml_features', dest_engine, if_exists='replace', index=False)
        print(f"   ✅ Migrated {len(df_ml)} ML features")
        
        # Verify migration
        print("\n5️⃣ Verifying migration...")
        verify_customers = pd.read_sql('SELECT COUNT(*) as count FROM customers', dest_engine)
        verify_ml = pd.read_sql('SELECT COUNT(*) as count FROM ml_features', dest_engine)
        
        print(f"   ✅ Cloud database has {verify_customers['count'][0]} customers")
        print(f"   ✅ Cloud database has {verify_ml['count'][0]} ML feature records")
        
        # Summary
        print("\n" + "="*60)
        print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"\nMigrated:")
        print(f"  - {len(df_customers)} customer records")
        print(f"  - {len(df_ml)} ML feature records")
        print(f"\nYour cloud database is ready for deployment!")
        print(f"Use this URL in your Streamlit secrets:")
        print(f"\n{dest_url}")
        print("\nParse it for secrets.toml:")
        
        # Parse URL for easy copying
        from urllib.parse import urlparse
        parsed = urlparse(dest_url)
        print("\n[database]")
        print(f'host = "{parsed.hostname}"')
        print(f'port = {parsed.port or 5432}')
        print(f'database = "{parsed.path[1:]}"')
        print(f'user = "{parsed.username}"')
        print(f'password = "{parsed.password}"')
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check your local PostgreSQL is running")
        print("2. Verify local password is correct")
        print("3. Verify cloud database URL is correct")
        print("4. Ensure cloud database is active")
        sys.exit(1)

if __name__ == "__main__":
    migrate_database()

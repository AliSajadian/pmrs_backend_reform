"""
Compatibility patch for SQL Server 2025 (version 17)
"""

def patch_mssql_for_sql_server_2025():
    try:
        from mssql import base
        
        # Add SQL Server 2025 (version 17) to the supported versions dictionary
        # Treat it as SQL Server 2022 (version 16) for compatibility
        if 17 not in base.DatabaseWrapper._sql_server_versions:
            base.DatabaseWrapper._sql_server_versions[17] = 2022
            print("✓ SQL Server 2025 (v17) added to supported versions")
        
    except ImportError:
        print("⚠ mssql package not found, skipping patch")
    except Exception as e:
        print(f"⚠ Could not apply SQL Server patch: {e}")

# Apply the patch when this module is imported
patch_mssql_for_sql_server_2025()

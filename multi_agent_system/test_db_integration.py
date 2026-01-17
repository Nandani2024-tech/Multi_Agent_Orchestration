import os
import time
from src.interface.tools import ToolRegistry
# Ensure the DB is initialized by importing it
from src.interface.database import db

def test_database_integration():
    print("🤖 --- STARTING DATABASE TEST ---")

    # 1. Check if DB file exists (it might be created on import)
    db_path = "orchestrator.db"
    if os.path.exists(db_path):
        print(f"📁 Database file found at: {os.path.abspath(db_path)}")
    else:
        print("📁 Database file will be created now...")

    # 2. Simulate an Agent saving a memory
    # The agent calls the tool "save_memory"
    print("\n📝 Agent is saving memory...")
    result_save = ToolRegistry.execute("save_memory", key="user_preference", value="Dark Mode")
    print(f"   Output: {result_save}")

    # 3. Simulate a different Agent reading that memory later
    print("\n📖 Another Agent is reading memory...")
    result_read = ToolRegistry.execute("read_memory", key="user_preference")
    print(f"   Output: {result_read}")

    # 4. Direct SQL Verification (Bypassing tools to be 100% sure)
    print("\n🔍 Verifying directly with SQL...")
    saved_value = db.get_memory("user_preference")
    if saved_value == "Dark Mode":
        print("✅ SUCCESS: Data is physically stored in SQLite.")
    else:
        print("❌ FAILURE: Data was not found in SQLite.")

    # 5. Check Audit Logs
    # (If you added the log_event hook in Step 3 of previous response)
    print("\nChecking Logs...")
    # Manually logging a test event
    db.log_event("test_script", "check_db", "Running integration test")
    
    import sqlite3
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM logs ORDER BY id DESC LIMIT 1")
    last_log = cursor.fetchone()
    conn.close()
    
    if last_log:
        print(f"✅ Log found: {last_log}")
    else:
        print("⚠️ No logs found (Did you add the logging hook? Optional)")

    print("\n🎉 DATABASE INTEGRATION TEST COMPLETE")

if __name__ == "__main__":
    test_database_integration()
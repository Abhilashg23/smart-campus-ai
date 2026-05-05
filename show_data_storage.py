#!/usr/bin/env python3
"""
Smart Campus Data Storage Demonstration Script
Shows where and how data is stored in the system
"""

import sqlite3
import os
from datetime import datetime

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_section(title):
    """Print a section header"""
    print(f"\n{'─' * 70}")
    print(f"  {title}")
    print(f"{'─' * 70}")

def show_database_info():
    """Show database file information"""
    print_header("SMART CAMPUS DATA STORAGE DEMONSTRATION")
    
    db_path = "instance/smart_campus.db"
    
    if os.path.exists(db_path):
        file_size = os.path.getsize(db_path)
        file_size_kb = file_size / 1024
        modified_time = datetime.fromtimestamp(os.path.getmtime(db_path))
        
        print(f"\n📍 Database Location:")
        print(f"   {os.path.abspath(db_path)}")
        print(f"\n📊 Database Info:")
        print(f"   Type: SQLite3")
        print(f"   Size: {file_size_kb:.2f} KB ({file_size:,} bytes)")
        print(f"   Last Modified: {modified_time.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print(f"\n❌ Database not found at: {db_path}")
        return False
    
    return True

def show_table_statistics():
    """Show statistics for all tables"""
    print_section("DATABASE TABLES & RECORD COUNTS")
    
    conn = sqlite3.connect("instance/smart_campus.db")
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = cursor.fetchall()
    
    print(f"\n{'Table Name':<25} {'Record Count':>15} {'Description':<30}")
    print(f"{'-' * 25} {'-' * 15} {'-' * 30}")
    
    table_descriptions = {
        'users': 'User accounts (all roles)',
        'departments': 'Academic departments',
        'programs': 'Academic programs',
        'events': 'Campus events',
        'attendance': 'Attendance records',
        'chat_history': 'AI chat conversations',
        'face_data': 'Face recognition data',
        'pending_registrations': 'Pending approvals'
    }
    
    total_records = 0
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        total_records += count
        description = table_descriptions.get(table_name, 'System table')
        print(f"{table_name:<25} {count:>15,} {description:<30}")
    
    print(f"{'-' * 25} {'-' * 15} {'-' * 30}")
    print(f"{'TOTAL':<25} {total_records:>15,}")
    
    conn.close()

def show_sample_data():
    """Show sample data from key tables"""
    print_section("SAMPLE DATA")
    
    conn = sqlite3.connect("instance/smart_campus.db")
    cursor = conn.cursor()
    
    # Show users by role
    print("\n👥 Users by Role:")
    cursor.execute("""
        SELECT role, COUNT(*) as count 
        FROM users 
        GROUP BY role 
        ORDER BY count DESC
    """)
    for row in cursor.fetchall():
        print(f"   {row[0]:<15} {row[1]:>5} users")
    
    # Show departments
    print("\n🏛️  Departments:")
    cursor.execute("SELECT name FROM departments ORDER BY name LIMIT 10")
    for i, row in enumerate(cursor.fetchall(), 1):
        print(f"   {i}. {row[0]}")
    
    # Show recent events
    print("\n📅 Recent Events:")
    cursor.execute("""
        SELECT title, event_date 
        FROM events 
        ORDER BY event_date DESC 
        LIMIT 5
    """)
    for row in cursor.fetchall():
        print(f"   • {row[0]} ({row[1][:10]})")
    
    # Show attendance stats
    print("\n✅ Attendance Statistics:")
    cursor.execute("SELECT COUNT(*) FROM attendance")
    total_attendance = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM attendance WHERE verification_method='face'")
    face_attendance = cursor.fetchone()[0]
    print(f"   Total Records: {total_attendance:,}")
    print(f"   Face Recognition: {face_attendance:,}")
    print(f"   Manual: {total_attendance - face_attendance:,}")
    
    # Show chat stats
    print("\n💬 Chat Statistics:")
    cursor.execute("SELECT COUNT(*) FROM chat_history")
    total_chats = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM chat_history WHERE chat_type='voice'")
    voice_chats = cursor.fetchone()[0]
    print(f"   Total Conversations: {total_chats:,}")
    print(f"   Voice Chats: {voice_chats:,}")
    print(f"   Text Chats: {total_chats - voice_chats:,}")
    
    conn.close()

def show_file_storage():
    """Show file storage locations"""
    print_section("FILE STORAGE LOCATIONS")
    
    storage_locations = [
        ("uploads/faces/", "Face recognition images"),
        ("uploads/events/", "Event files and images"),
        ("uploads/", "User profile pictures"),
        ("static/images/", "Campus photos and UI images"),
    ]
    
    for location, description in storage_locations:
        if os.path.exists(location):
            file_count = len([f for f in os.listdir(location) if os.path.isfile(os.path.join(location, f))])
            dir_size = sum(os.path.getsize(os.path.join(location, f)) 
                          for f in os.listdir(location) 
                          if os.path.isfile(os.path.join(location, f)))
            dir_size_mb = dir_size / (1024 * 1024)
            
            print(f"\n📁 {location}")
            print(f"   Purpose: {description}")
            print(f"   Files: {file_count:,}")
            print(f"   Size: {dir_size_mb:.2f} MB")
        else:
            print(f"\n📁 {location}")
            print(f"   Purpose: {description}")
            print(f"   Status: Directory not found")

def show_database_schema():
    """Show database schema for a sample table"""
    print_section("SAMPLE TABLE SCHEMA (users)")
    
    conn = sqlite3.connect("instance/smart_campus.db")
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    
    print(f"\n{'Column Name':<25} {'Type':<15} {'Nullable':<10} {'Key':<10}")
    print(f"{'-' * 25} {'-' * 15} {'-' * 10} {'-' * 10}")
    
    for col in columns:
        col_name = col[1]
        col_type = col[2]
        not_null = "NOT NULL" if col[3] else "NULL"
        is_pk = "PRIMARY" if col[5] else ""
        print(f"{col_name:<25} {col_type:<15} {not_null:<10} {is_pk:<10}")
    
    conn.close()

def main():
    """Main demonstration function"""
    try:
        # Change to script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        
        # Run demonstrations
        if show_database_info():
            show_table_statistics()
            show_sample_data()
            show_file_storage()
            show_database_schema()
            
            print_header("DEMONSTRATION COMPLETE")
            print("\n✅ All data is stored locally in SQLite database and file system")
            print("✅ No external database server required")
            print("✅ Portable and easy to backup")
            print("✅ Can be migrated to PostgreSQL/MySQL for production\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

#!/bin/bash
# Quick Data Storage Demo Script
# Run this to show where data is stored in Smart Campus

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║        SMART CAMPUS - DATA STORAGE DEMONSTRATION              ║"
echo "╚════════════════════════════════════════════════════════════════╝"

echo ""
echo "📍 DATABASE LOCATION:"
echo "   $(pwd)/instance/smart_campus.db"
echo ""

echo "📊 DATABASE FILE INFO:"
ls -lh instance/smart_campus.db | awk '{print "   Size: " $5 "\n   Modified: " $6 " " $7 " " $8}'
echo ""

echo "🗂️  DATABASE TABLES:"
sqlite3 instance/smart_campus.db ".tables" | tr '\t' '\n' | sed 's/^/   • /'
echo ""

echo "📈 RECORD COUNTS:"
echo "   Users:        $(sqlite3 instance/smart_campus.db 'SELECT COUNT(*) FROM users;')"
echo "   Departments:  $(sqlite3 instance/smart_campus.db 'SELECT COUNT(*) FROM departments;')"
echo "   Programs:     $(sqlite3 instance/smart_campus.db 'SELECT COUNT(*) FROM programs;')"
echo "   Events:       $(sqlite3 instance/smart_campus.db 'SELECT COUNT(*) FROM events;')"
echo "   Attendance:   $(sqlite3 instance/smart_campus.db 'SELECT COUNT(*) FROM attendance;')"
echo "   Chat History: $(sqlite3 instance/smart_campus.db 'SELECT COUNT(*) FROM chat_history;')"
echo "   Face Data:    $(sqlite3 instance/smart_campus.db 'SELECT COUNT(*) FROM face_data;')"
echo ""

echo "👥 USERS BY ROLE:"
sqlite3 instance/smart_campus.db "SELECT '   ' || role || ': ' || COUNT(*) FROM users GROUP BY role;" 
echo ""

echo "📁 FILE STORAGE LOCATIONS:"
for dir in "uploads/faces" "uploads/events" "uploads" "static/images"; do
    if [ -d "$dir" ]; then
        count=$(find "$dir" -type f | wc -l | tr -d ' ')
        echo "   • $dir/ ($count files)"
    fi
done
echo ""

echo "✅ All data stored locally - No external database server required!"
echo ""
echo "💡 For detailed view, run: python3 show_data_storage.py"
echo ""

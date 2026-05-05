#!/bin/bash
# Smart Campus Startup Script

cd "$(dirname "$0")"
source myenv/bin/activate

echo "🚀 Starting Smart Campus System..."
echo "📍 Application will be available at: http://localhost:5001"
echo ""
echo "Default Login Credentials:"
echo "  Admin:   admin / Admin@123"
echo "  Student: student1 / Student@123"
echo "  Faculty: faculty1 / Faculty@123"
echo ""
echo "Press CTRL+C to stop the server"
echo "================================"
echo ""

# Run on port 5001 to avoid conflicts
export FLASK_RUN_PORT=5001
python3 -c "
from app import create_app
app = create_app('development')
print('✅ Server starting...')
app.run(host='0.0.0.0', port=5001, debug=True, use_reloader=False)
"

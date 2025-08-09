#!/bin/bash
# Network Management System Runner with Neo4j
# Runs all components with proper Neo4j connection

echo "🚀 AI-POWERED NETWORK MANAGEMENT WITH NEO4J"
echo "============================================================"

# Activate virtual environment
echo "🔧 Activating Neo4j virtual environment..."
source neo4j-env/bin/activate

echo "✅ Virtual environment activated"

# Check Neo4j connection
echo "🔌 Testing Neo4j connection..."
python3 -c "
from neo4j import GraphDatabase
try:
    driver = GraphDatabase.driver('neo4j://localhost:7687', auth=('neo4j', 'password'))
    with driver.session() as session:
        result = session.run('MATCH (d:Device) RETURN count(d) as device_count')
        count = result.single()['device_count']
        print(f'✅ Neo4j connected: {count} devices in topology')
    driver.close()
except Exception as e:
    print(f'❌ Neo4j connection failed: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🌐 ACCESS POINTS:"
    echo "   Neo4j Browser: http://localhost:7474 (neo4j/password)"
    echo "   Chat Copilot: http://localhost:11000"
    echo "   Grafana: http://localhost:3000"
    echo ""
    echo "🎯 READY TO RUN:"
    echo "   python3 automated-health-assessment.py"
    echo "   python3 generate-executive-report.py"
    echo "   python3 test-implementation-status.py"
    echo ""
    echo "💬 NATURAL LANGUAGE QUERIES (Chat Copilot):"
    echo "   'Show me network topology for all locations'"
    echo "   'What devices need immediate attention?'"
    echo "   'Generate an executive network health summary'"
else
    echo "❌ Neo4j connection failed. Please check the setup."
    exit 1
fi
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY main.py .
COPY manifest.json .
COPY test_plugin.py .
COPY README.md .

# Create a simple demo script
RUN echo '#!/usr/bin/env python3\n\
import asyncio\n\
import sys\n\
from main import Tools\n\
\n\
async def demo():\n\
    tools = Tools()\n\
    \n\
    print("🏀🏈 Sports Score Tracker Demo 🏈🏀\\n")\n\
    \n\
    if len(sys.argv) > 1:\n\
        command = sys.argv[1].lower()\n\
        \n\
        if command == "teams":\n\
            result = await tools.get_team_info({}, "all")\n\
        elif command == "scores":\n\
            sport = sys.argv[2] if len(sys.argv) > 2 else "both"\n\
            result = await tools.get_live_scores({}, sport)\n\
        elif command == "schedule":\n\
            if len(sys.argv) < 3:\n\
                print("Usage: demo.py schedule <team>")\n\
                return\n\
            team = sys.argv[2]\n\
            days = int(sys.argv[3]) if len(sys.argv) > 3 else 7\n\
            result = await tools.get_team_schedule({}, team, days)\n\
        else:\n\
            print("Available commands:")\n\
            print("  teams           - Show all tracked teams")\n\
            print("  scores [sport]  - Show live scores (basketball|football|nfl|both)")\n\
            print("  schedule <team> [days] - Show team schedule")\n\
            return\n\
    else:\n\
        print("🎯 Available commands:")\n\
        print("  teams           - Show all tracked teams")\n\
        print("  scores [sport]  - Show live scores (basketball|football|nfl|both)")\n\
        print("  schedule <team> [days] - Show team schedule")\n\
        print("\\nExamples:")\n\
        print("  python demo.py teams")\n\
        print("  python demo.py scores nfl")\n\
        print("  python demo.py schedule panthers 14")\n\
        return\n\
    \n\
    print(result)\n\
\n\
if __name__ == "__main__":\n\
    asyncio.run(demo())\n\
' > demo.py && chmod +x demo.py

# Expose port for potential web interface
EXPOSE 8000

# Default command shows help
CMD ["python", "demo.py"]
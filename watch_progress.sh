#!/bin/bash
# Watch benchmark progress in real-time

LATEST_LOG=$(ls -t /home/hor20kud/aug/EPA/logs/benchmark_*_out.txt 2>/dev/null | head -1)

if [ -z "$LATEST_LOG" ]; then
    echo "No benchmark logs found yet"
    exit 1
fi

echo "Monitoring: $LATEST_LOG"
echo "Press Ctrl+C to stop watching"
echo "========================================"
echo ""

tail -f "$LATEST_LOG"

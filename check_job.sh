#!/bin/bash
# Quick job status checker for EPA benchmark

echo "=== Job Status ==="
squeue -u $USER

echo ""
echo "=== Latest Log Files ==="
ls -lht /home/hor20kud/aug/EPA/logs/ | head -5

echo ""
echo "=== Last 20 lines of most recent output ==="
LATEST_OUT=$(ls -t /home/hor20kud/aug/EPA/logs/benchmark_*_out.txt 2>/dev/null | head -1)
if [ -n "$LATEST_OUT" ]; then
    echo "File: $LATEST_OUT"
    tail -20 "$LATEST_OUT"
else
    echo "No output files found yet"
fi

echo ""
echo "=== Any errors? ==="
LATEST_ERR=$(ls -t /home/hor20kud/aug/EPA/logs/benchmark_*_err.txt 2>/dev/null | head -1)
if [ -n "$LATEST_ERR" ] && [ -s "$LATEST_ERR" ]; then
    echo "File: $LATEST_ERR"
    tail -20 "$LATEST_ERR"
else
    echo "No errors in latest error log"
fi

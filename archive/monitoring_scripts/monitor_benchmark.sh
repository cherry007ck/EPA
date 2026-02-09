#!/bin/bash
# Monitor EPA Benchmark Job

JOB_ID=${1:-20736984}

echo "=========================================="
echo "EPA Benchmark Monitor"
echo "=========================================="
echo "Job ID: $JOB_ID"
echo ""

# Check job status
echo "=== Job Status ==="
squeue -u $USER -j $JOB_ID
echo ""

# Show recent output
echo "=== Latest Output (last 20 lines) ==="
OUTPUT_FILE="/home/hor20kud/aug/EPA/logs/benchmark_${JOB_ID}_out.txt"
if [ -f "$OUTPUT_FILE" ]; then
    tail -20 "$OUTPUT_FILE"
else
    echo "Output file not yet created: $OUTPUT_FILE"
fi
echo ""

# Show recent errors
echo "=== Latest Errors (last 10 lines) ==="
ERROR_FILE="/home/hor20kud/aug/EPA/logs/benchmark_${JOB_ID}_err.txt"
if [ -f "$ERROR_FILE" ]; then
    tail -10 "$ERROR_FILE"
else
    echo "Error file not yet created: $ERROR_FILE"
fi
echo ""

echo "=========================================="
echo "To cancel job: scancel $JOB_ID"
echo "To watch output: tail -f $OUTPUT_FILE"
echo "To watch errors: tail -f $ERROR_FILE"
echo "=========================================="

#!/bin/bash
# Monitor EPA benchmark jobs progress

echo "=========================================="
echo "EPA Benchmark Job Monitor"
echo "=========================================="
echo "Timestamp: $(date)"
echo ""

# Check running jobs
echo "Running Jobs:"
squeue -u $USER -o "%.10i %.10P %.30j %.8u %.2t %.10M %.6D %R" | grep "epa-"

echo ""
echo "=========================================="
echo "Recent Log Files:"
echo "=========================================="
ls -lht logs/benchmark_epa-*_out.txt 2>/dev/null | head -6

echo ""
echo "=========================================="
echo "Latest Progress Snippets:"
echo "=========================================="

# Show latest progress from each active job
for log in $(ls -t logs/benchmark_epa-*_out.txt 2>/dev/null | head -3); do
    jobname=$(basename "$log" | sed 's/benchmark_//' | sed 's/_out.txt//')
    echo ""
    echo "--- $jobname ---"
    
    # Find last training line
    grep -E "(Training:|Epoch [0-9]+/[0-9]+:|✅)" "$log" | tail -5
done

echo ""
echo "=========================================="
echo "Result Files:"
echo "=========================================="
ls -lht benchmark_results_*.json 2>/dev/null | head -10

echo ""
echo "=========================================="
echo "To view live updates:"
echo "  tail -f logs/benchmark_epa-<dataset>_<jobid>_out.txt"
echo ""
echo "To check errors:"
echo "  tail -f logs/benchmark_epa-<dataset>_<jobid>_err.txt"
echo ""
echo "To summarize completed results:"
echo "  python summarize_results.py"
echo "=========================================="

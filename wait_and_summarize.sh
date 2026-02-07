#!/bin/bash
# Wait for all benchmark jobs to complete and generate final report

echo "=========================================="
echo "EPA Benchmark Completion Checker"
echo "=========================================="

# Check if any jobs are still running
while true; do
    running_jobs=$(squeue -u $USER -o "%.30j" | grep "epa-" | wc -l)
    
    if [ $running_jobs -eq 0 ]; then
        echo "✅ All jobs completed!"
        break
    else
        echo "⏳ $running_jobs job(s) still running... ($(date +%H:%M:%S))"
        sleep 300  # Check every 5 minutes
    fi
done

echo ""
echo "=========================================="
echo "Generating Results Summary"
echo "=========================================="

cd /home/hor20kud/aug/EPA
source epa_venv/bin/activate
python summarize_results.py | tee FINAL_RESULTS_SUMMARY.txt

echo ""
echo "=========================================="
echo "Results saved to: FINAL_RESULTS_SUMMARY.txt"
echo "=========================================="
echo ""
echo "Available result files:"
ls -lh benchmark_results_*.json

echo ""
echo "✅ Benchmark complete! Check FINAL_RESULTS_SUMMARY.txt for details."

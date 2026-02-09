#!/bin/bash
# Check progress of remote_homology_fold benchmark

echo "================================================================================"
echo "Remote Homology (Fold) Benchmark Progress"
echo "================================================================================"
echo ""

# Check job status
echo "📊 Job Status:"
squeue -j 20807682 -o "%.10i %.15j %.8u %.2t %.10M %.6D %R"
echo ""

# Check if results file exists
RESULTS_FILE=$(ls -t benchmark_results_remote_homology_fold_*.json 2>/dev/null | head -1)
if [ -f "$RESULTS_FILE" ]; then
    echo "✅ Results file found: $RESULTS_FILE"
    echo ""
    echo "📈 Quick Summary:"
    python3 << PYTHON_EOF
import json
with open("$RESULTS_FILE", 'r') as f:
    results = json.load(f)
baseline = next((r for r in results if r['augmentation'] == 'baseline'), None)
best = max(results, key=lambda x: x['test_acc'])
print(f"  Methods tested: {len(results)}/24")
if baseline:
    print(f"  Baseline accuracy: {baseline['test_acc']:.4f}")
print(f"  Best so far: {best['augmentation']} - {best['test_acc']:.4f}")
PYTHON_EOF
else
    echo "⏳ No results file yet - job still running"
    echo ""
    echo "Expected output file: benchmark_results_remote_homology_fold_<timestamp>.json"
fi

echo ""
echo "================================================================================"
echo "To monitor in real-time, run: watch -n 30 ./check_fold_progress.sh"
echo "================================================================================"

#!/bin/bash
# Run EPA Benchmark - FIXED VERSION

echo "=========================================="
echo "EPA Augmentation Benchmark (FIXED)"
echo "=========================================="
echo "Testing all 23 augmentations individually"
echo "Expected runtime: ~4-6 hours (GPU) or ~8-12 hours (CPU)"
echo ""
echo "Results: EPA/benchmark_results_final_*.json"
echo ""

# Clear GPU memory cache
echo "Clearing GPU cache..."
python3 -c "import torch; torch.cuda.empty_cache()" 2>/dev/null || true

read -p "Press Enter to start or Ctrl+C to cancel..."

cd "$(dirname "$0")"
../venv/bin/python benchmark_FIXED.py 2>&1 | tee benchmark_log_$(date +%Y%m%d_%H%M%S).txt

echo ""
echo "=========================================="
echo "Benchmark Complete!"
echo "=========================================="

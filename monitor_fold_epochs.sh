#!/bin/bash
# Monitor epoch progress for remote_homology_fold benchmark

LOG_FILE="logs/benchmark_epa-benchmark_20807682_out.txt"

clear
echo "================================================================================"
echo "Remote Homology (Fold) Benchmark - LIVE EPOCH MONITORING"
echo "================================================================================"
echo "Job ID: 20807682 | GPU: gpu104 | Dataset: 12,313 sequences | Classes: 1,195"
echo ""

# Check if log file exists
if [ ! -f "$LOG_FILE" ]; then
    echo "❌ Log file not found yet. Job may be starting..."
    exit 1
fi

# Get current augmentation method
CURRENT_AUG=$(grep -E "^Training: " "$LOG_FILE" | tail -1)
echo "🔄 Current Augmentation: $CURRENT_AUG"
echo ""

# Count completed augmentations
COMPLETED=$(grep -c "^Training: " "$LOG_FILE")
echo "📊 Progress: $COMPLETED/24 augmentation methods completed"
echo ""

# Show last 15 epochs
echo "📈 Recent Epochs:"
echo "--------------------------------------------------------------------------------"
tail -n 100 "$LOG_FILE" | grep -E "^Epoch [0-9]+/[0-9]+:" | tail -15
echo ""

# Get best validation accuracy so far
BEST_VALID=$(tail -n 100 "$LOG_FILE" | grep -E "^Epoch [0-9]+/[0-9]+:" | tail -30 | \
    awk -F'Valid=' '{print $2}' | awk -F',' '{print $1}' | sort -rn | head -1)

if [ ! -z "$BEST_VALID" ]; then
    echo "🏆 Best Validation Accuracy (current method): $BEST_VALID"
fi

echo ""
echo "================================================================================"
echo "Last update: $(date)"
echo "To refresh: ./monitor_fold_epochs.sh"
echo "For auto-refresh: watch -n 10 ./monitor_fold_epochs.sh"
echo "================================================================================"

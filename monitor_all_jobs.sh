#!/bin/bash
# Monitor all running EPA benchmark jobs

echo "=========================================="
echo "EPA Benchmark Job Status"
echo "Date: $(date)"
echo "=========================================="
echo ""

# Check SLURM queue
echo "SLURM Queue:"
squeue -u $USER -o "%.10i %.20j %.8T %.10M %.9l %R" | grep -E "JOBID|epa-benchmark|beta_lactamase|secondary_structure|human_ppi|solubility"
echo ""

# Check each job's progress
LOGS_DIR="/home/hor20kud/aug/EPA/logs"

echo "=========================================="
echo "Job Progress Summary:"
echo "=========================================="

# Remote homology fold (job 20807682)
if [ -f "$LOGS_DIR/benchmark_epa-benchmark_20807682_out.txt" ]; then
    echo ""
    echo "1. REMOTE_HOMOLOGY_FOLD (Job 20807682):"
    LAST_LINE=$(tail -1 "$LOGS_DIR/benchmark_epa-benchmark_20807682_out.txt" 2>/dev/null)
    EPOCH_LINE=$(grep -E "Epoch [0-9]+/30:" "$LOGS_DIR/benchmark_epa-benchmark_20807682_out.txt" 2>/dev/null | tail -1)
    AUG_LINE=$(grep -E "Training:" "$LOGS_DIR/benchmark_epa-benchmark_20807682_out.txt" 2>/dev/null | tail -1)
    echo "   Current: $AUG_LINE"
    echo "   Latest:  $EPOCH_LINE"
fi

# Beta lactamase (job 20808638)
if [ -f "$LOGS_DIR/beta_lactamase_20808638_out.txt" ]; then
    echo ""
    echo "2. BETA_LACTAMASE - Regression (Job 20808638):"
    EPOCH_LINE=$(grep -E "Epoch [0-9]+/30:" "$LOGS_DIR/beta_lactamase_20808638_out.txt" 2>/dev/null | tail -1)
    AUG_LINE=$(grep -E "Training:" "$LOGS_DIR/beta_lactamase_20808638_out.txt" 2>/dev/null | tail -1)
    echo "   Current: $AUG_LINE"
    echo "   Latest:  $EPOCH_LINE"
fi

# Secondary structure (job 20808639)
if [ -f "$LOGS_DIR/secondary_structure_20808639_out.txt" ]; then
    echo ""
    echo "3. SECONDARY_STRUCTURE - Residue Classification (Job 20808639):"
    EPOCH_LINE=$(grep -E "Epoch [0-9]+/30:" "$LOGS_DIR/secondary_structure_20808639_out.txt" 2>/dev/null | tail -1)
    AUG_LINE=$(grep -E "Training:" "$LOGS_DIR/secondary_structure_20808639_out.txt" 2>/dev/null | tail -1)
    COMPLETED=$(grep -c "✅" "$LOGS_DIR/secondary_structure_20808639_out.txt" 2>/dev/null)
    echo "   Current: $AUG_LINE"
    echo "   Latest:  $EPOCH_LINE"
    echo "   Completed augmentations: $COMPLETED/23"
fi

# Human PPI (job 20808640)
if [ -f "$LOGS_DIR/human_ppi_20808640_out.txt" ]; then
    echo ""
    echo "4. HUMAN_PPI - PPI Classification (Job 20808640):"
    EPOCH_LINE=$(grep -E "Epoch [0-9]+/30:" "$LOGS_DIR/human_ppi_20808640_out.txt" 2>/dev/null | tail -1)
    AUG_LINE=$(grep -E "Training:" "$LOGS_DIR/human_ppi_20808640_out.txt" 2>/dev/null | tail -1)
    COMPLETED=$(grep -c "✅" "$LOGS_DIR/human_ppi_20808640_out.txt" 2>/dev/null)
    echo "   Current: $AUG_LINE"
    echo "   Latest:  $EPOCH_LINE"
    echo "   Completed augmentations: $COMPLETED/23"
fi

# Solubility (job 20808641)
if [ -f "$LOGS_DIR/solubility_20808641_out.txt" ]; then
    echo ""
    echo "5. SOLUBILITY - Binary Classification (Job 20808641):"
    EPOCH_LINE=$(grep -E "Epoch [0-9]+/30:" "$LOGS_DIR/solubility_20808641_out.txt" 2>/dev/null | tail -1)
    AUG_LINE=$(grep -E "Training:" "$LOGS_DIR/solubility_20808641_out.txt" 2>/dev/null | tail -1)
    COMPLETED=$(grep -c "✅" "$LOGS_DIR/solubility_20808641_out.txt" 2>/dev/null)
    echo "   Current: $AUG_LINE"
    echo "   Latest:  $EPOCH_LINE"
    echo "   Completed augmentations: $COMPLETED/23"
fi

echo ""
echo "=========================================="
echo "To monitor in real-time: watch -n 30 ./monitor_all_jobs.sh"
echo "=========================================="

#!/bin/bash

# Master launch script for all LSTM EPA benchmarks
# Creates and launches all 7 LSTM dataset benchmarks

echo "=========================================="
echo "Launching All LSTM EPA Benchmarks"
echo "=========================================="

# Navigate to EPA directory
cd /home/hor20kud/aug/EPA

# Ensure logs directory exists
mkdir -p logs

# Track job IDs
declare -a JOB_IDS
declare -a JOB_NAMES

# Submit all jobs
echo -e "\nSubmitting LSTM jobs..."

# 1. Beta Lactamase (Regression) - 12h, 32GB
JOB_ID=$(sbatch scripts/slurm/lstm_beta_lactamase.sbatch | awk '{print $4}')
JOB_IDS+=($JOB_ID)
JOB_NAMES+=("beta_lactamase")
echo "✓ beta_lactamase: Job ID $JOB_ID"

# 2. Secondary Structure (Residue-level) - 12h, 32GB
JOB_ID=$(sbatch scripts/slurm/lstm_secondary_structure.sbatch | awk '{print $4}')
JOB_IDS+=($JOB_ID)
JOB_NAMES+=("secondary_structure")
echo "✓ secondary_structure: Job ID $JOB_ID"

# 3. Human PPI (Binary, Large) - 48h, 48GB
JOB_ID=$(sbatch scripts/slurm/lstm_human_ppi.sbatch | awk '{print $4}')
JOB_IDS+=($JOB_ID)
JOB_NAMES+=("human_ppi")
echo "✓ human_ppi: Job ID $JOB_ID"

# 4. Solubility (Binary, Very Large) - 48h, 48GB
JOB_ID=$(sbatch scripts/slurm/lstm_solubility.sbatch | awk '{print $4}')
JOB_IDS+=($JOB_ID)
JOB_NAMES+=("solubility")
echo "✓ solubility: Job ID $JOB_ID"

# 5. Subcellular Localization (10-class) - 24h, 48GB
JOB_ID=$(sbatch scripts/slurm/lstm_subcellular_localization.sbatch | awk '{print $4}')
JOB_IDS+=($JOB_ID)
JOB_NAMES+=("subcellular_localization")
echo "✓ subcellular_localization: Job ID $JOB_ID"

# 6. Subcellular Localization 2 (3-class) - 12h, 32GB
JOB_ID=$(sbatch scripts/slurm/lstm_subcellular_localization_2.sbatch | awk '{print $4}')
JOB_IDS+=($JOB_ID)
JOB_NAMES+=("subcellular_localization_2")
echo "✓ subcellular_localization_2: Job ID $JOB_ID"

# 7. Yeast PPI (Binary) - 24h, 48GB
JOB_ID=$(sbatch scripts/slurm/lstm_yeast_ppi.sbatch | awk '{print $4}')
JOB_IDS+=($JOB_ID)
JOB_NAMES+=("yeast_ppi")
echo "✓ yeast_ppi: Job ID $JOB_ID"

echo -e "\n=========================================="
echo "All LSTM jobs submitted!"
echo "=========================================="
echo -e "\nJob Summary:"
for i in "${!JOB_IDS[@]}"; do
    echo "  ${JOB_NAMES[$i]}: ${JOB_IDS[$i]}"
done

echo -e "\n=========================================="
echo "Monitoring Commands:"
echo "=========================================="
echo "Check job status:"
echo "  squeue -u \$USER"
echo ""
echo "Check specific job:"
echo "  squeue -j <JOB_ID>"
echo ""
echo "View live output:"
echo "  tail -f logs/lstm_*_out.txt"
echo ""
echo "View live errors:"
echo "  tail -f logs/lstm_*_err.txt"
echo ""
echo "Cancel all jobs:"
echo "  scancel ${JOB_IDS[@]}"
echo ""
echo "Results will be saved to: results/lstm/"
echo "=========================================="

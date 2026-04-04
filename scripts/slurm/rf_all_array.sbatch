#!/bin/bash
#SBATCH --job-name=rf_epa_array
#SBATCH --output=logs/rf_array_%A_%a_out.txt
#SBATCH --error=logs/rf_array_%A_%a_err.txt
#SBATCH --partition=uds-hub
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=24:00:00
#SBATCH --array=0-5
#
# ─────────────────────────────────────────────────────────────────────────────
# EPA Random Forest — SLURM Job Array (runs all 6 pending RF datasets in parallel)
#
# Usage:
#   sbatch scripts/slurm/rf_all_array.sbatch
#
# This submits 6 tasks (indices 0-5), one per dataset.
# All tasks run with the SAME resource request; the largest dataset (human_ppi)
# determines the ceiling: 16 CPUs, 64 GB, 24 h.
# ─────────────────────────────────────────────────────────────────────────────

# Dataset list — index maps to SLURM_ARRAY_TASK_ID
DATASETS=(
    "beta_lactamase"              # 0  ~4K  regression
    "subcellular_localization"    # 1  ~22K multi-class (10)
    "subcellular_localization_2"  # 2  ~6K  binary
    "yeast_ppi"                   # 3  ~11K binary
    "human_ppi"                   # 4  ~35K binary  (capped at 15K in config)
    "remote_homology_fold"        # 5  ~12K multi-class (1195-class, capped 10K)
)

DATASET="${DATASETS[$SLURM_ARRAY_TASK_ID]}"

echo "=========================================="
echo "RF EPA Benchmark — Array Job"
echo "Array Task:  $SLURM_ARRAY_TASK_ID  →  $DATASET"
echo "Array ID:    $SLURM_ARRAY_JOB_ID"
echo "Job ID:      $SLURM_JOB_ID"
echo "Node:        $SLURM_NODELIST"
echo "CPUs:        $SLURM_CPUS_PER_TASK"
echo "Start:       $(date)"
echo "=========================================="

# ── Environment setup ────────────────────────────────────────────────────────
cd /home/hor20kud/aug/EPA
source epa_venv/bin/activate

mkdir -p results/random_forest logs

# ── Run benchmark ────────────────────────────────────────────────────────────
echo -e "\nStarting Random Forest benchmark for: ${DATASET}"
python run_benchmark.py \
    --model random_forest \
    --dataset "${DATASET}" \
    --output-dir results/random_forest

EXIT_CODE=$?

echo "=========================================="
echo "Dataset: ${DATASET}"
echo "Exit code: ${EXIT_CODE}"
echo "End: $(date)"
echo "=========================================="

exit $EXIT_CODE

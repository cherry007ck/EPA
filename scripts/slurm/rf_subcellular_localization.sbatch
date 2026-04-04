#!/bin/bash
#SBATCH --job-name=rf_subcel
#SBATCH --output=logs/rf_subcellular_localization_%j_out.txt
#SBATCH --error=logs/rf_subcellular_localization_%j_err.txt
#SBATCH --partition=uds-hub
#SBATCH --cpus-per-task=16
#SBATCH --mem=48G
#SBATCH --time=12:00:00
# Random Forest — Subcellular Localization (10-class, ~22K samples)
# No GPU needed; RF runs fully on CPU with n_jobs=-1
# Expected runtime: ~6-10 hours (24 augmentations × RF fit)

echo "=========================================="
echo "RF Subcellular Localization EPA Benchmark"
echo "Job ID: $SLURM_JOB_ID"
echo "Node:   $SLURM_NODELIST"
echo "CPUs:   $SLURM_CPUS_PER_TASK"
echo "Start:  $(date)"
echo "=========================================="

cd /home/hor20kud/aug/EPA
source epa_venv/bin/activate

mkdir -p results/random_forest logs

echo -e "\nStarting Random Forest benchmark for subcellular_localization..."
python run_benchmark.py \
    --model random_forest \
    --dataset subcellular_localization \
    --output-dir results/random_forest

echo "=========================================="
echo "End: $(date)"
echo "=========================================="

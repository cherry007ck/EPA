#!/bin/bash
#SBATCH --job-name=rf_fold
#SBATCH --output=logs/rf_remote_homology_fold_%j_out.txt
#SBATCH --error=logs/rf_remote_homology_fold_%j_err.txt
#SBATCH --partition=uds-hub
#SBATCH --cpus-per-task=16
#SBATCH --mem=48G
#SBATCH --time=12:00:00
# Random Forest — Remote Homology Fold (1195-class, ~12K samples; capped at 10K)
# No GPU needed; RF runs fully on CPU with n_jobs=-1
# Expected runtime: ~5-10 hours (24 augmentations × RF fit; 1195 classes expensive)

echo "=========================================="
echo "RF Remote Homology Fold EPA Benchmark"
echo "Job ID: $SLURM_JOB_ID"
echo "Node:   $SLURM_NODELIST"
echo "CPUs:   $SLURM_CPUS_PER_TASK"
echo "Start:  $(date)"
echo "=========================================="

cd /home/hor20kud/aug/EPA
source epa_venv/bin/activate

mkdir -p results/random_forest logs

echo -e "\nStarting Random Forest benchmark for remote_homology_fold..."
python run_benchmark.py \
    --model random_forest \
    --dataset remote_homology_fold \
    --output-dir results/random_forest

echo "=========================================="
echo "End: $(date)"
echo "=========================================="

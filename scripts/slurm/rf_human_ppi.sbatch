#!/bin/bash
#SBATCH --job-name=rf_human_ppi
#SBATCH --output=logs/rf_human_ppi_%j_out.txt
#SBATCH --error=logs/rf_human_ppi_%j_err.txt
#SBATCH --partition=uds-hub
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=24:00:00
# Random Forest — Human PPI (binary classification, ~35K samples; capped at max_samples=15000)
# No GPU needed; RF runs fully on CPU with n_jobs=-1
# Expected runtime: ~8-16 hours (24 augmentations × RF fit on 15K samples)

echo "=========================================="
echo "RF Human PPI EPA Benchmark"
echo "Job ID: $SLURM_JOB_ID"
echo "Node:   $SLURM_NODELIST"
echo "CPUs:   $SLURM_CPUS_PER_TASK"
echo "Start:  $(date)"
echo "=========================================="

cd /home/hor20kud/aug/EPA
source epa_venv/bin/activate

mkdir -p results/random_forest logs

echo -e "\nStarting Random Forest benchmark for human_ppi..."
python run_benchmark.py \
    --model random_forest \
    --dataset human_ppi \
    --output-dir results/random_forest

echo "=========================================="
echo "End: $(date)"
echo "=========================================="

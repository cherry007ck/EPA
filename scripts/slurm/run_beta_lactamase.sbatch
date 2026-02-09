#!/bin/bash
#SBATCH --job-name=beta_lactamase
#SBATCH --output=logs/beta_lactamase_%j_out.txt
#SBATCH --error=logs/beta_lactamase_%j_err.txt
#SBATCH --partition=uds-hub
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=12:00:00

# Beta-lactamase Regression Benchmark
# Dataset: 4,158 samples, regression task
# Expected runtime: ~6-8 hours

echo "=========================================="
echo "Beta-lactamase EPA Benchmark"
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURM_NODELIST"
echo "Start: $(date)"
echo "=========================================="

# Setup
cd /home/hor20kud/aug/EPA
source epa_venv/bin/activate

# GPU info
nvidia-smi

# Run benchmark
echo -e "\nStarting benchmark for beta_lactamase..."
python universal_benchmark.py --dataset beta_lactamase --epochs 30 --batch_size 64

echo "=========================================="
echo "End: $(date)"
echo "=========================================="

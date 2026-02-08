#!/bin/bash
#SBATCH --job-name=solubility
#SBATCH --output=logs/solubility_%j_out.txt
#SBATCH --error=logs/solubility_%j_err.txt
#SBATCH --partition=uds-hub
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=48G
#SBATCH --time=24:00:00

# Solubility Binary Classification Benchmark
# Dataset: 62,479 samples, binary classification
# Expected runtime: ~12-20 hours

echo "=========================================="
echo "Solubility EPA Benchmark"
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
echo -e "\nStarting benchmark for solubility..."
python universal_benchmark.py --dataset solubility --epochs 30 --batch_size 32

echo "=========================================="
echo "End: $(date)"
echo "=========================================="

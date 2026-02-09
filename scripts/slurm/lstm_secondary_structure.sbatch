#!/bin/bash
#SBATCH --job-name=lstm_secondary_struct
#SBATCH --output=logs/lstm_secondary_struct_%j_out.txt
#SBATCH --error=logs/lstm_secondary_struct_%j_err.txt
#SBATCH --partition=uds-hub
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=12:00:00

# LSTM Secondary Structure Prediction Benchmark
# Dataset: 8,678 samples, 3-class per residue classification
# Model: LSTM
# Expected runtime: ~4-6 hours

echo "=========================================="
echo "LSTM Secondary Structure EPA Benchmark"
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURM_NODELIST"
echo "Start: $(date)"
echo "=========================================="

# Setup
cd /home/hor20kud/aug/EPA
source epa_venv/bin/activate

# GPU info
nvidia-smi

# Run benchmark with LSTM
echo -e "\nStarting LSTM benchmark for secondary_structure..."
python run_benchmark.py --model lstm --dataset secondary_structure --epochs 30 --batch-size 64 --output-dir results/lstm

echo "=========================================="
echo "End: $(date)"
echo "=========================================="

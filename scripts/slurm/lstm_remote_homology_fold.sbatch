#!/bin/bash
#SBATCH --job-name=lstm_remote_fold
#SBATCH --output=logs/lstm_remote_homology_fold_%j_out.txt
#SBATCH --error=logs/lstm_remote_homology_fold_%j_err.txt
#SBATCH --partition=uds-hub
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=48G
#SBATCH --time=24:00:00

# LSTM Remote Homology Fold Classification Benchmark
# Dataset: ~12K samples, 1195-class fold classification
# Model: Bidirectional LSTM (batch_size=32, larger output layer for 1195 classes)
# Expected runtime: ~12-20 hours (1195 classes is expensive)

echo "=========================================="
echo "LSTM Remote Homology Fold EPA Benchmark"
echo "Job ID: $SLURM_JOB_ID"
echo "Node:   $SLURM_NODELIST"
echo "Start:  $(date)"
echo "=========================================="

# Setup
cd /home/hor20kud/aug/EPA
source epa_venv/bin/activate

# GPU info
nvidia-smi

# Run benchmark with LSTM
echo -e "\nStarting LSTM benchmark for remote_homology_fold..."
python run_benchmark.py \
    --model lstm \
    --dataset remote_homology_fold \
    --epochs 30 \
    --batch-size 32 \
    --output-dir results/lstm

echo "=========================================="
echo "End: $(date)"
echo "=========================================="

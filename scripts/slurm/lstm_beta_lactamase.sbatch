#!/bin/bash
#SBATCH --job-name=lstm_beta_lactamase
#SBATCH --output=logs/lstm_beta_lactamase_%j_out.txt
#SBATCH --error=logs/lstm_beta_lactamase_%j_err.txt
#SBATCH --partition=uds-hub
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=12:00:00

# LSTM Beta-lactamase Regression Benchmark
# Dataset: 4,158 samples, regression task
# Model: LSTM
# Expected runtime: ~6-8 hours

echo "=========================================="
echo "LSTM Beta-lactamase EPA Benchmark"
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
echo -e "\nStarting LSTM benchmark for beta_lactamase..."
python run_benchmark.py --model lstm --dataset beta_lactamase --epochs 30 --batch-size 64 --output-dir results/lstm

echo "=========================================="
echo "End: $(date)"
echo "=========================================="

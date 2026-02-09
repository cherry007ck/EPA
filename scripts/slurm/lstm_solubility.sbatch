#!/bin/bash
#SBATCH --job-name=lstm_solubility
#SBATCH --output=logs/lstm_solubility_%j_out.txt
#SBATCH --error=logs/lstm_solubility_%j_err.txt
#SBATCH --partition=uds-hub
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=48G
#SBATCH --time=48:00:00

# LSTM Solubility Binary Classification Benchmark
# Dataset: 62,478 samples, protein solubility prediction
# Model: LSTM
# Expected runtime: ~24-36 hours

echo "=========================================="
echo "LSTM Solubility EPA Benchmark"
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
echo -e "\nStarting LSTM benchmark for solubility..."
python run_benchmark.py --model lstm --dataset solubility --epochs 30 --batch-size 32 --output-dir results/lstm

echo "=========================================="
echo "End: $(date)"
echo "=========================================="

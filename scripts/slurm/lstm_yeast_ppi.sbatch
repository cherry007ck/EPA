#!/bin/bash
#SBATCH --job-name=lstm_yeast_ppi
#SBATCH --output=logs/lstm_yeast_ppi_%j_out.txt
#SBATCH --error=logs/lstm_yeast_ppi_%j_err.txt
#SBATCH --partition=uds-hub
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=48G
#SBATCH --time=24:00:00

# LSTM Yeast PPI Binary Classification Benchmark
# Dataset: 11,188 samples, dual-sequence PPI classification
# Model: LSTM
# Expected runtime: ~8-12 hours

echo "=========================================="
echo "LSTM Yeast PPI EPA Benchmark"
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
echo -e "\nStarting LSTM benchmark for yeast_ppi..."
python run_benchmark.py --model lstm --dataset yeast_ppi --epochs 30 --batch-size 64 --output-dir results/lstm

echo "=========================================="
echo "End: $(date)"
echo "=========================================="

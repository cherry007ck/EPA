#!/bin/bash
#SBATCH --job-name=lstm_subcellular
#SBATCH --output=logs/lstm_subcellular_localization_%j_out.txt
#SBATCH --error=logs/lstm_subcellular_localization_%j_err.txt
#SBATCH --partition=uds-hub
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=48G
#SBATCH --time=24:00:00

# LSTM Subcellular Localization Multi-class Classification Benchmark
# Dataset: 22,168 samples, 10-class localization prediction
# Model: LSTM
# Expected runtime: ~12-18 hours

echo "=========================================="
echo "LSTM Subcellular Localization EPA Benchmark"
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
echo -e "\nStarting LSTM benchmark for subcellular_localization..."
python run_benchmark.py --model lstm --dataset subcellular_localization --epochs 30 --batch-size 64 --output-dir results/lstm

echo "=========================================="
echo "End: $(date)"
echo "=========================================="

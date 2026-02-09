#!/bin/bash
#SBATCH --job-name=resnet_secondary_struct
#SBATCH --output=logs/resnet_secondary_struct_%j_out.txt
#SBATCH --error=logs/resnet_secondary_struct_%j_err.txt
#SBATCH --partition=uds-hub
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=12:00:00

# ResNet Secondary Structure Prediction Benchmark
# Dataset: 8,678 samples, 3-class classification
# Model: ResNet
# Expected runtime: ~4-6 hours

echo "=========================================="
echo "ResNet Secondary Structure EPA Benchmark"
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURM_NODELIST"
echo "Start: $(date)"
echo "=========================================="

# Setup
cd /home/hor20kud/aug/EPA
source epa_venv/bin/activate

# GPU info
nvidia-smi

# Run benchmark with ResNet config
echo -e "\nStarting ResNet benchmark for secondary_structure..."
python run_benchmark.py --model resnet --dataset secondary_structure --epochs 30 --batch-size 64

echo "=========================================="
echo "End: $(date)"
echo "=========================================="

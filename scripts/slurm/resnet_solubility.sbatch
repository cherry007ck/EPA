#!/bin/bash
#SBATCH --job-name=resnet_solubility
#SBATCH --output=logs/resnet_solubility_%j_out.txt
#SBATCH --error=logs/resnet_solubility_%j_err.txt
#SBATCH --partition=uds-hub
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=48G
#SBATCH --time=24:00:00

# ResNet Solubility Binary Classification Benchmark
# Dataset: 62,478 samples, solubility prediction
# Model: ResNet
# Expected runtime: ~12-18 hours

echo "=========================================="
echo "ResNet Solubility EPA Benchmark"
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
echo -e "\nStarting ResNet benchmark for solubility..."
python run_benchmark.py --model resnet --dataset solubility --epochs 30 --batch-size 32

echo "=========================================="
echo "End: $(date)"
echo "=========================================="

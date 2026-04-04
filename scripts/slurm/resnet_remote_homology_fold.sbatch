#!/bin/bash
#SBATCH --job-name=resnet_remote_fold
#SBATCH --output=logs/resnet_remote_homology_fold_%j_out.txt
#SBATCH --error=logs/resnet_remote_homology_fold_%j_err.txt
#SBATCH --partition=uds-hub
#SBATCH --nodelist=gpu101,gpu102,gpu103,gpu104,gpu105,gpu113,gpu114,gpu117,gpu118
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=48G
#SBATCH --time=24:00:00

# ResNet Remote Homology Fold Classification Benchmark
# Dataset: ~12K samples, 1195-class fold classification
# Model: ResNet (batch_size=32, larger output layer for 1195 classes)
# Expected runtime: ~12-20 hours (1195 classes is expensive)

echo "=========================================="
echo "ResNet Remote Homology Fold EPA Benchmark"
echo "Job ID: $SLURM_JOB_ID"
echo "Node:   $SLURM_NODELIST"
echo "Start:  $(date)"
echo "=========================================="

# Setup
cd /home/hor20kud/aug/EPA
source epa_venv/bin/activate

# GPU info
nvidia-smi

# Run benchmark with ResNet
echo -e "\nStarting ResNet benchmark for remote_homology_fold..."
python run_benchmark.py \
    --model resnet \
    --dataset remote_homology_fold \
    --epochs 30 \
    --batch-size 32 \
    --output-dir results/resnet

echo "=========================================="
echo "End: $(date)"
echo "=========================================="

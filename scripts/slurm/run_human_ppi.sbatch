#!/bin/bash
#SBATCH --job-name=human_ppi
#SBATCH --output=logs/human_ppi_%j_out.txt
#SBATCH --error=logs/human_ppi_%j_err.txt
#SBATCH --partition=uds-hub
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=48G
#SBATCH --time=24:00:00

# Human PPI Binary Classification Benchmark
# Dataset: 35,670 samples, dual-sequence PPI classification
# Expected runtime: ~12-18 hours

echo "=========================================="
echo "Human PPI EPA Benchmark"
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
echo -e "\nStarting benchmark for human_ppi..."
python universal_benchmark.py --dataset human_ppi --epochs 30 --batch_size 32

echo "=========================================="
echo "End: $(date)"
echo "=========================================="

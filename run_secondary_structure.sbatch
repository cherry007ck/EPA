#!/bin/bash
#SBATCH --job-name=secondary_struct
#SBATCH --output=logs/secondary_structure_%j_out.txt
#SBATCH --error=logs/secondary_structure_%j_err.txt
#SBATCH --partition=uds-hub
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=12:00:00

# Secondary Structure Residue Classification Benchmark
# Dataset: 8,679 samples, 3-class per-residue classification
# Expected runtime: ~6-8 hours

echo "=========================================="
echo "Secondary Structure EPA Benchmark"
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
echo -e "\nStarting benchmark for secondary_structure..."
python universal_benchmark.py --dataset secondary_structure --epochs 30 --batch_size 64

echo "=========================================="
echo "End: $(date)"
echo "=========================================="

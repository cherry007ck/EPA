#!/bin/bash
#SBATCH --job-name=resnet_subcell_loc
#SBATCH --output=logs/resnet_subcell_loc_%j_out.txt
#SBATCH --error=logs/resnet_subcell_loc_%j_err.txt
#SBATCH --partition=uds-hub
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=48G
#SBATCH --time=24:00:00

# ResNet Subcellular Localization Benchmark
# Dataset: 22,168 samples, 10-class classification
# Model: ResNet
# Expected runtime: ~12-18 hours

echo "=========================================="
echo "ResNet Subcellular Localization EPA Benchmark"
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
echo -e "\nStarting ResNet benchmark for subcellular_localization..."
python run_benchmark.py --model resnet --dataset subcellular_localization --epochs 30 --batch-size 32

echo "=========================================="
echo "End: $(date)"
echo "=========================================="

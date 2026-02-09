#!/bin/bash
#SBATCH -J epa-benchmark
#SBATCH -t 12:00:00
#SBATCH --mem=32G
#SBATCH --cpus-per-task=4
#SBATCH -N 1
#SBATCH --gpus=a4000:1
#SBATCH --partition=uds-hub
#SBATCH --output=/home/hor20kud/aug/EPA/logs/benchmark_%x_%j_out.txt
#SBATCH --error=/home/hor20kud/aug/EPA/logs/benchmark_%x_%j_err.txt

# Universal EPA Benchmark Script
# Usage: sbatch run_universal_benchmark.sbatch <dataset_name>
# Example: sbatch run_universal_benchmark.sbatch subcellular_localization

DATASET=${1:-subcellular_localization_2}  # Default to binary classification

echo "=========================================="
echo "EPA Universal Benchmark"
echo "=========================================="
echo "Dataset: $DATASET"
echo "Job ID: $SLURM_JOB_ID"
echo "Job started at: $(date)"
echo "Running on node: $(hostname)"
echo "=========================================="

# Activate virtual environment
source /home/hor20kud/aug/EPA/epa_venv/bin/activate
echo "Activated virtual environment: epa_venv"

# Navigate to EPA directory
cd /home/hor20kud/aug/EPA

# Print GPU info
echo "GPU Information:"
nvidia-smi
echo "=========================================="

# Print Python environment
echo "Python environment:"
echo "  Python binary: $(which python)"
echo "  Python version: $(python --version)"
python -c "import torch; print(f'  PyTorch: {torch.__version__}'); print(f'  CUDA available: {torch.cuda.is_available()}'); print(f'  CUDA version: {torch.version.cuda}'); print(f'  GPU count: {torch.cuda.device_count()}')"
echo "=========================================="

# Run benchmark
echo "Starting benchmark for dataset: $DATASET"
echo ""

python universal_benchmark.py \
    --dataset "$DATASET" \
    --epochs 30 \
    --batch_size 64

echo ""
echo "=========================================="
echo "Benchmark Complete!"
echo "Job finished at: $(date)"
echo "=========================================="

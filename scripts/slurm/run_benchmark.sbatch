#!/bin/bash
#SBATCH -J epa-benchmark
#SBATCH -t 12:00:00
#SBATCH --mem=32G
#SBATCH --cpus-per-task=4
#SBATCH -N 1
#SBATCH --gpus=a4000:1
#SBATCH --partition=uds-hub
#SBATCH --output=/home/hor20kud/aug/EPA/logs/benchmark_%j_out.txt
#SBATCH --error=/home/hor20kud/aug/EPA/logs/benchmark_%j_err.txt

# EPA Augmentation Benchmark - SLURM Batch Job
# Expected runtime: ~4-6 hours (GPU) or ~8-12 hours (CPU)
# Tests all 23 augmentations individually

echo "=========================================="
echo "EPA Augmentation Benchmark (FIXED)"
echo "=========================================="
echo "Job ID: $SLURM_JOB_ID"
echo "Job started at: $(date)"
echo "Running on node: $(hostname)"
echo "=========================================="

# Load environment modules
module load cuda/12.1

# Activate the dedicated EPA virtual environment
source /home/hor20kud/aug/EPA/epa_venv/bin/activate
echo "Activated virtual environment: epa_venv"

# Navigate to EPA directory
cd /home/hor20kud/aug/EPA

# Create logs directory if it doesn't exist
mkdir -p logs

# Print GPU info
echo "GPU Information:"
nvidia-smi
echo "=========================================="

# Clear GPU memory cache
echo "Clearing GPU cache..."
python -c "import torch; torch.cuda.empty_cache()" 2>/dev/null || true

# Set Python binary
PYTHON_BIN=python

# Print Python environment info
echo "Python environment:"
echo "  Conda env: $CONDA_DEFAULT_ENV"
echo "  Python binary: $(which python)"
echo "  Python version: $(python --version)"
echo ""
echo "PyTorch version and CUDA availability:"
python -c "import torch; print(f'  PyTorch: {torch.__version__}'); print(f'  CUDA available: {torch.cuda.is_available()}'); print(f'  CUDA version: {torch.version.cuda if torch.cuda.is_available() else \"N/A\"}'); print(f'  GPU count: {torch.cuda.device_count()}')"
echo "=========================================="

# Run the benchmark with timestamped log
LOG_FILE="benchmark_log_$(date +%Y%m%d_%H%M%S).txt"
echo "Starting benchmark..."
echo "Detailed output will be saved to: $LOG_FILE"
echo ""

python benchmark_FIXED.py 2>&1 | tee "$LOG_FILE"

# Print completion message
echo ""
echo "=========================================="
echo "Benchmark Complete!"
echo "Job finished at: $(date)"
echo "=========================================="
echo "Results saved to: EPA/benchmark_results_final_*.json"
echo "Log saved to: $LOG_FILE"
echo "=========================================="

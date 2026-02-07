#!/bin/bash
#SBATCH -J epa-apa-run
#SBATCH -t 6:00:00
#SBATCH --mem=16G
#SBATCH --cpus-per-task=4
#SBATCH -N 1
#SBATCH --gpus=a4000:1
#SBATCH --partition=uds-hub
#SBATCH --output=/home/hor20kud/aug/EPA/logs/epa_apa_%j_out.txt
#SBATCH --error=/home/hor20kud/aug/EPA/logs/epa_apa_%j_err.txt

# EPA (APA) - Enhanced Protein Augmentation 
# Two-phase training with automated policy search

echo "=========================================="
echo "EPA (APA) - Enhanced Protein Augmentation"
echo "=========================================="
echo "Job ID: $SLURM_JOB_ID"
echo "Job started at: $(date)"
echo "Running on node: $(hostname)"
echo "=========================================="

# Activate the dedicated EPA virtual environment
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

# Print PyTorch info
python -c "import torch; print(f'  PyTorch: {torch.__version__}'); print(f'  CUDA available: {torch.cuda.is_available()}'); print(f'  CUDA version: {torch.version.cuda}'); print(f'  GPU count: {torch.cuda.device_count()}')"
echo "=========================================="

# Run EPA training
echo "Starting EPA training with policy search..."
echo ""

python epa/EnhancedProteinAugment.py \
    --config config/LSTM/binloc_LSTM.yaml \
    --seed 42

echo ""
echo "=========================================="
echo "EPA Training Complete!"
echo "Job finished at: $(date)"
echo "=========================================="

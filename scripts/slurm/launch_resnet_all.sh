#!/bin/bash
#
# Launch all ResNet EPA benchmark jobs
# This script submits all 7 ResNet tasks to SLURM
#

echo "=========================================="
echo "Launching ResNet EPA Benchmarks"
echo "Date: $(date)"
echo "=========================================="

cd /home/hor20kud/aug/EPA

# Create logs directory if it doesn't exist
mkdir -p logs

# Array of all ResNet tasks
tasks=(
    "beta_lactamase"
    "secondary_structure"
    "human_ppi"
    "solubility"
    "subcellular_localization"
    "subcellular_localization_2"
    "yeast_ppi"
)

echo -e "\nSubmitting 7 ResNet benchmark jobs...\n"

# Submit all jobs
for task in "${tasks[@]}"; do
    echo "Submitting: resnet_${task}"
    job_id=$(sbatch scripts/slurm/resnet_${task}.sbatch 2>&1 | grep -oP 'Submitted batch job \K\d+')
    if [ $? -eq 0 ]; then
        echo "  Job ID: $job_id"
    else
        echo "  Failed to submit"
    fi
done

echo -e "\n=========================================="
echo "All jobs submitted!"
echo "=========================================="
echo ""
echo "Check job status with:"
echo "  squeue -u \$USER"
echo ""
echo "Monitor logs in real-time:"
echo "  tail -f logs/resnet_*_out.txt"
echo ""
echo "Check all jobs:"
echo "  sacct -u \$USER --format=JobID,JobName%30,State,Start,Elapsed -S $(date +%Y-%m-%d)"
echo ""

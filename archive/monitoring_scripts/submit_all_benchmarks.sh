#!/bin/bash
# Submit benchmark jobs for all available datasets

echo "=========================================="
echo "EPA Multi-Dataset Benchmark Submission"
echo "=========================================="

DATASETS=(
    "subcellular_localization_2"    # 2 classes - fastest
    "subcellular_localization"      # 10 classes
    "yeast_ppi"                     # 2 classes, PPI task
    # "remote_homology_fold"        # 1195 classes - very large, uncomment if needed
    # "remote_homology_family"      # 4254 classes - very large
    # "remote_homology_superfamily" # 2056 classes - large
)

cd /home/hor20kud/aug/EPA

for dataset in "${DATASETS[@]}"; do
    echo ""
    echo "Submitting job for: $dataset"
    job_id=$(sbatch --job-name="epa-$dataset" run_universal_benchmark.sbatch "$dataset" | awk '{print $4}')
    echo "  Job ID: $job_id"
    sleep 1
done

echo ""
echo "=========================================="
echo "All jobs submitted!"
echo "=========================================="
echo ""
echo "Check status with: squeue -u \$USER"
echo "Monitor logs: ls -lht logs/"

#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# launch_rf_all.sh
# Master launch script for all Random Forest EPA benchmarks
#
# USAGE:
#   Option A — Job Array (recommended, all 6 datasets in parallel):
#       bash scripts/slurm/launch_rf_all.sh
#
#   Option B — Individual jobs (more control per-dataset):
#       bash scripts/slurm/launch_rf_all.sh --individual
#
# NOTE: Solubility already has results (results/random_forest_solubility_*).
#       This script only submits the 6 PENDING datasets.
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

cd /home/hor20kud/aug/EPA
mkdir -p logs results/random_forest

echo "=========================================="
echo " EPA Random Forest — Launch All Benchmarks"
echo "=========================================="
echo " Start: $(date)"
echo " Mode: ${1:---array}"
echo "=========================================="

# ── Pending datasets (solubility already done) ───────────────────────────────
DATASETS=(
    "beta_lactamase"
    "subcellular_localization"
    "subcellular_localization_2"
    "yeast_ppi"
    "human_ppi"
    "remote_homology_fold"
)

declare -a JOB_IDS
declare -a JOB_NAMES

# ── Option B: submit individually ────────────────────────────────────────────
if [[ "${1:-}" == "--individual" ]]; then
    echo -e "\nSubmitting 6 individual RF jobs...\n"

    SBATCH_MAP=(
        "beta_lactamase:scripts/slurm/rf_beta_lactamase.sbatch"
        "subcellular_localization:scripts/slurm/rf_subcellular_localization.sbatch"
        "subcellular_localization_2:scripts/slurm/rf_subcellular_localization_2.sbatch"
        "yeast_ppi:scripts/slurm/rf_yeast_ppi.sbatch"
        "human_ppi:scripts/slurm/rf_human_ppi.sbatch"
        "remote_homology_fold:scripts/slurm/rf_remote_homology_fold.sbatch"
    )

    for entry in "${SBATCH_MAP[@]}"; do
        DS="${entry%%:*}"
        SCRIPT="${entry#*:}"
        JOB_ID=$(sbatch "$SCRIPT" | awk '{print $4}')
        JOB_IDS+=("$JOB_ID")
        JOB_NAMES+=("$DS")
        echo "  ✓  ${DS}  →  Job ID ${JOB_ID}"
    done

# ── Option A: job array (default) ────────────────────────────────────────────
else
    echo -e "\nSubmitting RF job array (6 tasks, one per dataset)...\n"
    ARRAY_OUTPUT=$(sbatch scripts/slurm/rf_all_array.sbatch)
    ARRAY_JOB_ID=$(echo "$ARRAY_OUTPUT" | awk '{print $4}')
    echo "  ✓  Array job submitted  →  Job ID ${ARRAY_JOB_ID}"
    echo "     Tasks: ${ARRAY_JOB_ID}_0 … ${ARRAY_JOB_ID}_5"
    for i in "${!DATASETS[@]}"; do
        JOB_IDS+=("${ARRAY_JOB_ID}_${i}")
        JOB_NAMES+=("${DATASETS[$i]}")
    done
fi

# ── Summary ───────────────────────────────────────────────────────────────────
echo -e "\n=========================================="
echo " Job Summary"
echo "=========================================="
printf "  %-35s  %s\n" "DATASET" "JOB ID"
printf "  %-35s  %s\n" "-------" "------"
for i in "${!JOB_IDS[@]}"; do
    printf "  %-35s  %s\n" "${JOB_NAMES[$i]}" "${JOB_IDS[$i]}"
done

echo -e "\n=========================================="
echo " Monitoring Commands"
echo "=========================================="
echo "  # Live queue status:"
echo "    squeue -u \$USER --format='%.18i %.9P %.30j %.8T %.10M %.9l %.6D %R'"
echo ""
echo "  # Watch logs (array):"
echo "    tail -f logs/rf_array_*_out.txt"
echo ""
echo "  # Watch logs (individual):"
echo "    tail -f logs/rf_*_out.txt"
echo ""
echo "  # Cancel all RF jobs:"
if [[ "${1:-}" == "--individual" ]]; then
    echo "    scancel ${JOB_IDS[*]}"
else
    echo "    scancel \$ARRAY_JOB_ID"
fi
echo ""
echo "  # Check results:"
echo "    ls -lh results/random_forest/"
echo ""
echo "  # Quick result summary (after completion):"
echo "    python - <<'EOF'"
echo "    import glob, json"
echo "    for f in sorted(glob.glob('results/random_forest/random_forest_*.json')):"
echo "        d = json.load(open(f))"
echo "        rs = d.get('results', [])"
echo "        if rs:"
echo "            metric = rs[0].get('metric', list(rs[0].keys())[-1])"
echo "            best = max(rs, key=lambda x: x.get(metric, 0))"
echo "            print(f\"{d['dataset_name']:35s} best={best.get(metric,0):.4f}  aug={best.get('augmentation','?')}\")"
echo "    EOF"
echo "=========================================="
echo ""
echo " Results will be saved to: results/random_forest/"
echo " Log files at:             logs/rf_*"
echo "=========================================="

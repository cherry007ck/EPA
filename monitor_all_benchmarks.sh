#!/bin/bash
# Monitor all EPA benchmark jobs

echo "=========================================="
echo "EPA Benchmark Jobs Status"
echo "$(date)"
echo "=========================================="

# Check SLURM queue
echo -e "\n📊 Job Queue:"
squeue -u $USER --format="%.10i %.20j %.10P %.8T %.10M %.12l %.18R" | head -20

echo -e "\n=========================================="
echo "📁 Recent Results Files:"
echo "=========================================="
ls -lht benchmark_results_*.json 2>/dev/null | head -10 || echo "No results yet"

echo -e "\n=========================================="
echo "📈 Job Progress Summary:"
echo "=========================================="

# Function to check progress
check_progress() {
    local dataset=$1
    local job_pattern=$2
    
    # Find most recent log file
    log_file=$(ls -t logs/${job_pattern}*_out.txt 2>/dev/null | head -1)
    
    if [ -f "$log_file" ]; then
        echo -e "\n🔬 ${dataset}:"
        
        # Current augmentation
        current_aug=$(tail -100 "$log_file" | grep "Training:" | tail -1 | sed 's/.*Training: \([^(]*\).*/\1/' | xargs)
        if [ ! -z "$current_aug" ]; then
            echo "  Current: $current_aug"
        fi
        
        # Recent epochs
        echo "  Recent progress:"
        tail -100 "$log_file" | grep "Epoch" | tail -3 | sed 's/^/    /'
        
        # Best validation score
        if echo "$dataset" | grep -q "beta_lactamase"; then
            # Regression task
            best=$(tail -100 "$log_file" | grep "✅" | tail -1)
            if [ ! -z "$best" ]; then
                echo "  Latest completed: $best"
            fi
        else
            # Classification tasks
            best=$(tail -100 "$log_file" | grep "✅" | tail -1)
            if [ ! -z "$best" ]; then
                echo "  Latest completed: $best"
            fi
        fi
    else
        echo -e "\n🔬 ${dataset}: No log file yet"
    fi
}

# Check each benchmark
check_progress "remote_homology_fold" "epa-benchmark"
check_progress "beta_lactamase" "beta_lactamase"
check_progress "secondary_structure" "secondary_structure"
check_progress "human_ppi" "human_ppi"
check_progress "solubility" "solubility"

echo -e "\n=========================================="
echo "💾 Disk Usage:"
df -h /home/hor20kud/aug/EPA | tail -1 | awk '{print "  " $3 " used, " $4 " available"}'
echo "=========================================="

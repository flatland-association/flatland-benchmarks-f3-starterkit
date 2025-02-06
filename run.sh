#!/bin/bash
set -x
echo "/ start submission_template/run.sh"
set -e
source /home/conda/.bashrc
source activate base
conda activate flatland-rl
python -m pip list
python run_solution.py
echo "\\ end submission_template/run.sh"

#/bin/bash
echo "genetic 4" >> logs.txt
sudo ./run_genetic_for_diff_params.sh 4 16 1 60
echo "run_project 4" >> logs.txt
sudo ./run_project.sh 4 16 1 60
echo "run_project 8" >> logs.txt
sudo ./run_project.sh 8 16 1 60
echo "genetic 8" >> logs.txt
sudo ./run_genetic_for_diff_params.sh 8 16 1 60

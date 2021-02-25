python3 tsvForBert.py

rm -f apps/tmp/sim_model/*
rm -r apps/tmp/sim_model/eval

#!/usr/bin/env bash
python3 run_training.py \
  --data_dir=train_data/bert/zh \
  --output_dir=tmp/sim_model 
  
rm -f train_data/raw/zh/*
rm -f train_data/raw/en/*
rm -f train_data/raw/*
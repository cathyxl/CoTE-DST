HOME_DIR=""

DATA_ROOT="$HOME_DIR/datasets"
DATA_OUT_ROOT="$DATA_ROOT/dst"
OUTPUT_DIR="$HOME_DIR/code_outputs/DST/low-resource"

DATA_DIR=${DATA_OUT_ROOT}/$DATA_VERSION
MODEL_NAME=t5-base
# max_train_samples=278202
max_train_samples=13037
# max_train_samples=139101

seeds=(660 0 746 953 62)

gpus=0,1
for seed in ${seeds[@]};
do
EXP_NAME=${OUTPUT_DIR}/${MODEL_NAME}-woes-bs64-e10-$DATA_VERSION-s$seed-$max_train_samples


resume_from_checkpoint=$EXP_NAME/checkpoint-65205
echo $EXP_NAME
CUDA_VISIBLE_DEVICES=$gpus python3 cot_src/train.py \
    --model_name_or_path $MODEL_NAME \
    --do_train \
    --do_predict \
    --train_file "$DATA_DIR/train.json" \
    --validation_file "$DATA_DIR/test.json" \
    --test_file "$DATA_DIR/test.json" \
    --source_prefix "" \
    --output_dir $EXP_NAME \
    --max_source_length=1024 \
    --max_target_length=512 \
    --seed=$seed \
    --max_train_samples=$max_train_samples \
    --per_device_train_batch_size=16 \
    --per_device_eval_batch_size=128 \
    --gradient_accumulation_steps=2 \
    --num_train_epochs=15 \
    --predict_with_generate \
    --text_column="dialogue" \
    --summary_column="result" \
    --save_strategy epoch \
    --resume_from_checkpoint $resume_from_checkpoint
done

HOME_DIR=""
DATA_ROOT=$HOME_DIR/datasets
DATA_OUT_ROOT=$DATA_ROOT/dst
OUTPUT_DIR=$HOME_DIR/code_outputs/DST

DATA_VERSION=multiwoz2.2-bin-cot-rmnone-gpt3
DATA_DIR=${DATA_OUT_ROOT}/$DATA_VERSION

MODEL_NAME=t5-base

EXP_NAME=""

echo $EXP_NAME
# EXP_NAME=${OUTPUT_DIR}/${MODEL_NAME}-$DATA_VERSION/checkpoint-2920
gpus=0,1

CUDA_VISIBLE_DEVICES=$gpus python3 cot_src/train.py \
    --model_name_or_path $EXP_NAME \
    --do_predict \
    --train_file "$DATA_DIR/train.json" \
    --validation_file "$DATA_DIR/dev.json" \
    --test_file "$DATA_DIR/test.json" \
    --source_prefix "" \
    --output_dir $EXP_NAME \
    --max_source_length=1024 \
    --max_target_length=512 \
    --per_device_train_batch_size=16 \
    --per_device_eval_batch_size=128 \
    --predict_with_generate \
    --text_column="dialogue" \
    --summary_column="result"

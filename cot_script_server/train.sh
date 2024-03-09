
DATA_ROOT=""
DATA_OUT_ROOT="$DATA_ROOT/dst"
OUTPUT_DIR=""

DATA_VERSION="multiwoz2.2-bin-cot-rmnone-gpt3"
# DATA_VERSION="woz2.0-simple-bin-cotqa-"

# DATA_VERSION="woz2.0-bin-cotqa"

DATA_DIR=${DATA_OUT_ROOT}/$DATA_VERSION
MODEL_NAME=t5-base
# seed=104
# max_train_samples=3550

# EXP_NAME=${OUTPUT_DIR}/${MODEL_NAME}-$DATA_VERSION-s$seed-$max_train_samples
EXP_NAME=${OUTPUT_DIR}/${MODEL_NAME}-bs64-e10-$DATA_VERSION
# EXP_NAME=${OUTPUT_DIR}/${MODEL_NAME}-bs64-e50-pt10-rg-$DATA_VERSION
echo $EXP_NAME
# TIME=`date +%Y%m%d%H%M%S`
gpus=2,3,4,5
CUDA_VISIBLE_DEVICES=$gpus python3 cot_src/train.py \
    --model_name_or_path $MODEL_NAME \
    --do_train \
    --train_file "$DATA_DIR/train.json" \
    --validation_file "$DATA_DIR/dev.json" \
    --test_file "$DATA_DIR/test.json" \
    --source_prefix "" \
    --output_dir $EXP_NAME \
    --max_source_length=1024 \
    --max_target_length=512 \
    --per_device_train_batch_size=16 \
    --per_device_eval_batch_size=128 \
    --gradient_accumulation_steps=1 \
    --num_train_epochs=10 \
    --predict_with_generate \
    --text_column="dialogue" \
    --summary_column="result" \
    --save_strategy epoch

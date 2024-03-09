
DATA_ROOT="/datasets"

DATA_OUT_ROOT="$DATA_ROOT/dst"

# DATASET="multiwoz2.2"
DATASET="m2m-R-M-full"
# DATASET="woz2.0-simple"

CUSTOM_FILE="cot_preprocess/m2m_sdp.py"



if [[ ${CUSTOM_FILE} ]]; then
    rm cot_src/utils.py
    cp ${CUSTOM_FILE} cot_src/utils.py
fi
echo "finish copy"
# if [[ ! ${DATASET} ]]; then
#     DATASET="multiwoz2.2"
# fi

# mkdir -p ${DATA_DIR}/data/
if [[ ${DATASET} == "multiwoz2.2" ]]; then
    echo "Loading Multiwoz Data..."
    DATA_DIR=$DATA_ROOT/MultiWOZ_2.2
elif [[ ${DATASET} == "m2m-R" ]]; then
    echo "Loading m2m-R Data..." 
    DATA_DIR=${DATA_ROOT}/m2m/sim-R
elif [[ ${DATASET} == "m2m-R-full" ]]; then
    echo "Loading m2m-R-full Data..." 
    DATA_DIR=${DATA_ROOT}/m2m/sim-R-full
elif [[ ${DATASET} == "m2m-M" ]]; then
    echo "Loading m2m-M Data..." 
    DATA_DIR=${DATA_ROOT}/m2m/sim-M
elif [[ ${DATASET} == "m2m-R-M" ]]; then
    echo "Loading m2m-R-M Data..." 
    DATA_DIR=${DATA_ROOT}/m2m/sim-R-M
elif [[ ${DATASET} == "m2m-R-M-full" ]]; then
    echo "Loading m2m-R-M-full Data..." 
    DATA_DIR=${DATA_ROOT}/m2m/sim-R-M-full
elif [[ ${DATASET} == "dstc2" ]]; then
    echo "Loading dstc2 Data..." 
    DATA_DIR=${DATA_ROOT}/dstc8-schema-guided-dialogue
elif [[ ${DATASET} == "woz2.0" ]]; then
    echo "Loading woz2.0 Data..." 
    DATA_DIR=${DATA_ROOT}/woz2.0
elif [[ ${DATASET} == "woz2.0-simple" ]]; then
    echo "Loading woz2.0 Data..." 
    DATA_DIR=${DATA_ROOT}/woz2.0-simple
else
    echo "DATASET should be chosen from ['multiwoz2.2', 'multiwoz2.1', 'm2m-R-M', 'm2m-R', 'm2m-M', 'woz2.0', 'dstc2', 'sgd']"
    exit -3
fi


echo "Doing Preprocessing..."


# VERSION="-cot-gpt3"
# VERSION="-cot"


# VERSION="-cotqa-wexplain"

DATA_BIN_DIR=${DATA_OUT_ROOT}/$DATASET-bin$VERSION

mkdir -p ${DATA_BIN_DIR}/
python3 cot_src/preprocess.py ${DATA_DIR}/ ${DATA_BIN_DIR}/ ${DATASET}

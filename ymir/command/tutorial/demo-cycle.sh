#!/bin/bash
set -e # stop when any step fails.

# this script implements the expose_rubbish model training process by fengzhanpeng

# work dir structure
# CUR_DIR
# |- ymir-assets (YMIR_ASSET_LOCATION)
# |- ymir-models (YMIR_MODEL_LOCATION)
# |- mir-root (MIR_ROOT)

# usage:
#   0. decide your working directory, and copy this script to that directory
#   1. set global variables
#   2. ./demo-fzp.sh init: check and init enviroment
#   3. ./demo-fzp.sh import: import datasets
#   4. ./demo-fzp.sh training <num>: do training
#   5. ./demo-fzp.sh exclude <num>: exclude train and val set from mining dataset
#   6. ./demo-fzp.sh mining <num> <model-hash>: do mining, and merge top k (as training assets) to train and val set
#   7a1. ./demo-fzp.sh outlabel <num>: export top k for label
#   7a2. ./demo-fzp.sh inlabel <num> <label-dir>: import top k label to train
#   7b. ./demo-fzp.sh join <num>: merge top k to train
#   8. num++, and go step 4

# the whole pipeline just like this:
# [train and val]:       init --> import --> train                              +--> train
#                                                |                              |        |
# [big set for mining]:                          +--> exclude --> mining --> join        +--> exclude --> mining ...
# join can be replaced by outlabel and inlabel


# global variables
MIR_EXE="mir"
CUR_DIR="$PWD"  # your working directory
MIR_ROOT="$CUR_DIR/mir-demo-repo"

YMIR_MODEL_LOCATION="$CUR_DIR/ymir-models"
YMIR_ASSET_LOCATION="$CUR_DIR/ymir-assets"
RAW_DATA_ROOT="$CUR_DIR/data"  #! you can change

# in this pipeline, the whole data is devided into 3 part: TRAINING_SET, the VAL_SET and the MINING_SET
# TRAINING_SET and VAL_SET are used to train the first version of model
# and MINING_SET used to mining datas with command mir mining
#   and the mining result will be merged into the previous training set
RAW_TRAINING_SET_IMG_ROOT="$RAW_DATA_ROOT/train/img"  #! you can change
RAW_TRAINING_SET_ANNO_ROOT="$RAW_DATA_ROOT/train/anno"  #! you can change
RAW_TRAINING_SET_INDEX_PATH="$RAW_DATA_ROOT/train-short.txt"  #! you can change

RAW_VAL_SET_IMG_ROOT="$RAW_DATA_ROOT/val/img"  #! you can change
RAW_VAL_SET_ANNO_ROOT="$RAW_DATA_ROOT/val/anno"  #! you can change
RAW_VAL_SET_INDEX_PATH="$RAW_DATA_ROOT/val.txt"  #! you can change

RAW_MINING_SET_IMG_ROOT="$RAW_DATA_ROOT/train/img"  #! you can change
RAW_MINING_SET_ANNO_ROOT="$RAW_DATA_ROOT/train/anno"  #! you can change
RAW_MINING_SET_INDEX_PATH="$RAW_DATA_ROOT/mining.txt"  #! you can change, FOR TEST

CLASS_TYPES="expose_rubbish"
MINING_TOPK=50  #! FOR TEST

TRAINING_SET_PREFIX="dataset-training"  #! you can change
VAL_SET_PREFIX="dataset-val"  #! you can change
MINING_SET_PREFIX="dataset-mining"  #! you can change

TMP_TRAINING_ROOT="$CUR_DIR/tmp/training"
TMP_MINING_ROOT="$CUR_DIR/tmp/mining"
TMP_OUTLABEL_ASSET_ROOT="$CUR_DIR/tmp/outlabel/assets"
TMP_INLABEL_ANNOTATION_ROOT="$CUR_DIR/tmp/inlabel/annotations"
MEDIA_CACHE_PATH="$CUR_DIR/cache"

_MERGED_TRAINING_SET_PREFIX="cycle-node-tr-and-va"
_TRAINED_TRAINING_SET_PREFIX="cycle-node-trained"
_EXCLUDED_SET_PREFIX="cycle-node-excluded"
_MINED_SET_PREFIX="cycle-node-mined"
_INLABELED_SET_PREFIX="cycle-node-inlabeled"

# colors
C_OFF='\033[0m'
C_RED='\033[0;31m'
C_GREEN='\033[0;32m'
C_YELLOW='\033[0;33m'
C_RED_BOLD='\033[1;31m'
C_GREEN_BOLD='\033[1;32m'
C_YELLOW_BOLD='\033[1;33m'

# sub commands
init() {
    # YMIR_MODEL_LOCATION and YMIR_ASSET_LOCATION should exists
    # init MIR_ROOT
    # RAW_DATA_ROOT should exists
    if ! [[ -d $YMIR_MODEL_LOCATION ]]; then
        mkdir $YMIR_MODEL_LOCATION
    fi
    if ! [[ -d $YMIR_ASSET_LOCATION ]]; then
        mkdir -p $YMIR_ASSET_LOCATION
    fi

    # check raw dataset's assets and annotation dirs, make sure that they are exist
    _RAW_DATASET_ROOTS_=($RAW_TRAINING_SET_IMG_ROOT $RAW_TRAINING_SET_ANNO_ROOT \
                         $RAW_VAL_SET_IMG_ROOT $RAW_VAL_SET_ANNO_ROOT \
                         $RAW_MINING_SET_IMG_ROOT $RAW_MINING_SET_ANNO_ROOT)
    for _DATASET_ROOT_ in "${_RAW_DATASET_ROOTS_[@]}"; do
        if ! [[ -d $_DATASET_ROOT_ ]]; then
            echo "$_DATASET_ROOT_ is not a dir, abort" >&2
            exit 1
        fi
    done
    # check raw dataset's index files
    _RAW_DATASET_INDEX_PATHS_=($RAW_TRAINING_SET_INDEX_PATH $RAW_VAL_SET_INDEX_PATH $RAW_MINING_SET_INDEX_PATH)
    for _INDEX_PATH_ in "${_RAW_DATASET_INDEX_PATHS_[@]}"; do
        if ! [[ -f $_INDEX_PATH_ ]]; then
            echo "$_INDEX_PATH_ is not a file, abort" >&2
            exit 1
        fi
    done
    # check dataset prefix, they are used in task ids, branch names and dataset names
    if [[ -z $TRAINING_SET_PREFIX || -z $VAL_SET_PREFIX || -z $MINING_SET_PREFIX ]]; then
        echo "invalid train / val / mining dataset prefix, abort" >&2
        exit 1
    fi

    # check MIR_ROOT
    if [[ -d $MIR_ROOT ]]; then
        echo "$MIR_ROOT already exists, you can:"
        echo "    rm it and init again if you just want a new mir repo"
        echo "    or run deinit to REMOVE ALL THINGS and start over again"
    else
        mkdir -p $MIR_ROOT; cd $MIR_ROOT; mir init
    fi

    # check tmp
    if ! [[ -d $CUR_DIR/tmp ]]; then
        mkdir -p $CUR_DIR/tmp
    fi

    # check cache
    if ! [[ -d $MEDIA_CACHE_PATH ]]; then
        mkdir -p $MEDIA_CACHE_PATH
    fi
}

post_init_success() {
    _echo_in_color $C_GREEN "$1 success"
    echo "next: run $0 import"
}

deinit() {
    if [[ -d $YMIR_ASSET_LOCATION ]]; then
        rm -rf $YMIR_ASSET_LOCATION
    fi
    if [[ -d $YMIR_MODEL_LOCATION ]]; then
        rm -rf $YMIR_MODEL_LOCATION
    fi
    if [[ -d $MIR_ROOT ]]; then
        rm -rf $MIR_ROOT
    fi
    if [[ -d $CUR_DIR/tmp ]]; then
        rm -rf $CUR_DIR/tmp
    fi
}

post_deinit_success() {
    _echo_in_color $C_GREEN "$1 success"
    echo "next: run $0 init"
}

import() {
    # import training dataset
    _echo_in_color $C_YELLOW "import from master to $TRAINING_SET_PREFIX"
    $MIR_EXE checkout master --root "$MIR_ROOT"
    $MIR_EXE import --root "$MIR_ROOT" \
                    --index-file "$RAW_TRAINING_SET_INDEX_PATH" \
                    --pred-dir "$RAW_TRAINING_SET_ANNO_ROOT" \
                    --gen-dir "$YMIR_ASSET_LOCATION" \
                    --dataset-name "$TRAINING_SET_PREFIX" \
                    --dst-rev "$TRAINING_SET_PREFIX@$TRAINING_SET_PREFIX"

    # import val dataset
    _echo_in_color $C_YELLOW "import from master to $VAL_SET_PREFIX"
    $MIR_EXE checkout master --root "$MIR_ROOT"
    $MIR_EXE import --root "$MIR_ROOT" \
                    --index-file "$RAW_VAL_SET_INDEX_PATH" \
                    --pred-dir "$RAW_VAL_SET_ANNO_ROOT" \
                    --gen-dir "$YMIR_ASSET_LOCATION" \
                    --dataset-name "$VAL_SET_PREFIX" \
                    --dst-rev "$VAL_SET_PREFIX@$VAL_SET_PREFIX"

    # import mining dataset
    _echo_in_color $C_YELLOW "import from master to $MINING_SET_PREFIX"
    $MIR_EXE checkout master --root "$MIR_ROOT"
    $MIR_EXE import --root "$MIR_ROOT" \
                    --index-file "$RAW_MINING_SET_INDEX_PATH" \
                    --pred-dir "$RAW_MINING_SET_ANNO_ROOT" \
                    --gen-dir "$YMIR_ASSET_LOCATION" \
                    --dataset-name "$MINING_SET_PREFIX" \
                    --dst-rev "$MINING_SET_PREFIX@$MINING_SET_PREFIX"

    # first merge: _MERGED_TRAINING_SET_PREFIX-0 = tr:TRAINING_SET_PREFIX + va: VAL_SET_PREFIX
    _echo_in_color $C_YELLOW "merge from tr:$TRAINING_SET_PREFIX + va:$VAL_SET_PREFIX to $_MERGED_TRAINING_SET_PREFIX-0"
    $MIR_EXE merge --root $MIR_ROOT \
                   --src-revs "tr:$TRAINING_SET_PREFIX@$TRAINING_SET_PREFIX;va:$VAL_SET_PREFIX@$VAL_SET_PREFIX" \
                   --dst-rev "$_MERGED_TRAINING_SET_PREFIX-0@$_MERGED_TRAINING_SET_PREFIX-0" \
                   -s host
}

post_import_success() {
    _echo_in_color $C_GREEN "$1 success"
    echo "next: run $0 training 0"
}

training() {
    # prepare and training
    if [[ $# -lt 2 ]]; then
        echo "training needs cycle num, abort" >&2
        exit 1
    fi
    if [[ $2 -ge 0 ]]; then
        # training
        _echo_in_color $C_YELLOW "training from $_MERGED_TRAINING_SET_PREFIX-$2 to $_TRAINED_TRAINING_SET_PREFIX-$2"
        $MIR_EXE train --root $MIR_ROOT \
                       -w "$TMP_TRAINING_ROOT/$_MERGED_TRAINING_SET_PREFIX-$2" \
                       --model-location "$YMIR_MODEL_LOCATION" \
                       --media-location "$YMIR_ASSET_LOCATION" \
                       --src-revs "$_MERGED_TRAINING_SET_PREFIX-$2@$_MERGED_TRAINING_SET_PREFIX-$2" \
                       --dst-rev "$_TRAINED_TRAINING_SET_PREFIX-$2@$_TRAINED_TRAINING_SET_PREFIX-$2" \
                       --task-config-file "$CUR_DIR/training-config.yaml" \
                       --executor industryessentials/executor-det-yolov4-train:release-0.1.1
    else
        echo "invalid cycle num: $2, abort" >&2
        exit 1
    fi
}

post_training_success() {
    _echo_in_color $C_GREEN "$1 success"
    echo "next: run $0 exclude $2"
}

exclude() {
    if [[ $# < 2 ]]; then
        echo "exclude needs cycle num, abort" >&2
        exit 1
    fi

    if [[ $2 -eq 0 ]]; then
        # first exclude merge:
        _echo_in_color $C_YELLOW \
                       "exclude from $MINING_SET_PREFIX - $_MERGED_TRAINING_SET_PREFIX-0 to $_EXCLUDED_SET_PREFIX-0"
        $MIR_EXE merge --root $MIR_ROOT \
                       --src-revs "$MINING_SET_PREFIX@$MINING_SET_PREFIX" \
                       --ex-src-revs "$_MERGED_TRAINING_SET_PREFIX-0@$_MERGED_TRAINING_SET_PREFIX-0" \
                       --dst-rev "$_EXCLUDED_SET_PREFIX-0@$_EXCLUDED_SET_PREFIX-0" \
                       -s host
    elif [[ $2 -gt 0 ]]; then
        _PREVIOUS_CYCLE_NUM=$(($2 - 1))
        _echo_in_color $C_YELLOW \
                       "exclude from $_EXCLUDED_SET_PREFIX-$_PREVIOUS_CYCLE_NUM - $_MERGED_TRAINING_SET_PREFIX-$2 to $_EXCLUDED_SET_PREFIX-$2"
        $MIR_EXE merge --root $MIR_ROOT \
                       --src-revs "$_EXCLUDED_SET_PREFIX-$_PREVIOUS_CYCLE_NUM@$_EXCLUDED_SET_PREFIX-$_PREVIOUS_CYCLE_NUM" \
                       --ex-src-revs "$_MERGED_TRAINING_SET_PREFIX-$2@$_MERGED_TRAINING_SET_PREFIX-$2" \
                       --dst-rev "$_EXCLUDED_SET_PREFIX-$2@$_EXCLUDED_SET_PREFIX-$2" \
                       -s host
    else
        echo "invalid cycle num: $2, abort" >&2
        exit 1
    fi
}

post_exclude_success() {
    _echo_in_color $C_GREEN "$1 success"
    echo "next: run $0 mining $2 <model-hash> (model-hash: hash of the model you just trained)"
}

mining() {
    if [[ $# -lt 3 ]]; then
        echo "exclude needs cycle num and model hash, abort" >&2
        exit 1
    fi

    if [[ $2 -ge 0 ]]; then
        _echo_in_color $C_YELLOW "mining from $_EXCLUDED_SET_PREFIX-$2 to $_MINED_SET_PREFIX-$2"
        $MIR_EXE mining --root $MIR_ROOT \
                        --src-revs "$_EXCLUDED_SET_PREFIX-$2@$_EXCLUDED_SET_PREFIX-$2" \
                        --dst-rev "$_MINED_SET_PREFIX-$2@$_MINED_SET_PREFIX-$2" \
                        -w "$TMP_MINING_ROOT/$_MINED_SET_PREFIX-$2" \
                        --topk $MINING_TOPK \
                        --model-location "$YMIR_MODEL_LOCATION" \
                        --media-location "$YMIR_ASSET_LOCATION" \
                        --model-hash $3 \
                        --cache $MEDIA_CACHE_PATH \
                        --task-config-file "$CUR_DIR/mining-config.yaml" \
                        --executor industryessentials/executor-det-yolov4-mining:release-0.1.2
    else
        echo "invalid cycle num: $2, abort" >&2
        exit 1
    fi
}

post_mining_success() {
    _echo_in_color $C_GREEN "$1 success"
    echo "next: run $0 join $2"
    echo "  or: run $0 outlabel $2"
}

join() {
    if [[ $# -lt 2 ]]; then
        echo "join needs cycle num, abort" >&2
        exit 1
    fi

    if [[ $2 -ge 0 ]]; then
        _NEXT_CYCLE_NUM=`expr $2 + 1`
        _echo_in_color $C_YELLOW \
                       "merge topk from $_MERGED_TRAINING_SET_PREFIX-$2 + tr:$_MINED_SET_PREFIX-$2 to $_MERGED_TRAINING_SET_PREFIX-$_NEXT_CYCLE_NUM"
        $MIR_EXE merge --root $MIR_ROOT \
                       --src-revs "$_MERGED_TRAINING_SET_PREFIX-$2@$_MERGED_TRAINING_SET_PREFIX-$2;tr:$_MINED_SET_PREFIX-$2@$_MINED_SET_PREFIX-$2" \
                       --dst-rev "$_MERGED_TRAINING_SET_PREFIX-$_NEXT_CYCLE_NUM@$_MERGED_TRAINING_SET_PREFIX-$_NEXT_CYCLE_NUM" \
                       -s host
    else
        echo "invalid cycle num: $2, abort" >&2
        exit 1
    fi
}

post_join_success() {
    _echo_in_color $C_GREEN "$1 success"
    echo "next: run $0 training `expr $2 + 1`"
}

outlabel() {
    if [[ $# -lt 2 ]]; then
        echo "outlabel needs cycle num, abort" >&2
        exit 1
    fi

    if [[ $2 -ge 0 ]]; then
        _echo_in_color $C_YELLOW "export from $_MINED_SET_PREFIX-$2 to path $TMP_OUTLABEL_ASSET_ROOT/$_MINED_SET_PREFIX-$2"
        $MIR_EXE export --root $MIR_ROOT \
                        --asset-dir "$TMP_OUTLABEL_ASSET_ROOT/$_MINED_SET_PREFIX-$2" \
                        --pred-dir "$TMP_OUTLABEL_ASSET_ROOT/$_MINED_SET_PREFIX-$2" \
                        --media-location "$YMIR_ASSET_LOCATION" \
                        --src-revs "$_MINED_SET_PREFIX-$2@$_MINED_SET_PREFIX-$2" \
                        --format "none"

        # generate index file
        find "$TMP_OUTLABEL_ASSET_ROOT/$_MINED_SET_PREFIX-$2" -type f > \
            "$TMP_OUTLABEL_ASSET_ROOT/$_MINED_SET_PREFIX-$2.index.tsv"

        # create dir for inlabel annotations
        if ! [[ -d $TMP_INLABEL_ANNOTATION_ROOT/$_MINED_SET_PREFIX-$2 ]]; then
            mkdir -p "$TMP_INLABEL_ANNOTATION_ROOT/$_MINED_SET_PREFIX-$2"
        fi
    else
        echo "invalid cycle num: $2, abort" >&2
        exit 1
    fi
}

post_outlabel_success() {
    _echo_in_color $C_GREEN "$1 success"
    echo "next:"
    echo "  1. get assets from $TMP_OUTLABEL_ASSET_ROOT/$_MINED_SET_PREFIX-$2, create task in external labeling system"
    echo "  2. when task done, export annotation result to voc format"
    echo "  3. copy annotations to $TMP_INLABEL_ANNOTATION_ROOT/$_MINED_SET_PREFIX-$2"
    echo "  4. run $0 inlabel $2 $TMP_INLABEL_ANNOTATION_ROOT/$_MINED_SET_PREFIX-$2"
}

inlabel() {
    if [[ $# -lt 3 ]]; then
        echo "inlabel needs cycle num and voc annotation path, abort" >&2
        exit 1
    fi

    if [[ $2 -ge 0 ]]; then
        _echo_in_color $C_YELLOW "import"
        $MIR_EXE import --root "$MIR_ROOT" \
                    --index-file "$TMP_OUTLABEL_ASSET_ROOT/$_MINED_SET_PREFIX-$2.index.tsv" \
                    --pred-dir "$3" \
                    --gen-dir "$YMIR_ASSET_LOCATION" \
                    --dataset-name "$MINING_SET_PREFIX" \
                    --src-revs "$_MINED_SET_PREFIX-$2" \
                    --dst-rev "$_INLABELED_SET_PREFIX-$2@$_INLABELED_SET_PREFIX-$2"

        _NEXT_CYCLE_NUM=`expr $2 + 1`
        _echo_in_color $C_YELLOW \
                       "merge topk from $_MERGED_TRAINING_SET_PREFIX-$2 + tr:$_INLABELED_SET_PREFIX-$2 to $_MERGED_TRAINING_SET_PREFIX-$_NEXT_CYCLE_NUM"
        $MIR_EXE merge --root $MIR_ROOT \
                       --src-revs "$_MERGED_TRAINING_SET_PREFIX-$2@$_MERGED_TRAINING_SET_PREFIX-$2;tr:$_INLABELED_SET_PREFIX-$2@$_INLABELED_SET_PREFIX-$2" \
                       --dst-rev "$_MERGED_TRAINING_SET_PREFIX-$_NEXT_CYCLE_NUM@$_MERGED_TRAINING_SET_PREFIX-$_NEXT_CYCLE_NUM" \
                       -s host
    else
        echo "invalid cycle num: $2, abort" >&2
        exit 1
    fi
}

post_inlabel_success() {
    _echo_in_color $C_GREEN "$1 success"
    echo "next: run $0 training `expr $2 + 1`"
}

show_help_info() {
    _echo_in_color $C_OFF "ymir-0.1.1" 2 3 4
}

# private: colors
_echo_in_color() {
    printf $1
    printf "${*:2}\n"
    printf $C_OFF
}

# main
main() {
    # source demo-fzp.sh <command> <args>
    # call sub command in $1 directly
    if [[ $# -eq 0 ]]; then
        show_help_info
    else
        $1 "$@"
        post_$1_success "$@"
    fi
}

main "$@"

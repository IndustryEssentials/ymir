#!/bin/bash
set -e # stop when any step fails.

# This script simulates ymir demo 0.1 using cmd.

CUR_DIR="$PWD"
WORK_DIR_ROOT_ABS="$CUR_DIR/ymir-demo-work"
# Requirement:
# 1. git/mir installed.
# 2. docker images for training (mx_train:0.1.1.210804) and mining (al:0.0.1.b)
# 3. set up following:
# 3.0. this script will create ymir-demo-work under current folder as working dir.
# 3.1. download pascal data and extract to raw-data under working dir.
#      pascal train/val set: http://host.robots.ox.ac.uk/pascal/VOC/
#      coco val set: https://cocodataset.org/
# 3.2. folder stucture should be like:
#      raw-data
#        - pascal
#          - VOCdevkit
#            - VOC2012
#              - Annotations
#              - JPEGImages
#        - coco
#          - val2017
#          - annotations
#          - converted_xml (convert coco json format to pascal format)
PASCAL_DATA_ROOT_ABS="$CUR_DIR/raw-data/pascal"
COCO_DATA_ROOT_ABS="$CUR_DIR/raw-data/coco"

# setup sub_folder location.
PASCAL_DATA_IMG_ABS="$PASCAL_DATA_ROOT_ABS/VOCdevkit/VOC2012/JPEGImages"
PASCAL_DATA_ANNO_ABS="$PASCAL_DATA_ROOT_ABS/VOCdevkit/VOC2012/Annotations"
COCO_DATA_IMG_ABS="$COCO_DATA_ROOT_ABS/val2017"
COCO_DATA_ANNO_ABS="$COCO_DATA_ROOT_ABS/converted_xml"
INTERMEDIATE_FOLDER_ABS="$WORK_DIR_ROOT_ABS/intermedia"
MODEL_FOLDER_ABS="$INTERMEDIATE_FOLDER_ABS/models"
ASSET_LOCATION_ABS="$INTERMEDIATE_FOLDER_ABS"

# setup index file path.
IDX_PASCAL_ABS="$INTERMEDIATE_FOLDER_ABS/index_pascal.txt"
IDX_COCO_ABS="$INTERMEDIATE_FOLDER_ABS/index_coco.txt"

# setup mir repo env
TMP_DEMO_REPO_ABS="$WORK_DIR_ROOT_ABS/mir-demo-repo"
MIR_EXE='mir -d' # MIR_EXE="mir -d" # for debug
DEMO_PASCAL_BRANCH='demo-pascal'
DEMO_PASCAL_BRANCH_FILTER='demo-pascal-filter'
DEMO_PASCAL_BRANCH_TRAIN='demo-pascal-train'
DEMO_PASCAL_BRANCH_MINING='demo-pascal-mining'
DEMO_COCO_BRANCH='demo-coco'
DEMO_INIT_BRANCH='demo-branch'
DEMO_MERGE_AND_TRAINING='demo-merge-train'

# fitler
MATCHED_KEYWORDS="person;cat;dog"
EXCLUDE_KEYWORDS="bicycle"

demo_main() {
# Step 1: check environment.
check_env

# Step 2: create empty mir repo.
prepare_repo

# Step 3: Generate sha index file and rename images using sha id.
# import_data

# Step 4: filter.
# process_filter

# Step 5: train.
TRAIN_IMAGE='mx_train:0.1.1.210804'
# process_train

# Step 6: mining.
MINING_IMAGE='al:0.0.1.b'
# process_mining

# Step : merge and train.
# process_merge_train
}


check_env () {
    # check mir, git, docker installeed.
    if ! [ -x "$(command -v mir)" ] || \
    ! [ -x "$(command -v git)" ] || ! [ -x "$(command -v docker)" ]; then
        echo 'mir/git/docker non exist';
        exit 1;
    fi

    if [ ! -d $PASCAL_DATA_IMG_ABS ] || [ ! -d $PASCAL_DATA_ANNO_ABS ] \
        || [ ! -d $COCO_DATA_IMG_ABS ] || [ ! -d $COCO_DATA_ANNO_ABS ]; then
        echo 'data dir check fail, the following dirs/file may not exist:';
        echo 'pascal images: '$PASCAL_DATA_IMG_ABS;
        echo 'pascal annotations: '$PASCAL_DATA_ANNO_ABS;
        echo 'coco images: '$COCO_DATA_IMG_ABS;
        echo 'coco annotations: '$COCO_DATA_ANNO_ABS;
        exit 1;
    fi

    if [ ! -d $WORK_DIR_ROOT_ABS ]; then
        printf '%s\n' 'working folder not exist, creating...';
        mkdir -p $WORK_DIR_ROOT_ABS;
    fi

    if ! [ -d $INTERMEDIATE_FOLDER_ABS ]; then
        printf '%s\n' "data intermediate dir not exist, building...";
        mkdir $INTERMEDIATE_FOLDER_ABS;
    fi

    printf 'Environment pass.\n'
}

prepare_repo () {
    if ! [ -d $TMP_DEMO_REPO_ABS ]; then
        printf '%s\n' "repo dir not exist, building...";
        mkdir $TMP_DEMO_REPO_ABS && cd $TMP_DEMO_REPO_ABS;
        $MIR_EXE init && $MIR_EXE checkout -b $DEMO_INIT_BRANCH
        touch README && git add . && git commit -m "init repo"
    else
        cd $TMP_DEMO_REPO_ABS;
    fi

    printf 'prepare_repo pass.\n'
}

import_data() {
    if [ `git rev-parse --quiet --verify refs/heads/$DEMO_PASCAL_BRANCH` ]; then
        printf '%s\n' "Branch name $DEMO_PASCAL_BRANCH already exists.";
    else
        printf '%s\n' "importing pascal as branch $DEMO_PASCAL_BRANCH";
        import_data_pascal
    fi

    if [ `git rev-parse --quiet --verify refs/heads/$DEMO_COCO_BRANCH` ]; then
        printf '%s\n' "Branch name $DEMO_COCO_BRANCH already exists.";
    else
        printf '%s\n' "importing coco as branch $DEMO_COCO_BRANCH";
        $MIR_EXE checkout $DEMO_INIT_BRANCH
        import_data_coco
    fi

    printf 'import_data pass.\n'
}

import_data_pascal() {
    # prepare pascal-branch
    $MIR_EXE checkout $DEMO_INIT_BRANCH
    if ! [ -f $IDX_PASCAL_ABS ]; then
        printf '%s\n' "creating pascal index file... $IDX_PASCAL_ABS"
        find $PASCAL_DATA_IMG_ABS -iname \*.jpg >> $IDX_PASCAL_ABS
    fi
    $MIR_EXE import --index-file $IDX_PASCAL_ABS --annotation-dir $PASCAL_DATA_ANNO_ABS --gen-dir $INTERMEDIATE_FOLDER_ABS --dataset-name $DEMO_PASCAL_BRANCH -t $DEMO_PASCAL_BRANCH
}

import_data_coco() {
    # prepare coco-branch
    $MIR_EXE checkout $DEMO_INIT_BRANCH
    if ! [ -f $IDX_COCO_ABS ]; then
        printf '%s\n' "creating coco index file... $IDX_COCO_ABS"
        find $COCO_DATA_IMG_ABS -iname \*.jpg >> $IDX_COCO_ABS
    fi
    $MIR_EXE import --index-file $IDX_COCO_ABS --annotation-dir $COCO_DATA_ANNO_ABS --gen-dir $INTERMEDIATE_FOLDER_ABS --dataset-name $DEMO_COCO_BRANCH -t $DEMO_COCO_BRANCH
}

process_filter() {
    if ! [ `git rev-parse --quiet --verify refs/heads/$DEMO_PASCAL_BRANCH_FILTER` ]; then
        printf '%s\n' "filtering pascal as branch $DEMO_PASCAL_BRANCH_FILTER";
        $MIR_EXE checkout $DEMO_PASCAL_BRANCH
        $MIR_EXE filter -p $MATCHED_KEYWORDS -e $EXCLUDE_KEYWORDS -t $DEMO_PASCAL_BRANCH_FILTER --base-task-id $DEMO_PASCAL_BRANCH
    else
        printf '%s\n' "Branch name $DEMO_PASCAL_BRANCH_FILTER already exists.";
        $MIR_EXE checkout $DEMO_PASCAL_BRANCH_FILTER
    fi
}


process_train() {
    if [ `git rev-parse --quiet --verify refs/heads/$DEMO_PASCAL_BRANCH_TRAIN` ]; then
        printf '%s\n' "Branch name $DEMO_PASCAL_BRANCH_TRAIN already exists.";
        $MIR_EXE checkout $DEMO_PASCAL_BRANCH_TRAIN
        return 0
    fi


    if ! [[ -n "$(docker images -q $TRAIN_IMAGE)" ]]; then
        echo "training docker image not exist";
        #exit 1;
    fi

    $MIR_EXE checkout $DEMO_PASCAL_BRANCH_FILTER


    if ! [ -d $MODEL_FOLDER_ABS ]; then
        printf '%s\n' "creating model folder $MODEL_FOLDER_ABS"
        mkdir $MODEL_FOLDER_ABS;
    fi
    TASK_ID='training_task_1'
    WORKING_DIR="/tmp/$TASK_ID"
    $MIR_EXE train -p $MATCHED_KEYWORDS -tp 0.7 -vp 0.2 --model-location $MODEL_FOLDER_ABS -t $TASK_ID --media-location $ASSET_LOCATION_ABS -w $WORKING_DIR
    printf 'done training\n';
}

process_mining() {
    if [ `git rev-parse --quiet --verify refs/heads/$DEMO_PASCAL_BRANCH_MINING` ]; then
        printf '%s\n' "Branch name $DEMO_PASCAL_BRANCH_MINING already exists.";
        $MIR_EXE checkout $DEMO_PASCAL_BRANCH_MINING
        return 0
    fi

    $MIR_EXE checkout $DEMO_COCO_BRANCH

    if ! [[ -n "$(docker images -q $MINING_IMAGE)" ]]; then
        echo "mining docker image not exist";
        exit 1;
    fi
    MODEL_HASH='4ea7496e80ead9f683be8e59f224bdd04b22b745' # Resnet18
    #MODEL_HASH='c1a3ae7593b4e37bb01c3376e0d9464ade7f7305' # Mobilenet
    #MODEL_HASH='9302718f4b77d0d508516a0365a13c44affe7eda' # Resnet18
    WORKING_DIR="/tmp/mining_task_1"
    TOP_K=1000
    $MIR_EXE mining --model-hash "$MODEL_HASH"  -t "$DEMO_PASCAL_BRANCH_MINING" -w "$WORKING_DIR" --media-location "$ASSET_LOCATION_ABS" --model-location "$MODEL_FOLDER_ABS" -topk "$TOP_K" --base-task-id $DEMO_COCO_BRANCH
    cp "$WORKING_DIR/out/result.tsv" $INTERMEDIATE_FOLDER_ABS
    printf 'done mining\n'
}

process_merge_train() {
    if [ `git rev-parse --quiet --verify refs/heads/$DEMO_MERGE_AND_TRAINING` ]; then
        printf '%s\n' "Branch name $DEMO_MERGE_AND_TRAINING already exists.";
        $MIR_EXE checkout $DEMO_MERGE_AND_TRAINING
        return 0
    fi

    $MIR_EXE checkout $DEMO_PASCAL_BRANCH_MINING

    TASK_ID='merge_task_1'
    $MIR_EXE merge -t $DEMO_MERGE_AND_TRAINING --host-id $DEMO_PASCAL_BRANCH_MINING --guest-ids $DEMO_PASCAL_BRANCH_FILTER

    if ! [[ -n "$(docker images -q $TRAIN_IMAGE)" ]]; then
        echo "training docker image not exist";
        #exit 1;
    fi

    TASK_ID='training_task_2'
    WORKING_DIR="/tmp/$TASK_ID"
    $MIR_EXE train -p $MATCHED_KEYWORDS -tp 0.99 -vp 0.01 --model-location $MODEL_FOLDER_ABS -t $DEMO_MERGE_AND_TRAINING --media-location $ASSET_LOCATION_ABS -force -w $WORKING_DIR
    printf 'done training\n';
}

demo_main "$@"
printf 'demo done.\n'
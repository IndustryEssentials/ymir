# 如何导入外部模型

## 外部模型的准备

假设有一个在 ymir 系统外部进行的基于 mxnet 的训练过程，这个训练过程在第 1000 个 epoch 的时候产生了模型 `model-1000.params` 和 `model-symbol.json`，其 mAP 是 0.3，在第 2000 个 epoch 的时候产生了模型 `model-2000.params` 和 `model-symbol.json`，其 mAP 是 0.6，现在想要将这个过程中产生的模型导入 ymir 系统中。

在导入外部模型之前，需要做如下准备：

1. 将训练过程中产生的文件，如 `model-1000.params`, `model-2000.params`, `model-symbol.json`，拷贝到同一路径下；

2. 在此路径下生成 `ymir-info.yaml` 文件，其格式如下：

``` yaml
executor_config:
  class_names:  # 训练目标，必要
  - person
  - cat
stages:  # 训练过程中产生的 model stages，必要
  stage_1000:  # 在 epoch 1000 时产生的 model stage name，必要
    files:  # 此 model stage 对应的文件，必要
    - model-1000.params
    - model-symbol.json
    mAP: 0.3  # 此 model stage 的 mAP，必要
    stage_name: stage_1000  # model stage name，必要
    timestamp: 1655975204  # model stage 的创建时间，用 `ls --time-style=+%s -l` 取得文件创建时间，必要
  stage_2000:
    files:
    - model-2000.params
    - model-symbol.json
    mAP: 0.6
    stage_name: stage_2000
    timestamp: 1655975205
best_stage_name: stage_2000  # 最好的 model stage name，必要
task_context:
  executor: sample-executor  # 训练模型时所用的镜像，非必要
  mAP: 0.6  # 最好的 model stage 对应的 mAP
  producer: fenrir-z  # 模型作者
```

3. 将 `ymir-info.yaml` 和所有模型文件打包：

``` bash
tar -czvf model.tar.gz model-1000.params model-2000.params model-symbol.json ymir-info.yaml
```

## 如何导入

可以使用 ymir 的模型导入功能，也可以使用以下命令行：

``` bash
mir models --package-path /path/to/model.tar.gz
           --root /path/to/mir/repo
           --dst-rev model-0@model-0  # xxx@xxx 格式，导入模型即意味着产生一个新的模型分支
           --model-location /path/to/ymir-models  # ymir 系统模型保存路径
           -w /path/to/tmp/work/dir  # 模型导入时的临时工作目录
```

如果导入成功，控制台会显示以下信息：

``` plain
pack success, model hash: xxxxxxxxxxxxxxxx, best_stage_name: stage_2000, mAP: 0.6
```

这里产生的 model hash 就是此模型在 ymir 中的 id，当使用命令行进行挖掘，推理时，可以提供此 model hash 和 model stage 给相应的命令。

## 限制与注意事项

1. 在 `外部模型的准备` 一节中的第 2 步中标明 `必要` 的字段都需要提供

2. 模型的继续训练，推理，挖掘等任务需要配合特定镜像完成，所以需要在导入模型时，明确其使用的镜像，使其在后续流程中可用

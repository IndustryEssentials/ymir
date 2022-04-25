# ymir 用户自定义镜像制作指南

## 目的

此文档面向以下人员：

* 为 ymir 开发训练，挖掘及推理镜像的算法人员及工程人员

* 希望将已经有的训练，挖掘及推理镜像对接到 ymir 系统的算法及工程人员

此文档将详细描述如何使用 ymir executor framework 开发新的镜像。

## 准备工作

1. 下载 ymir 工程：

```
git clone --recursive git@github.com:IndustryEssentials/ymir.git
```

2. 建立自己的工作目录，并将相关文件拷入到自己的工作目录下：

```
mkdir ~/my_executor && cp -r ymir/docker_executor/sample_executor ~/my_executor
```

3. 安装 nvidia-docker 及 python3.8 以上版本（含 3.8）

## ymir 对镜像的调用流程

ymir 通过 mir train / mir mining / mir infer 命令启动镜像，遵循以下步骤：

1. 导出镜像需要用的图像资源以及标注资源文件

2. 准备镜像配置 config.yaml 及 env.yaml

3. 通过 nvidia-docker run 激活镜像，在启动镜像时，将提供以下目录及文件：

| 目录或文件 | 说明 | 权限 |
| --- | --- | --- |
| `/in/env.yaml` | 任务类型，任务 id，数据集索引文件位置等信息 | 只读 |
| `/in/*-index.tsv` | 数据集索引文件 | 只读 |
| `/in/config.yaml` | 镜像本身所用到的超参等标注信息 | 只读 |
| `/in/assets` | 图像资源存放目录 | 只读 |
| `/in/annotations` | 标注文件存放目录 | 只读 |
| `/out/tensorboard` | tensorboard 日志写入目录 | 读写 |
| `/out/models` | 结果模型保存目录 | 读写 |

4. 镜像启动以后，完成自己的训练、挖掘或推理任务，将相应结果写入对应文件，若成功，则返回 0，若失败，则返回非 0 错误码

5. ymir 将正确结果或异常结果归档，完成整个过程

## 训练、挖掘与推理镜像的通用部分开发

app/start.py 展示了一个简单的镜像执行部分，此文档也将基于这个样例工程来说明如何使用框架来开发镜像。

关于这个文件，有以下部分值得注意：

1. 在 Dockerfile 中，最后一条命令说明了：当此镜像被 ymir 系统通过 nvidia-docker run 启动时，默认执行的是 `python /app/start.py` 命令，也就是此工程中的 `app/start.py` 文件

2. 镜像框架相关的所有内容都在 `executor` 包中，包括以下部分：

  * `executor.env`：环境，提供任务类型，任务 id 等信息

  * `dataset_reader`：使用数据集读取器来取得数据集信息

  * `result_writer`：写入训练，挖掘以及推理结果

  * `monitor`：写入进度信息

3. 使用 `env.get_current_env()` 可以取得默认的 EnvConfig 实例，这个实例来源于文件 `/in/env.yaml`，如果出于测试的目的想要更改这个默认文件，可以直接更改 `settings.DEFAULT_ENV_FILE_PATH`，但在实际封装成镜像的时候，应该把它的值重新指回成默认的 `/in/env.yaml`

4. 在 `start()` 方法中，通过 `env.get_current_env()` 中的 `run_training` / `run_mining` / `run_infer` 来判断本次需要执行的任务类型。如果任务类型是本镜像不支持的，可以直接报错

5. 虽然 `app/start.py` 展示的是一个训练，挖掘和推理多合一的镜像，开发者也可以分成若干个独立的镜像，例如，训练一个，挖掘和推理合成一个

## 训练过程

`app/start.py` 中的函数 `_run_training` 展示了一个训练功能的样例，有以下部分需要注意：

1. 超参的取得

  * 使用 `env.get_executor_config()` 取得外部传入的超参数等信息

  * 每个训练镜像都应该准备一个超参模板 `training-template.yaml`，ymir 系统将以此模板为基础提供超参

  * 以下 key 为保留字，将由系统指定：

| key | 类型 | 说明 |
| --- | --- | --- |
| class_names | list | 类别 |
| gpu_id | str | 可使用的 gpu id，以英文逗号分隔，如果为空，则表示用 cpu 训练 |
| pretrained_model_params | list | 预训练模型列表，如果指定了，则表示需要基于此模型做继续训练 |

2. 训练集和验证集的取得：使用 `dataset_reader.item_paths()` 方法取得训练集和验证集的图片路径和标注文件路径，这个函数是一个生成器，可以通过循环来遍历它的所有值

3. 模型的保存

  * 在 `EnvConfig.output.models_dir` 中提供了模型的保存目录，用户可以使用 pytorch, mxnet, darknet 等训练框架自带的保存方法将模型保存在此目录下

  * 之后，可以使用 `result_writer.write_training_result()` 方法保存训练结果的摘要，这些内容包括：不带目录的模型名称，mAP，每个类别的 APs

4. 进度的记录：使用 `monitor.write_monitor_logger(percent)` 方法记录任务当前的进度，实际使用时，可以每隔若干轮迭代，根据当前迭代次数和总迭代次数来估算当前进度（一个 0 到 1 之间的数），调用此方法记录

## 挖掘过程

所谓挖掘过程指的是：提供一个基础模型，以及一个不带标注的候选数据集，在此候选数据集上进行 active learning 算法，得到每张图片的得分，并将这个得分结果保存。

`app/start.py` 中的函数 `_run_mining` 展示了一个数据挖掘过程的样例，有以下部分需要注意：

1. 参数的取得

  * 使用 `env.get_executor_config()` 取得外部传入的参数

  * 每个挖掘镜像都应该准备一个参数模板 `mining-template.yaml`，ymir 系统将以此模板为基础提供参数

  * 以下 key 为保留字，将由系统指定：

| key | 类型 | 说明 |
| --- | --- | --- |
| class_names | list | 类别 |
| gpu_id | str | 可使用的 gpu id，以英文逗号分隔，如果为空，则表示用 cpu 训练 |
| model_params_path | list | 模型路径列表，镜像应该从里面选择自己可以使用的模型，如果有多个模型可以使用，直接报错 |

2. 候选集的取得

  * 进行挖掘任务时，所使用的数据集是一个没有带标注的候选集，可以使用 `dataset_reader.item_paths()` 取得图片资源的路径列表，这个函数是一个生成器，可以通过循环来遍历它的所有值

3. 结果的保存

  * 使用 `result_writer.write_mining_result()` 对挖掘结果进行保存

## 推理过程

所谓推理过程指的是：提供一个基础模型，以及一个不带标注的候选数据集，在此候选数据集上进行模型推理，得到每张图片的 detection 结果（框，类别，得分），并保存此结果。

`app/start.py` 中的函数 `_run_infer` 展示了一个推理过程的样例，有以下部分需要注意：

1. 参数的取得：同数据挖掘过程

2. 候选集的取得：同数据挖掘过程

3. 结果的保存

  * 推理结果本身是一个 dict，key 是候选集图片的路径，value 是一个由 `result_writer.Annotation` 构成的 list

  * 使用 `result_writer.write_infer_result()` 保存推理结果

## 镜像打包

可以在 `sample_executor/Dockerfile` 的基础上构建自己的打包脚本，打包时需要确认 `settings.DEFAULT_ENV_FILE_PATH` 的值为 `/in/env.yaml`

## 测试

可以使用以下几种方式进行测试：

1. 通过 ymir 命令行启动 mir train / mir mining / mir infer 命令进行测试

2. 通过 ymir web 系统进行测试

3. 修改 settings.DEFAULT_ENV_FILE_PATH，将其指向自己的配置，然后直接启动可执行文件进行测试，这需要做以下准备：

  * executor 目录必须在 PYTHONPATH 中

  * settings.DEFAULT_ENV_FILE_PATH 需要指向自己的 env.yaml 中，一个典型的 env.yaml 具有以下结构：

```
task_id: task0
run_training: True
run_mining: False
run_infer: False
input:
    root_dir: /in
    assets_dir: assets
    annotations_dir: annotations
    models_dir: models
    training_index_file: train-index.tsv
    val_index_file: val-index.tsv
    candidate_index_file: candidate-index.tsv
    config_file: config.yaml
output:
    root_dir: /out
    models_dir: models
    tensorboard_dir: tensorboard
    training_result_file: result.yaml
    mining_result_file: result.txt
    infer_result_file: infer-result.yaml
    monitor_file: monitor.txt
```

  * 根据任务的类型，制作 `train-index.tsv`, `val-index.tsv` 和 `candidate-index.tsv`，此文件每一行都是一个图像和标注，之间以 `\t` 分隔

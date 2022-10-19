# ymir 与功能性 docker container 数据传输接口

| 协议文档版本 | ymir 版本 | 说明 | 镜像适配方式 |
| --- | --- | --- | --- |
| [0.0.0](https://raw.githubusercontent.com/IndustryEssentials/ymir/release-1.1.0/docs/ymir-cmd-container.md) | 0.0.0 - 1.1.0 | 初始版本 | |
| [1.0.0](https://raw.githubusercontent.com/IndustryEssentials/ymir/ymir-pa/docs/ymir-cmd-container.md) | 1.2.0 - 1.2.2 | 增加关于中间模型的描述 | 使用 `write_model_stage` 方法保存训练产出的中间模型 |
| 1.1.0 | 2.0.0 - | 4.3.2 节，训练完成后，模型保存策略更改<br>4.4.2 节，推理完成后，推理结果保存的节点由 annotations 改为 boxes | 1. 保存中间模型时，将模型文件保存至以 `中间模型名称` 命名的子目录中<br>2. 保存推理结果时，将原来的 annotations 键改为 boxes |

## 1. 关于此文档

此文档用于规定 ymir 与功能性 docker container 之间的数据交互方式，这些 docker container 用于模型训练，挖掘及推理任务。

此文档面向的读者为模型训练，挖掘及推理镜像的开发者们。

## 2. ymir 与 docker container 的协作方式

ymir 系统有两种用户交互方式：web 方式和命令行方式。

对于 web 用户来说，训练镜像，以及与之配套的挖掘与推理镜像合在一起，称为一个镜像方案，也就是说，一旦用户通过 web 页面，使用了某个训练镜像来训练模型，那挖掘与推理镜像也随之确定了。

而命令行用户在使用训练，挖掘与推理功能时，通过 `--executor` 参数来决定使用哪个镜像。

### 2.1. ymir 与训练镜像的协作方式

模型的训练过程分为以下几个步骤：

1. ymir 导出对应的训练集与验证集至指定的工作目录，并准备 `config.yaml` 文件；

2. ymir 通过 `nvidia-run` 将指定的工作目录，以及训练所需要的全部配置文件挂载至 4.3 节所述的位置，启动训练镜像，并等待完成；

3. 在此过程中，镜像完成以下事务：

    3.1. 读取 `/in/train-index.tsv` 及 `/in/val-index.tsv` 中的训练集与验证集中的图片和标注信息；

    3.2. 启动训练流程；

    3.3. 将训练结果保存至 `/out/models` 目录，并将最好的一个结果及其 mAP 写入 `/out/result.yaml` 中。

4. 训练成功完成后，ymir 读取位于 `out/models` 目录下的输出模型，校验其有效性，并将模型归档。

### 2.2. ymir 与挖掘及推理镜像的协作方式

ymir 对挖掘与推理这两个动作有如下定义：

> 推理：使用模型对图像进行前处理-前向-后处理，从而得出结果的过程。

> 挖掘：在已经具备模型和图像的前提下，使用 active learning 等技术对图像进行打分，并将结果图像依据分数从高到低进行排序；

ymir 的挖掘与推理镜像需要同时支持以下两种场景的使用：

#### 2.2.1. 推理

在此场景中，用户想在某个数据集上，或者某些图片上，对模型的效果进行初步验证，这个过程分为以下几个步骤：

1. ymir 将需要用到的图片导出到工作目录，并准备好 `config.yaml` 文件；

2. ymir 通过 `nvidia-run` 将工作目录，以及推理所需要的全部配置文件挂载至 4.4 节所述的位置，启动镜像，并等待完成；

3. 在此过程中，镜像完成以下事务：

    3.1. 从 `/in/candidate-index.tsv` 中读取所有图像资源；

    3.2. 使用 `/in/models` 位置的模型及预先写好的前后处理代码，完成推理，并将结果写入到 `/out/infer-result.json`中。

4. 推理成功完成后，ymir 读取位于 `out/infer-result.json` 位置下的输出结果，如果是对于某个特定数据集（而不是图片）进行的推理，则将推理结果写入数据集中，形成一个新的数据集。

#### 2.2.2. 挖掘

在此场景中，用户已经成功训练出了一个模型，希望进一步通过 active learning 等方式，在某个数据集中挑选出对模型下一步训练最为有效的图片，这个过程分为以下几个步骤：

1. ymir 将需要用到的图片导出到工作目录，并准备好 `config.yaml` 文件；

2. ymir 通过 `nvidia-run` 将指定工作目录，以及推理所需要的全部配置文件挂载至 4.4 节所述的位置，启动镜像，并等待完成；

3. 在此过程中，镜像完成以下事务：

    3.1 从 `/in/candidate-index.tsv` 中读取所有图像资源；
    
    3.2 使用上述模型以及合适的算法，对传入的每张图片进行打分，并将打分结果保存至 `/out/result.tsv` 中;

4. 镜像完成后，ymir 收集 `/out/result.tsv` 中的结果，根据其中 topk 的结果筛选数据集

#### 2.2.3. 推理并挖掘

在此场景中，用户已经成功训练出了一个模型，希望进一步通过 active learning 等方式，在某个数据集中挑选出对模型下一步训练最为有效的图片（挖掘过程），同时对这些图片使用这个已经训练好的模型进行一次推理，所得出的结果用于后续标注人员对这批图片进行标注，此过程分为以下几个步骤：

1. ymir 将需要用到的图片导出到工作目录；

2. ymir 通过 `nvidia-run` 将指定工作目录，以及推理所需要的全部配置文件挂载至 4.4 节所述的位置，启动镜像，并等待完成；

3. 在镜像启动过程中，镜像完成以下两个事务：

    3.1. 推理：使用 `/in/models` 位置的模型及预先写好的前后处理代码，完成推理，并将结果写入到 `/out/infer-result.json`中；

    3.2. 挖掘：使用上述模型以及合适的算法，对传入的每张图片进行打分，并将打分结果保存至 `/out/result.tsv` 中。

4. 镜像完成后，ymir 收集 `/out/result.tsv` 中的结果，根据其中 topk 的结果筛选数据集，并将 `/out/infer-result.json` 中的内容保存至结果数据集并归档。

## 3. 镜像自带的文件

| 路径 | 说明 |
| ---- | ---- |
| /img-man/readme.md | 对此镜像功能的描述，主要作用，接受的图像数据格式、标注数据格式、输出结果样式等 |
| /img-man/training-template.yaml | 训练镜像需要将自己使用的配置文件参考模板放在这个位置，供用户提取，并从命令行传入 |
| /img-man/mining-template.yaml <br> /img-man/infer-template.yaml | 挖掘和推理镜像需要将自己使用的配置文件参考模板放在这两个位置，供用户提取，并从命令行传入。当需要镜像同时进行推理和挖掘时，传入的配置文件是两个文件内容的合并 |

## 4. 需要调用者传入的文件

> 注：调用者事先将输入文件挂载到对应位置上，docker container 从这些固定位置上读取输入文件，同时，将输出文件写入到固定挂载的输出位置上。

### 4.1. 约定

以下章节，输入挂载点中所有 `.tsv` 和 `.yaml` 文件中出现的路径都是绝对路径。

### 4.2. 共同部分

#### 4.2.1. 日志挂载点

| 路径 | 说明 |
| ---- | ---- |
| /out/monitor.txt | 必要，模型训练进度的输出文件。<br>只保留最新的一条记录，记录不累加。<br>记录格式参考注1 |
| /out/monitor-log.txt | 非必要，短日志文件的输出位置，每一行都是一条记录<br>记录格式参考注2 |
| /out/log.txt | 非必要，长日志文件的输出位置，允许截断。 |

注1. `monitor.txt` 的格式如下：

```
<task_id>\t<timestamp>\t<percent>\t<status>\n
<message>
```

其中：

* `task_id` 是任务id，在任务启动时，由 `config.yaml` 传入

* `timestamp` 是写入监视信息的时间戳，单位为秒，保留六位小数。

* `percent` 是一个0-1之间的数，标识了任务执行的百分比

* `status` 状态标识，分为

    * 1（尚未开始）

    * 2（正在进行）

    * 3（正常结束）

    * 4（异常结束）

* `message` 是自定义信息，比如异常结束可以写入具体的错误原因，backtrace信息等

例如：
```
train_0 1622552974 0.5 2
```

或者：

```
train_0 1622552974 1 4
no training data found
```

注2. `monitor-log.txt` 的格式如下：

```
<task_id><tab><timestamp><tab><percent><tab><status>
```

这个文件主要关注任务状态的切换，例如什么时候创建，什么时候开始运行，什么时候百分比是多少，例如：

```
task_0    1622552964    0    pending
task_0    1622552965    0    running
task_0    1622552966    0.1    running
...
task_0    1622552975    1    done
```

#### 4.2.2. 容器的启动方式

* 所有docker image都通过 `nvidia-docker run` 命令启动

* 在 `/usr/bin` 下面都需要设置一个启动任务的脚本：`/usr/bin/start.sh`（不带参数）

* 所有配置全都放在 `/in/config.yaml` 下面

    * 特别的，如果用户需要同时在一个镜像中完成挖掘和推理任务，传入的 `/in/config.yaml` 将是挖掘配置和推理配置的合并

* 在任务执行过程中，所有输出过程如果遇到异常（比如写入失败、没有写入权限等），则直接报错退出；

* 所有输入过程如果遇到异常（如 `index.tsv` 里面所指示的图像文件或标注文件不存在），也直接报错退出

### 4.3. training 镜像输入/输出挂载格式

#### 4.3.1. 输入挂载点

| 路径 | 说明 |
| ---- | ---- |
| /in/train-index.tsv | 必要，训练集图像及标注的索引文件，每一行都是图片文件路径和标注路径<br>* 图片文件为jpg，png等常用格式（但不保证一定有扩展名）；<br>* 标注文件可以是csv，txt，xml，json格式，拥有和图片相同的主文件名。 |
| /in/val-index.tsv | 必要，验证集图像及标注的索引文件，格式同/in/train-index.tsv |
| /in/config.yaml | 必要，配置项所在的文件，YAML 格式，具体配置项由调用双方商定，注1中列出了几个固定的键 |
| /in/assets | 必要，图像资源所在的目录，只读 |
| /in/annotations | 必要，图像标注所在的目录 |

注1. `config.yaml` 文件的固定保留键

* `task_id`: 任务id，只含英文数字下划线，用于标识或区别任务，会出现在 `/out/monitor.txt` 中，也可以出现在日志中

* `class_names`：训练的物体类别名称

* `gpu_id`：使用哪几块 GPU，用逗号隔开，如果为空，则使用 CPU 训练

* `pretrained_model_params`: 预训练模型文件的路径列表，如果留空，则从头开始训练，如果非空，则从这个列表中找到镜像支持的模型文件，并在此模型的基础上继续训练

* `export_format`: 希望 ymir 向此镜像提供的数据格式，由 `标注格式` 与 `图像格式` 两部分组成，中间用英文冒号分隔，例如 `det-voc:raw` 表示导出原始图像，以及 voc 格式的检测标注，如果此项留空或者不存在，则只导出图像，不导出标注

    * `标注格式` 可取以下值：

        * `det-voc`: 导出 voc 格式的检测标注

        * `det-ark`: 导出 csv 格式的检测标注（class id, x, y, w, h, annotation quality, rotate angle）

        * `det-ls-json`: 导出适合 LabelStudio 使用的检测标注

        * `seg-poly`: 导出 polygon 格式的分割标注

        * `seg-mask`: 导出 mask 类型的分割标注

    * `图像格式` 目前只能指定为 `raw`

#### 4.3.2. 输出挂载点

| 路径 | 说明 |
| ---- | ---- |
| /out/log.txt | 参考共同部分 |
| /out/monitor.txt | 参考共同部分 |
| /out/monitor-log.txt | 参考共同部分 |
| /out/models | 必要，最终生成的模型的输出目录，模型文件存放在以 stage_name 命名的子目录中。<br>/out/models 下必须有一个 `result.yaml` 文件，格式参考注1 |

注1. `result.yaml` 文件的格式如下：

``` yaml
best_stage_name: epoch_50  # 最优的中间模型名称
model_stages:
  epoch_10:  # 中间模型名称：epoch_10
    files:   # 中间模型对应的文件列表，这些文件在 /out/models 下面
      - 149_1.000-symbol.json
      - 149_1.000-0149.params
    mAP: 0.6 # 中间模型对应的 mAP
    stage_name: epoch_10
    timestamp: 1663934682 # 创建时间对应的 timestamp
  epoch_50:
    files:
      - 149_1.000-symbol.json
      - 149_1.000-0149.params
    mAP: 0.8
    stage_name: epoch_50
    timestamp: 1663934682
```

### 4.4. inference / mining 镜像输入/输出挂载格式

#### 4.4.1. 输入挂载点

| 路径 | 说明 |
| ---- | ---- |
| /in/candidate-index.tsv | 必要，图片索引文件，此文件的每一行内容都是一个指向图片的路径，图片文件为jpg，png等常用格式（但不保证一定有扩展名） |
| /in/models | 推理时使用的模型所在的目录 |
| /in/config.yaml | 必要，配置项所在的文件，YAML 格式，具体配置项由调用双方商定，注1中列出了几个固定的键 |

注1: `config.yaml` 文件的固定保留键

* `task_id`: 任务id，只含英文数字下划线，用于标识或区别任务，会出现在 `/out/monitor.txt` 中，也可以出现在日志中

* `model_params_path`: 推理时使用的模型的路径列表，镜像从这个列表中找到镜像支持的模型文件，并使用此模型进行推理或挖掘

* `gpu_id`: 使用 GPU 的 ID，用英文逗号隔开，如果为空，则使用 CPU

* `run_infer`: 取值为0或1，1表示需要将检测/分类结果写入 `/out/infer-result.json` 中，0表示不需要进行推理

* `run_mining`: 取值为0或1，1表示需要将挖掘结果写入 `/out/result.tsv` 中，0表示不需要进行挖掘

* `class_names`: 模型可以识别的类型名称列表

#### 4.4.2. 输出挂载点

| 路径 | 说明 |
| ---- | ---- |
| /out/log.txt | 参考共同部分 |
| /out/monitor.txt | 参考共同部分 |
| /out/monitor-log.txt | 参考共同部分 |
| /out/result.tsv | 最终 mining 结果文件路径，格式见注1 |
| /out/infer-result.json | 模型推理结果，格式见注2 |

注1. `result.tsv` 文件的格式

每一行的内容为：

```
<asset_path>\t<results>
```

其中 asset_path 为 `/in/data/index.tsv` 中所指的资源路径（直接把那里面的内容copy过来），results为模型打分结果，具体数据项由调用双方事先约定

注2. `infer-result.json` 文件的格式

```
{'detection':
  {
    asset-name-0: {'boxes': [{'box': {'x': 30, 'y': 30, 'w': 50, 'h': 50}, 'class_name': 'cat','score': 0.8}, ...]},
    asset-name-1: {'boxes': [...]},
    ...
  }
}
```

其中：

* asset-name-0, asset-name-1就是 `/in/candidate-index.tsv` 里面的资源名称 (base name)

* box的结构为：x, y, w, h，参考系为图片坐标系，左上角为原点

* class_name：模型推断出的类别名称，此名称需要出现在 `/in/config.yaml` 中的 `class_names` 列表中

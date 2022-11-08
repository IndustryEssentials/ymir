# ymir-executor 使用说明

本文档面向使用或定制[ymir-executor](https://github.com/IndustryEssentials/ymir-executor)的用户，在阅读本文档之前，建议阅读以下文档:

- [ymir使用文件](https://github.com/IndustryEssentials/ymir/blob/master/README_zh-CN.md)

- [sample-executor](https://github.com/IndustryEssentials/ymir/tree/master/docker_executor/sample_executor)


## 外部数据集导入ymir-gui系统

- `<1G` 的数据集可以直接`本地导入`，将本地数据集压缩包上传到ymir系统中，数据集具体格式与voc类似，参考[ymir-cmd 准备外部数据](https://github.com/IndustryEssentials/ymir/blob/master/README_zh-CN.md#421-%E5%87%86%E5%A4%87%E5%A4%96%E9%83%A8%E6%95%B0%E6%8D%AE)
  - [sample导入数据集](https://github.com/yzbx/ymir-executor-fork/releases/download/dataset/import_sample_dataset.zip)

  ![](images/ymir-local-import.png)

- `>=1G` 的数据集可以通过`路径导入`，先将数据集复制到ymir工作目录下的子目录`ymir-sharing`，再输入相对路径导入
    ![](images/ymir-path-import.png)

- [其它数据集导入ymir-gui系统的方式](https://github.com/IndustryEssentials/ymir/blob/master/README_zh-CN.md#321-%E8%BF%AD%E4%BB%A3%E6%95%B0%E6%8D%AE%E5%87%86%E5%A4%87)


## ymir系统与ymir-executor镜像的数据传输接口

- 参考[ymir 与功能性 docker container 数据传输接口](https://github.com/IndustryEssentials/ymir/blob/master/docs/ymir-cmd-container.md)

  - ymir会将`/in`与`/out`目录挂载到镜像中

  - 镜像中需要自带`/img-man`目录，辅助ymir系统对镜像类型进行识别，并对超参数页面进行配置

  - 镜像默认以`bash /usr/bin/start.sh`进行启动

  - **注意所有 .tsv 和 .yaml 文件中出现的路径都是绝对路径**

- [sample /in /out](https://github.com/yzbx/ymir-executor-fork/releases/download/dataset/sample_docker_input.zip)

    ![](images/sample_docker_input.png)

- [sample /img-man](https://github.com/IndustryEssentials/ymir/tree/master/docker_executor/sample_executor/app)

  - 注意所有的`xxx-template.yaml`只能是一级`key:value`文件

### 索引文件 train-index.tsv / val-index.tsv / candidate-index.tsv

- 每行由`图像的绝对路径` + `制表符` + `标注的绝对路径`构成

```
{image_abs_path 1}\t{annotation_abs_path 1}
{image_abs_path 2}\t{annotation_abs_path 2}
...
```

- 注意 `candidate-index.tsv` 中只有`图像的绝对路径`

- 图像为常见的jpg, png格式

- 默认标注为`txt`格式，其中`class_id, xmin, ymin, xmax, ymax`均为整数， 所有标注格式介绍见[ymir输入镜像的标注格式]()

```
class_id, xmin, ymin, xmax, ymax, bbox_quality
```


### 超参数配置文件 config.yaml

用户可以在超参数页面看到`xxx-template.yaml`的信息，而`config.yaml` 中的信息，是用户更改过后的。

- 对于训练任务，`config.yaml`提供training-template.yaml中的配置 + ymir-gui 用户自定义配置 + ymir默认配置

- 对于挖掘任务，`config.yaml`提供mining-template.yaml中的配置 + ymir-gui 用户自定义配置 + ymir默认配置

- 对于推理任务，`config.yaml`提供infer-template.yaml中的配置 + ymir-gui 用户自定义配置 + ymir默认配置

```
class_names: # ymir默认配置
- bowl
- cat
- bottle
- cup
- spoon
gpu_id: '0' # ymir默认配置
pretrained_model_params: [] # ymir训练时可选默认配置
model_params_path: [] # ymir推理/挖掘时默认配置
task_id: t0000001000002ebb7f11653630774 # ymir默认配置
img_size: 640 # 用户自定义配置
model: yolov5n # 用户自定义配置
batch_size: 16 # 用户自定义配置
```

### ymir路径配置文件 env.yaml

存放一些路径信息，以及当前进行的任务信息

- 是否进行训练任务: `run_training: true|false`

- 是否进行推理任务：`run_infer: true|false`

- 是否进行挖掘任务: `run_mining: true|false`

```
input:
  annotations_dir: /in/annotations  # 标注文件存放目录
  assets_dir: /in/assets  # 图像文件存放目录
  candidate_index_file: ''  # 挖掘索引文件
  config_file: /in/config.yaml  # 超参配置文件
  models_dir: /in/models  # 预训练模型存放目录
  root_dir: /in # 输入根目录
  training_index_file: /in/train-index.tsv  # 训练索引文件
  val_index_file: /in/val-index.tsv # 验证索引文件
output:
  infer_result_file: /out/infer-result.json # 推理结果文件
  mining_result_file: /out/result.tsv # 挖掘结果文件
  models_dir: /out/models # 训练任务模型权重与信息等存放目录
  monitor_file: /out/monitor.txt  # 任务进度文件
  root_dir: /out  # 输出根目录
  tensorboard_dir: /out/tensorboard # tensorboard结果文件目录
  training_result_file: /out/models/result.yaml # 训练任务结果文件
run_infer: false
run_mining: false
run_training: true
task_id: t0000001000002ebb7f11653630774 # 任务id
```

## ymir输入镜像的标注格式

常见的目标检测标注格式有 `voc` 与 `coco`， ymir 除自身格式， 目前还支持`voc`格式，可在超参数页面通过设置`export_format`对ymir导入镜像的数据格式进行修改。

### 默认数据格式
- `export_format=ark:raw`， 标注文件为`xxx.txt`

### voc 数据格式

- `export_format=voc:raw`， 标注文件为`xxx.xml`

  ![](images/ymir-export-format.png)

- 导出的标注为voc的xml格式

  ![](images/ymir-export-voc-sample.png)

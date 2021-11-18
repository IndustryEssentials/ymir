# ymir 与功能性 docker container 数据传输接口

## 镜像自带

| 路径 | 说明 |
| ---- | ---- |
| /img-man/readme.md | 对此镜像功能的描述，主要作用，接受的图像数据格式、标注数据格式、输出结果样式等 |
| /img-man/training-template.yaml | 训练镜像需要将自己使用的配置文件参考模板放在这个位置，供用户提取，并从命令行传入 |
| /img-man/mining-template.yaml <br> /img-man/infer-template.yaml | 挖掘和推理镜像需要将自己使用的配置文件参考模板放在这两个位置，供用户提取，并从命令行传入 |

## 调用者传入

> 注：调用者事先将输入文件挂载到对应位置上，docker container 从这些固定位置上读取输入文件，同时，将输出文件写入到固定挂载的输出位置上。

### 0. 约定

所有路径是绝对路径，输入起算点为/in目录，输出起算点为/out目录

### 1. 共同部分

#### 日志挂载点

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

* `timestamp` 是写入监视信息的时间戳，单位为毫秒

* `percent` 是一个0-1之间的数，标识了任务执行的百分比

* `status` 状态标识，分为

    * done（正常结束）

	* running（正在进行）

	* error（异常结束）

	* pending（尚未开始）

* `message` 是自定义信息，比如异常结束可以写入具体的错误原因，backtrace信息等

例如：
```
train_0 1622552974000 0.5 running
```

或者：

```
train_0 1622552974000 1 error
no training data found
```

注2. `monitor-log.txt` 的格式如下：

```
<task_id><tab><timestamp><tab><percent><tab><status>
```

这个文件主要关注任务状态的切换，例如什么时候创建，什么时候开始运行，什么时候百分比是多少，例如：

```
task_0    1622552964000    0    pending
task_0    1622552965000    0    running
task_0    1622552966000    0.1    running
...
task_0    1622552975000    1    done
```

#### 容器的启动方式

* 所有docker image都通过 `nvidia-docker run` 命令启动

* 在 `/usr/bin` 下面都需要设置一个启动任务的脚本：`/usr/bin/start.sh`（不带参数）

* 所有配置全都放在 `/in/config.yaml` 下面

* 在任务执行过程中，所有输出过程如果遇到异常（比如写入失败、没有写入权限等），则直接报错退出；

* 所有输入过程如果遇到异常（如 `index.tsv` 里面所指示的图像文件或标注文件不存在），也直接报错退出

### 2. training 镜像输入/输出挂载格式

#### 输入挂载点

| 路径 | 说明 |
| ---- | ---- |
| /in/train | 必要，训练用图像资源及标注对所在的目录，有一个索引文件index.tsv，每一行都是图片文件路径<br>* 图片文件为jpg，png等常用格式（但不保证一定有扩展名）；<br>* 标注文件可以是csv，txt，xml，json格式，拥有和图片相同的主文件名。 |
| /in/val | 必要，验证用图像资源及标注对所在的目录，格式同/in/train |
| /in/test | 非必要，测试用图像资源及标注对所在的目录，格式同/in/train |
| /in/config.yaml | 必要，配置项所在的文件，YAML格式，具体配置项由调用双方商定，注1中列出了几个固定的键 |

注1. `config.yaml` 文件的固定保留键

* `task_id`: 任务id，只含英文数字下划线，用于标识或区别任务，会出现在/out/monitor.txt中，也可以出现在日志中

* `class_names`：训练的物体类别名称

* `gpu_id`：使用哪几块gpu，用逗号隔开，如果为空，则使用cpu训练

#### 输出挂载点

| 路径 | 说明 |
| ---- | ---- |
| /out/log.txt | 参考共同部分 |
| /out/monitor.txt | 参考共同部分 |
| /out/monitor-log.txt | 参考共同部分 |
| /out/models | 必要，最终生成的模型的输出目录。<br>必须有一个 `result.yaml` 文件，格式参考注1 |

注1. `result.yaml` 文件的格式如下：

```
map: 1.000
model: 
 - 149_1.000-symbol.json
 - 149_1.000-0149.params
```

### 3. inference / mining 镜像输入/输出挂载格式

#### 输入挂载点

| 路径 | 说明 |
| ---- | ---- |
| /in/candidate | 必要，图片资源，有一个索引文件 `index.tsv`，此文件的每一行内容都是一个指向图片的路径，图片文件为jpg，png等常用格式（但不保证一定有扩展名） |
| /in/model | 推理时使用的模型 |
| /in/config.yaml | 必要，配置项所在的文件，YAML格式，具体配置项由调用双方商定，注1中列出了几个固定的键 |

注1: `config.yaml` 文件的固定保留键

* `task_id`: 任务id，只含英文数字下划线，用于标识或区别任务，会出现在/out/monitor.txt中，也可以出现在日志中

* `model_params_path`: 推理时使用的模型的路径

* `gpu_id`: 使用gpu的id，用英文逗号隔开，如果为空，则使用cpu

* `write_result`: 可选，如果其值为真，则表示需要将检测/分类结果写入 `infer-result.json` 中

#### 输出挂载点

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

其中asset_path为/in/data/index.tsv中所指的资源路径（直接把那里面的内容copy过来），results为模型打分结果，具体数据项由调用双方事先约定

注2. `infer-result.json` 文件的格式

```
{'detection':
  {
    asset-name-0: [{'box': {x: 30,y: 30,w: 50, h: 50}, 'class_name': cat,'conf': 0.8}, ...],
    asset-name-1: [...],
    ...
  }
}
```

其中：

* asset-name-0, asset-name-1就是 `/in/candidate/index.tsv` 里面的资源名称

* box的结构为：x, y, w, h，原图片坐标系

* class_name：模型推断出的类别名称

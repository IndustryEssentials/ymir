# 简介

Hi，您好，欢迎使用 YMIR 模型生产平台。YMIR 系统为算法人员提供端到端的算法研发工具，围绕 AI 开发过程中所需要数据处理、模型训练等业务需求提供一站式服务，推动算法技术进步。目前，YMIR 系统支持目标检测类模型训练，主要用于检测图中每个物体的位置、类别。适合图中有多个主体要识别、或要识别主体位置及数量的场景。

# 专用名词

* 类别/Class：类别一般指用户添加到 YMIR 系统下的关键词，这类关键词通常用于训练、标注，即用户想要在图像中检测出来的目标物体。

* 类别别名/Alias：别名一般和类别的主名对应，当用户为某一个类别添加了别名后，该别名对应的标注框将会在训练中按类别主名来分类训练。

* 数据标签/Asset Tag ：单个图像数据所带有的标签分类，一般指图像的某个属性，如该图像的来源地点、所属场景等。

* 标注框标签/Box Tag：单个标注框所带有的标签分类，一般指标注框的某个属性，如该标注框的质量、分辨率等。

* 训练目标/Target：训练目标由用户在类别中选取，即当前要训练的模型想要检测的目标物体。

* 镜像/DockerImage：运行训练、挖掘和推理任务的环境，YMIR 系统提供一些默认镜像，也支持用户自行开发上传。

* 标准值/GroundTruth(GT)：数据集中正确的标注值，作为待识别目标的参考标注，一般情况下为人工标注。

* 预测标注/Prediction：数据集经过模型推理后产生的标注结果，用于评估模型的识别效果。

* 迭代流程/Iteration：YMIR 提供标准化的模型迭代流程，并且会在每一步操作中帮助用户默认填入上一次的操作结果，普通用户按照既定步骤操作，即可完成完整的模型迭代流程。迭代的主要目标是为了帮助用户获取更优质的训练数据和效果更好的模型。

* 模型部署/Deployment：模型即服务。模型部署是指将模型推理细节打包到模型中，通过一套 API 实现所有深度学习模型的推理工作。提供标准的 HTTP 接口，支持用户快速集成与验证。

# 使用流程

YMIR 系统的使用流程一般分为两类，一类是系统的元操作，包括数据的管理、处理、分析、标注以及模型的训练、诊断、部署等功能，全程可视化简易操作。一类是系统提供的迭代流程，将模型训练中的关键步骤进行拆解，辅助用户填入数据，支持用户流程化地优化模型，获得最终的训练结果。了解更多迭代相关的操作，请跳转至 [模型迭代](README.md#模型迭代)。

接下来我们将详细讲述每个步骤的具体操作，如果有其他问题，请发送邮件到 contact.viesc@gmail.com 进行反馈。

## 创建项目

首先，我们需要在项目管理中【创建项目】，YMIR 系统以项目为维度进行数据、模型的管理。

![create_a_project_1.jpg](https://raw.githubusercontent.com/IndustryEssentials/ymir-images/main/doc_v2/create_a_project_1.jpg)

![create_a_project_2.jpg](https://raw.githubusercontent.com/IndustryEssentials/ymir-images/main/doc_v2/create_a_project_2.jpg)

请注意，项目的训练目标将会默认设为您在启用【迭代流程】时的训练目标。


## 添加数据集

项目创建完成后，在训练之前需要在项目中【添加数据集】，导入并标注数据。

### 添加类别

在上传之前确定想要识别哪几种物体，并上传含有这些物体的数据集。每个类别对应想要在图片中检测出的一种物体，并将对应的类别添加到【类别管理】中。

### 准备数据集

基于添加好的类别准备数据集，格式要求如下：

* 仅支持 zip 格式压缩包文件上传；

* 局域网内上传压缩包大小\<1G, 互联网建议\<200MB，超过 1G 的数据集可以通过路径导入（见 [上传数据集](README.md#上传数据集)）；

* 目前支持图片类型: jpg、jpg、bmp、jpeg，格式不符的图片将不会导入；

* 如果需要同步导入标注文件，则标注的文件格式需要为 Pascal VOC；

* 压缩包文件内图片文件需放入 JPEGImages 文件夹内，标准值文件需放入 Annotations 文件夹内。另外也可添加可选的预测标注文件，需放入 pred 文件夹内，且 pred 文件夹内应包含产生该预测结果的模型信息。压缩包内文件结构如下。点击下载示例文件：[sample_dataset.zip](https://github.com/IndustryEssentials/ymir-images/blob/main/doc_v2/sample_dataset.zip?raw=true)

![sample_zip.jpg](https://raw.githubusercontent.com/IndustryEssentials/ymir-images/main/doc_v2/sample_zip.jpg)

### 上传数据集

在完成了添加类别与数据准备后，点击【添加数据集】按钮，进入添加数据集页面。

![create_a_dataset_1.jpg](https://raw.githubusercontent.com/IndustryEssentials/ymir-images/main/doc_v2/create_a_dataset_1.jpg)

可以通过以下方式导入数据：

1\. 用户本地数据：支持上传压缩包，或通过网络 url、路径导入。

> **Note**
> 
> 路径导入：将数据文件夹存放到 ymir 工作空间目录下的 ymir-sharing 目录，如 /home/ymir/ymir-workspace/ymir-sharing/VOC2012, 输入基于 ymir-sharing 相对路径：VOC2012

![create_a_dataset_2.jpg](https://raw.githubusercontent.com/IndustryEssentials/ymir-images/main/doc_v2/create_a_dataset_2.jpg)

2\. 平台已有数据：支持复制该用户下的其他数据集或导入平台已有的公共数据集。

![create_a_dataset_3.jpg](https://raw.githubusercontent.com/IndustryEssentials/ymir-images/main/doc_v2/create_a_dataset_3.jpg)

## 数据挖掘

YMIR 为用户提供成熟的挖掘算法，数据挖掘的主要目的是为了在未标注的数据中找到有利于模型训练的数据。一般挖掘的目标数据集来源于现场数据或相关场景，通过挖掘后可以在其中找出高价值的优质数据并在标注操作中完成标注，从而在扩充训练集的同时降低标注成本。

首先选择要挖掘的数据集，点击**挖掘**操作，创建挖掘任务。

![mining_1.jpg](https://raw.githubusercontent.com/IndustryEssentials/ymir-images/main/doc_v2/mining_1.jpg)

![mining_2.jpg](https://raw.githubusercontent.com/IndustryEssentials/ymir-images/main/doc_v2/mining_2.jpg)

挖掘模型应选用期望提升效果的模型，如果缺少模型，应前往【模型训练】或【模型导入】获取，其中 topk 值为挖掘出的数据总量。

## 数据标注

上传的数据集如果不包含标注文件或用户需要重新标注，即可进入数据标注页面进行标注。

Step 1 首先选择要标注的数据集，点击**标注**操作，创建标注任务。

![labelling_1.jpg](https://raw.githubusercontent.com/IndustryEssentials/ymir-images/main/doc_v2/labelling_1.jpg)

Step 2 填写标注需要的内容，标注目标可在当前用户下的类别列表中选择，支持上传标注标准文档，如果用户尚未注册标注平台的账户，可点击下方链接跳转至标注平台注册账号。

![labelling_2.jpg](https://raw.githubusercontent.com/IndustryEssentials/ymir-images/main/doc_v2/labelling_2.jpg)

Step 3 标注任务创建完成后，用户可以通过查看标注数据集的详情，跳转至标注平台自行标注。

![labelling_3.jpg](https://raw.githubusercontent.com/IndustryEssentials/ymir-images/main/doc_v2/labelling_3.jpg)

## 数据分析

您可从【项目管理】下左侧菜单操作列点击【数据集分析】进入该功能页面。

数据分析旨在对您数据集中的图像数据进行质量检测，通过提供客观指标，为您对数据集的下一步操作（标注、训练、诊断等）进行参照引导。

整体质检报告将包括对标准值、预测标注两个层面的指标进行统计。

分析结果分为整体指标和分布指标两类。整体指标包括数据集存储大小、标注框总数、图片平均标注框数量、以及已标注图片占比四类；分布指标包括图像存储大小分布、图像高宽比分布、图像分辨率分布、图像质量分布、标注框分辨率分布以及类别占比分布六类。

可以通过切换数据集查看不同数据集的分析报告，支持多选数据集进行比对。

![data_analysis_1.jpg](https://raw.githubusercontent.com/IndustryEssentials/ymir-images/main/doc_v2/data_analysis_1.jpg)

## 模型训练

### 功能页面

您可从【项目管理】下左侧菜单操作列点击【模型训练】进入该功能页面。

![training_1.jpg](https://raw.githubusercontent.com/IndustryEssentials/ymir-images/main/doc_v2/training_1.jpg)

如果有指定的数据集作为训练集，也可以在数据集的右侧操作入口中进入训练页面。

![training_2.jpg](https://raw.githubusercontent.com/IndustryEssentials/ymir-images/main/doc_v2/training_2.jpg)

### 训练配置

![training_3.jpg](https://raw.githubusercontent.com/IndustryEssentials/ymir-images/main/doc_v2/training_3.jpg)

Step 1 选择镜像

选择此次训练的需要的镜像容器，YMIR 提供默认的开发镜像，支持 yolo v5 训练。如需要其他镜像，可以由管理员前往【我的镜像】-【公共镜像】列表页面拉取更多镜像，具体操作参考 [镜像管理](README.md#镜像管理)。

Step 2 选择训练集

选择您想要用于当前模型训练的数据集，数据集可选列表为当前项目下的数据集，无法跨项目选取。注意请确保选中的数据集已经完成数据标注，否则无法启动训练，在数据集标注质量较高的情况下，可能获得的模型效果也会更好。

Step 3 选择训练目标

训练目标为您本次训练想要识别的物体类别，仅支持在已选中训练集的类别列表中选择，选择完成之后可点击【计算正负样本】按钮计算当前选中类别在训练集中的占比。

Step 4 选择验证集

AI 模型在训练时，每训练一批数据会进行模型效果检验，以验证集的图片作为验证数据，通过结果反馈去调节训练。因此，需要选择一个与训练目标类别一致的数据集作为验证集，用于模型效果的提升。验证集同样需要已标注的数据，否则会影响最终模型的效果。

Step 5 预训练模型

预训练模型：在模型迭代训练时，用户在原训练数据上增加了训练数据，可通过加载原训练数据训练出的模型参数进行模型训练。这样可让模型收敛速度变快，训练时间变短，同时在数据集质量较高的情况下，可能获得的模型效果也会更好。

注：仅可选择同一训练镜像下训练出的模型作为预训练模型。

Step 6 GPU 个数

目前 YMIR 仅支持 GPU 训练，可以在这里调整用于本次训练的 GPU 数量，合理分配资源。

Step 7 超参数配置

超参数配置开关默认关闭，建议对深度学习有一定了解的用户根据实际情况考虑使用，超参数配置在提供镜像内置的参数修改功能外，额外提供「最长边长缩放」配置项。

* 最长边长缩放：可以输入的数值调整训练数据的图像尺寸，将图像的最长边设为您所设置的数值，其他边长按比例缩放。

### 训练模型

点击「开始训练」，训练模型。

* 训练时间与数据量大小有关，1000 张图片可能需要几个小时训练，请耐心等待。

* 模型训练过程中，可以到【模型列表】页面查看模型的训练进度。

![training_4.jpg](https://raw.githubusercontent.com/IndustryEssentials/ymir-images/main/doc_v2/training_4.jpg)

* 想要查看更多的模型训练过程中的信息，可打开【模型详情】页面，点击【训练过程】按钮，查看训练信息。

![training_5.jpg](https://raw.githubusercontent.com/IndustryEssentials/ymir-images/main/doc_v2/training_5.jpg)

![training_6.jpg](https://raw.githubusercontent.com/IndustryEssentials/ymir-images/main/doc_v2/training_6.jpg)

## 模型诊断 

可通过模型推理或者模型诊断了解模型效果：

### 模型推理

通过模型的【推理】操作，在选中的测试集上生成推理结果，支持同时选中多个数据集或模型进行推理。

![inference_1.jpg](https://raw.githubusercontent.com/IndustryEssentials/ymir-images/main/doc_v2/inference_1.jpg)

![inference_2.jpg](https://raw.githubusercontent.com/IndustryEssentials/ymir-images/main/doc_v2/inference_2.jpg)

推理完成后，支持对推理结果进行可视化查看。

![inference_3.jpg](https://raw.githubusercontent.com/IndustryEssentials/ymir-images/main/doc_v2/inference_3.jpg)

![inference_4.jpg](https://raw.githubusercontent.com/IndustryEssentials/ymir-images/main/doc_v2/inference_4.jpg)

![inference_5.jpg](https://raw.githubusercontent.com/IndustryEssentials/ymir-images/main/doc_v2/inference_5.jpg)

当前可视化结果支持对推理结果的指标评估，包括 FP、FN、TP 以及 MTP，支持按类别进行筛选查看。

FP：False Positive，当前测试图片的标准值不包含正确的检测目标，但模型将其错误地识别为了检测目标。即预测结果中被预测为正类的负样本。

FN：False Negative，当前测试图片的标准值为正确的检测目标，但模型未识别到或将其错误地识别为了其他目标。即预测结果中被预测为负类的正样本。

TP：True Positive，即在目标预测类别下，和标准值匹配的模型预测结果。

MTP：Matched True Positive，和预测结果匹配的标准值。

### 模型诊断

在【项目管理】的左侧导航栏中找到【模型诊断】模块，在线评估模型的效果。具体操作为：①选中你要评估的模型，②选择测试集（选中的测试集需要在模型上已完成推理，具体步骤参考 [模型推理](README.md#模型推理)），③调整评估参数，点击诊断。

* 可以通过切换指标来查看不同参数下的模型诊断结果，诊断结果包括 mAP、PR 曲线、精确率、召回率。显示结果示例如下：

![diagnosis_1.jpg](https://raw.githubusercontent.com/IndustryEssentials/ymir-images/main/doc_v2/diagnosis_1.jpg)

![diagnosis_2.jpg](https://raw.githubusercontent.com/IndustryEssentials/ymir-images/main/doc_v2/diagnosis_2.jpg)

查看模型诊断结果时，需要思考在当前业务场景，更关注精确率与召回率哪个指标。是更希望减少误识别，还是更希望减少漏识别。前者更需要关注精确率的指标，后者更需要关注召回率的指标。评估指标说明如下：

mAP：mAP(mean average precision) 是目标检测 (Object Detection) 算法中衡量算法效果的指标。对于目标检测任务，每一类 object 都可以计算出其精确率 (Precision) 和召回率 (Recall)，在不同阈值下多次计算/试验，每个类都可以得到一条 P-R 曲线，可根据曲线下面积可计算 mAP。

精确率： 正确预测的物体数与预测物体总数之比。

召回率： 正确预测的物体数与真实物体数之比。

## 镜像管理

镜像管理为进阶功能，目前仅针对管理员开放，镜像管理中支持用户上传自定义镜像，来实现用户理想的训练、挖掘、推理操作。镜像的具体开发标准请参考 [镜像开发文档](https://github.com/IndustryEssentials/ymir/tree/master/docker_executor/sample_executor)。

### 新增镜像

管理员进入【我的镜像】页面， 点击**新增镜像**按钮，填写镜像名称和地址，完成镜像的添加。

![docker_1.jpg](https://raw.githubusercontent.com/IndustryEssentials/ymir-images/main/doc_v2/docker_1.jpg)

也可通过复制公共镜像的方式进行镜像的添加，进入【公共镜像】页面，点击**复制**按钮，修改名称和描述，完成公共镜像的复制。

![docker_2.jpg](https://raw.githubusercontent.com/IndustryEssentials/ymir-images/main/doc_v2/docker_2.jpg)

### 关联镜像

用户自定义的训练、挖掘和推理镜像，一般来说需要具有关联性，才可保证操作流程可串联。也就是说用户 A 制作的训练镜像所训练出的模型，一般情况下无法适配用户 B 所制作的挖掘或推理镜像。为了便于用户记忆不同类别间的镜像关系，平台特别设计了镜像关联功能。点击训练镜像的**关联**按钮，选择对应的挖掘镜像：

![docker_3.jpg](https://raw.githubusercontent.com/IndustryEssentials/ymir-images/main/doc_v2/docker_3.jpg)

![docker_4.jpg](https://raw.githubusercontent.com/IndustryEssentials/ymir-images/main/doc_v2/docker_4.jpg)

注：目前仅支持由训练镜像关联到挖掘镜像。

## 模型迭代

### 功能概述

一个模型很难一次性就训练到最佳的效果，可能需要结合模型推理结果和诊断数据不断扩充数据和调优。

为此我们设计了模型迭代功能，下图为一个完整的模型迭代流程，用户通过多次迭代，不断地调整训练数据和算法，多次训练，获得更好的模型效果。

![workflow.jpg](https://raw.githubusercontent.com/IndustryEssentials/ymir-images/main/doc_v2/workflow.jpg)

开启迭代后，YMIR 提供标准化的模型迭代流程，并且会在每一步操作中帮助用户默认填入上一次的操作结果，普通用户按照既定步骤操作，即可完成完整的模型迭代流程。当前操作结果如不符合您的预期，您也可以选择跳过当前操作。

### 功能入口

创建项目完成后，您可以在【项目概览】页面中点击**系统辅助式模型生产**按钮进入该页面，也可以直接从【项目管理】下左侧菜单操作列点击【项目迭代】进入。

![iteration_1.jpg](https://raw.githubusercontent.com/IndustryEssentials/ymir-images/main/doc_v2/iteration_1.jpg)

### 迭代前准备

开启迭代需要用户准备好要使用的数据集以及初始模型，各类数据的作用如下：

* 训练集：用于训练的初始数据，训练集的类别需要包含当前项目的目标类别。训练集会在每次迭代的过程中通过版本更新的方式不断地扩充。

* 挖掘集：这类数据集数量较多且可以尚未标注目标类别，一般来源于现场数据，通过挖掘后可以在其中找出优质数据，用于扩充训练数据。当用户认为挖掘集中已无有价值数据，可以自行替换。

* 验证集：用于在模型的训练过程中校验数据，模型迭代过程中使用统一的验
  证集参与训练，可以更好地比对模型训练效果。

* 测试集：用于模型训练完成后的效果测试，一般用在模型的推理和诊断环节，便于比对模型在不同的数据环境下的效果。

* 初始模型：首次迭代用于挖掘的模型，可以由用户自行导入，也支持由用户通过导入后的训练集自行训练。

在迭代准备界面对以上的数据类别分别进行设置，完成后点击**使用迭代功能提升模型效果**按钮，进入迭代流程。

![Iteration_2.jpg](https://raw.githubusercontent.com/IndustryEssentials/ymir-images/main/doc_v2/Iteration_2.jpg)

### 迭代流程

step 1 挖掘数据准备

该操作用于确定待挖掘的数据，在所选挖掘集上进行数据筛选或去重，最终获得的结果就是下一步用于挖掘的数据，此步骤可跳过。

![Iteration_pre_1.jpg](https://raw.githubusercontent.com/IndustryEssentials/ymir-images/main/doc_v2/Iteration_pre_1.jpg)

step 2 数据挖掘

根据上一步获取到的待挖掘数据，设置用户想要挖掘的数据量，其他参数均有迭代系统辅助填写，具体操作可参考[数据挖掘](README.md#数据挖掘)。注意，这里用于挖掘的模型是您上次迭代获取到的最终训练模型（如果是第一次迭代，则这里是您设置的初始模型)，挖掘任务完成后获取挖掘结果数据，此步骤可跳过。

![Iteration_mine_1.jpg](https://raw.githubusercontent.com/IndustryEssentials/ymir-images/main/doc_v2/Iteration_mine_1.jpg)

step 3 数据标注

挖掘后的结果一般不带有用户想要训练的目标类别标注，这是需要对挖掘结果进行人工标注，在迭代流程中点击**数据标注**按钮，进入标注页面，待标注数据为上一步中的挖掘结果，其他操作参考 [数据标注](README.md#数据标注)，此步骤可跳过。

![Iteration_label.jpg](https://raw.githubusercontent.com/IndustryEssentials/ymir-images/main/doc_v2/Iteration_label.jpg)

step 4 更新训练集

迭代的主要目的是扩充用户的训练数据，将已经标注好的挖掘结果合并到之前的训练集中，生成新的训练集版本，用于模型训练。

![Iteration_merge.jpg](https://raw.githubusercontent.com/IndustryEssentials/ymir-images/main/doc_v2/Iteration_merge.jpg)

step 5 模型训练

已合并后的训练集需要再次进行训练产生新的模型，注意，这里的验证集是用户在迭代前所设置的验证集，为了保证模型效果的一致性，暂不支持更改，其他操作参考 [模型训练](README.md#模型训练)。点击**训练**按钮后获得本次迭代的模型结果。

![Iteration_train_1.jpg](https://raw.githubusercontent.com/IndustryEssentials/ymir-images/main/doc_v2/Iteration_train_1.jpg)

step 6 下一轮迭代

如果效果未达到您的要求，可以点击**开启下一轮迭代**按钮继续进行下一次迭代。每轮迭代的流程一致，可按用户的需求自行跳过某些步骤。

step7 查看迭代历史

在完成迭代过程后，如果需要查看之前或者当前迭代的信息，可点击**迭代历史**页面，查看历史的迭代信息。

![Iteration_history.jpg](https://raw.githubusercontent.com/IndustryEssentials/ymir-images/main/doc_v2/Iteration_history.jpg)

## 模型部署

出于性能和速度考虑，算法平台训练产生的模型并不直接使用，而是通过提供一键式模型转换与量化工具，将模型转换至具体硬件平台可使用的模型。

### 本地部署

step 1 进入【模型列表】页面，点击**发布**按钮，发布完成后请前往【模型部署】模块【我的算法】页面查看发布结果。

![release_1.jpg](https://raw.githubusercontent.com/IndustryEssentials/ymir-images/main/doc_v2/release_1.jpg)

![release_2.jpg](https://raw.githubusercontent.com/IndustryEssentials/ymir-images/main/doc_v2/release_2.jpg)

step 2 进入【我的算法】页面， 对选中的已发布模型点击**部署**按钮，进入【模型部署】页面，选择要部署的设备。设备列表为当前服务器环境下的设备，如需要选择其他设备，请前往【设备列表】页面添加。

![deploy_1.jpg](https://raw.githubusercontent.com/IndustryEssentials/ymir-images/main/doc_v2/deploy_1.jpg)

![deploy_2.jpg](https://raw.githubusercontent.com/IndustryEssentials/ymir-images/main/doc_v2/deploy_2.jpg)

![deploy_3.jpg](https://raw.githubusercontent.com/IndustryEssentials/ymir-images/main/doc_v2/deploy_3.jpg)

step 3 部署完成后，可前往设备页面查看模型运行情况。前往【设备列表】页面，点击设备名称，进入设备详情页面查看。在设备的【算法中心】页面可设置算法的开启状态。

![device_1.jpg](https://raw.githubusercontent.com/IndustryEssentials/ymir-images/main/doc_v2/device_1.jpg)

![device_2.jpg](https://raw.githubusercontent.com/IndustryEssentials/ymir-images/main/doc_v2/device_2.jpg)

### 发布到公共算法库

进入【我的算法】页面， 对选中的已发布模型点击**发布到公有算法**按钮，点击**确定**后，算法会交给后台人工审核打包，完成后即可前往【模型部署】-【公有算法】页面查看对应的模型。

![public_alg_1.jpg](https://raw.githubusercontent.com/IndustryEssentials/ymir-images/main/doc_v2/public_alg_1.jpg)

![public_alg_2.jpg](https://raw.githubusercontent.com/IndustryEssentials/ymir-images/main/doc_v2/public_alg_2.jpg)

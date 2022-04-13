## 简介

[English](README.md) | 简体中文

![YMIR](docs/images/YMIR.jpeg)

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**目录**

- [文章引用](#文章引用)
- [1. AI SUITE-YMIR介绍](#1--ai-suite-ymir%E4%BB%8B%E7%BB%8D)
  - [1.1.	主要功能](#11-主要功能)
  - [1.2.	申请试用](#12-申请试用)
- [2. 安装](#2-%E5%AE%89%E8%A3%85)
  - [2.1. 环境依赖](#21-%E7%8E%AF%E5%A2%83%E4%BE%9D%E8%B5%96)
  - [2.2. 安装 YMIR-GUI](#22-%E5%AE%89%E8%A3%85-ymir-gui)
  - [2.3. 安装配置LabelStudio （可选）](#23-%E5%AE%89%E8%A3%85%E9%85%8D%E7%BD%AElabelstudio-%E5%8F%AF%E9%80%89)
- [3. GUI使用-典型模型生产流程](#3-gui%E4%BD%BF%E7%94%A8-%E5%85%B8%E5%9E%8B%E6%A8%A1%E5%9E%8B%E7%94%9F%E4%BA%A7%E6%B5%81%E7%A8%8B)
  - [3.1. 标签管理](#31-%E6%A0%87%E7%AD%BE%E7%AE%A1%E7%90%86)
  - [3.2. 项目管理](#32-项目管理)
    - [3.2.1 迭代数据准备](#321-迭代数据准备)
    - [3.2.2 初始模型准备](#322-初始模型准备)
    - [3.2.3 挖掘数据准备](#323-挖掘数据准备)
    - [3.2.4 数据挖掘](#324-数据挖掘)
    - [3.2.5 数据标注](#325-数据标注)
    - [3.2.6 更新训练集](#326-更新训练集)
    - [3.2.7 合并训练](#327-合并训练)
    - [3.2.8 模型验证](#328-模型验证)
    - [3.2.9 模型下载](#329-模型下载)
- [4. 进阶版：Ymir-CMD line使用指南](#4-%E8%BF%9B%E9%98%B6%E7%89%88ymir-cmd-line%E4%BD%BF%E7%94%A8%E6%8C%87%E5%8D%97)
  - [4.1 安装](#41-%E5%AE%89%E8%A3%85)
    - [方式一：通过pip安装](#%E6%96%B9%E5%BC%8F%E4%B8%80%E9%80%9A%E8%BF%87pip%E5%AE%89%E8%A3%85)
    - [方式二：通过源码安装](#%E6%96%B9%E5%BC%8F%E4%BA%8C%E9%80%9A%E8%BF%87%E6%BA%90%E7%A0%81%E5%AE%89%E8%A3%85)
  - [4.2 典型模型生产流程](#42-%E5%85%B8%E5%9E%8B%E6%A8%A1%E5%9E%8B%E7%94%9F%E4%BA%A7%E6%B5%81%E7%A8%8B)
    - [4.2.1 准备外部数据](#421-%E5%87%86%E5%A4%87%E5%A4%96%E9%83%A8%E6%95%B0%E6%8D%AE)
    - [4.2.2 建立本地repo并导入数据](#422-%E5%BB%BA%E7%AB%8B%E6%9C%AC%E5%9C%B0repo%E5%B9%B6%E5%AF%BC%E5%85%A5%E6%95%B0%E6%8D%AE)
    - [4.2.3 合并及筛选](#423-%E5%90%88%E5%B9%B6%E5%8F%8A%E7%AD%9B%E9%80%89)
    - [4.2.4 训练第一个模型](#424-%E8%AE%AD%E7%BB%83%E7%AC%AC%E4%B8%80%E4%B8%AA%E6%A8%A1%E5%9E%8B)
    - [4.2.5 挖掘](#425-%E6%8C%96%E6%8E%98)
    - [4.2.6 标注](#426-%E6%A0%87%E6%B3%A8)
    - [4.2.7 合并](#427-%E5%90%88%E5%B9%B6)
    - [4.2.8 训练第二个模型](#428-%E8%AE%AD%E7%BB%83%E7%AC%AC%E4%BA%8C%E4%B8%AA%E6%A8%A1%E5%9E%8B)
  - [4.3. 命令参数手册](#43-%E5%91%BD%E4%BB%A4%E5%8F%82%E6%95%B0%E6%89%8B%E5%86%8C)
- [5.  获取代码](#5--%E8%8E%B7%E5%8F%96%E4%BB%A3%E7%A0%81)
  - [5.1  YMIR repos](#51--ymir-repos)
  - [5.2  代码贡献](#52--%E4%BB%A3%E7%A0%81%E8%B4%A1%E7%8C%AE)
  - [5.3  关于训练，推理与挖掘镜像](#53-%E5%85%B3%E4%BA%8E%E8%AE%AD%E7%BB%83%E6%8E%A8%E7%90%86%E4%B8%8E%E6%8C%96%E6%8E%98%E9%95%9C%E5%83%8F)
- [6. 设计理念](#6-设计理念)
  - [6.1.	Life of a dataset](#61-life-of-a-dataset)
    - [6.1.1 数据集介绍](#611-数据集介绍)
    - [6.1.2 分支与数据集的管理](#612-分支与数据集的管理)
- [7.MISC](#7misc)
  - [7.1 常见问题](#71-%E5%B8%B8%E8%A7%81%E9%97%AE%E9%A2%98)
  - [7.2 License](#72-license)
  - [7.3 联系我们](#73-%E8%81%94%E7%B3%BB%E6%88%91%E4%BB%AC)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# 文章引用

如要在您的工作中引用YMIR，请使用下面的Bibtex：

```bibtex
@inproceedings{huang2021ymir,
      title={YMIR: A Rapid Data-centric Development Platform for Vision Applications}, 
      author={Phoenix X. Huang and Wenze Hu and William Brendel and Manmohan Chandraker and Li-Jia Li and Xiaoyu Wang},
      booktitle={Proceedings of the Data-Centric AI Workshop at NeurIPS},
      year={2021},
}
```

# 1.  AI SUITE-YMIR介绍

YMIR(You Mine In Recursion)是一个简化的模型开发产品，专注于AI SUITE开源系列中的数据集版本和模型迭代。

目前人工智能商业化在算力、算法和技术方面达到阶段性成熟。AI应用在产品落地过程中经常会遇到无法大规模扩展的瓶颈，例如人才紧缺、开发成本高、迭代周期长等问题。

在此基础上，为了降低企业利用AI技术的成本，加速推进AI赋能企业，YMIR系统为算法人员提供端到端的算法研发工具，围绕AI开发过程中所需要的数据处理、模型训练等业务需求提供一站式服务，推动算法技术应用。

YMIR主要以数据为中心，提供高效模型开发迭代能力，集成了主动学习方法、数据和模型版本控制，同时集成工作空间等概念，实现多个任务特定数据集的并行快速迭代。平台设计开放API来集成第三方工具，支持企业将有限的人力投入到应用的开发中，以更低成本实现AI到行业的落地。

## 1.1. 主要功能

在AI开发过程中，基本流程通常可以归纳为几个步骤：确定目的、准备数据、训练模型、评估模型、部署模型。

*  确定目的：在开始AI开发之前，必须明确要分析什么？要解决什么问题？商业目的是什么？基于商业的理解，整理AI开发框架和思路。例如，图像分类、物体检测等。不同的项目对数据的要求，使用的AI开发手段也是不一样的。
*  准备数据：数据准备主要是指收集和预处理数据的过程。按照确定的分析目的，有目的性的收集、整合相关数据，数据准备是AI开发的一个基础。此时最重要的是保证获取数据的真实可靠性。而事实上，不能一次性将所有数据都采集全，因此需要反复新增数据来调整优化。
*  训练模型：俗称“建模”，指通过分析手段、方法和技巧对准备好的数据进行探索分析，从中发现因果关系、内部联系和业务规律，为商业目的提供决策参考。训练模型的结果通常是一个或多个机器学习或深度学习模型，模型可以应用到新的数据中，得到预测、评价等结果。
*  评估模型：训练得到模型之后，整个开发过程还不算结束，需要对模型进行评估和考察。通过现有的数据往往不能一次性获得一个满意的模型，需要反复的调整算法参数，新增有效数据，不断地迭代和评估生成的模型。一些常用的指标，如mAP，能帮助您有效的评估，最终获得一个满意的模型。
*  部署模型：模型的开发训练，是基于之前的已有数据（有可能是测试数据），而在得到一个满意的模型之后，需要将其应用到正式的实际数据或新产生数据中，进行预测、评价、或以可视化和报表的形式把数据中的高价值信息以精辟易懂的形式提供给决策人员，帮助其制定更加正确的商业策略。

YMIR平台主要满足用户规模化生产模型的需求，为用户提供良好、易用的展示界面，便于数据和模型的管理与查看。平台包含项目管理、标签管理、系统配置等主要功能模块，支持实现以下主要功能：

| 功能模块     |    一级功能    | 二级功能          | 功能说明      |
|----------|-----------|------------|-----------------------------------------|
|项目管理|项目管理|项目编辑|支持添加、删除、编辑项目及项目信息|
|项目管理|迭代管理|迭代准备|支持设置迭代所需要的数据集和模型信息|
|项目管理|迭代管理|迭代步骤|支持将上一轮的数据填充到下一步对应的任务参数中|
|项目管理|迭代管理|迭代图表|支持将迭代过程中产生的数据集和模型按图表比对的方式展示在界面中|
|项目管理|数据集管理|导入数据集|支持用户通过复制公共数据集、url地址、路径导入以及本地导入等方式导入准备好的数据集|
|项目管理|数据集管理|查看数据集|支持图片数据及标注的可视化查看、以及历史信息的查看|
|项目管理|数据集管理|编辑数据集|支持数据集的编辑、删除|
|项目管理|数据集管理|数据集版本|支持在源数据集上创建新的数据集版本，版本号按时间递增|
|项目管理|数据集管理|数据预处理|支持图片数据的融合、筛选、采样操作|
|项目管理|数据集管理|数据挖掘|支持在海量数据集中找到对模型优化最有利的数据|
|项目管理|数据集管理|数据标注|支持为图片数据添加标注|
|项目管理|数据集管理|数据推理|支持通过指定模型为数据集添加标注|
|项目管理|模型管理|模型导入|支持本地导入模型文件到平台|
|项目管理|模型管理|训练模型|持自选数据集、标签，并根据需求调整训练参数来训练模型，完成后可查看对应的模型效果|
|项目管理|模型管理|模型验证|支持上传单张图片，通过可视化的方式查看模型在真实图片中的表现，以校验模型的精确度|
|标签管理|标签管理|新增标签|支持训练标签的主名和别名的添加|
|系统配置|镜像管理|我的镜像|支持添加自定义镜像到系统中（仅管理员可用）|
|系统配置|镜像管理|公共镜像|支持查看其他人上传的公共镜像并复制到自己的系统中|
|系统配置|权限配置|权限管理|支持对用户的权限进行配置（仅管理员可用）|

## 1.2. 申请试用

我们提供一个在线的体验版本，方便您试用，如有需要，请填写[YMIR在线系统申请试用表](https://alfrat.wufoo.com/forms/z2wr9vz0dl1jeo/)，我们会将试用信息发送至您的邮箱。

# 2. 安装

![YMIR总流程图](docs/images/processing.png)

**用户如何选择安装GUI or CMD：**

1.普通用户推荐安装GUI，支持模型的训练、优化完整流程；

2.如需要修改系统默认的配置，推荐安装CMD；

本章节为YMIR-GUI的安装说明，如需使用CMD，请参考[Ymir-CMD line使用指南](#4-进阶版ymir-cmd-line使用指南)。

## 2.1. 环境依赖

1. GPU版本需要GPU，并安装nvidia驱动: [https://www.nvidia.cn/geforce/drivers/](https://www.nvidia.cn/geforce/drivers/) 

2. 需要安装docker：
*  Docker & Docker Compose 安装： [https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/) 
*  NVIDIA Docker安装： [https://github.com/NVIDIA/nvidia-docker](https://github.com/NVIDIA/nvidia-docker)
 
3. 推荐服务器配置：
*  NVIDIA GeForce RTX 2080 Ti 12G
*  显存最大值到达9974MiB

## 2.2. 安装 YMIR-GUI

需要保证[环境依赖](#211-环境依赖)中所有条件已满足才能部署，否则容易出现各种不可控问题。

YMIR-GUI项目包在DockerHub上，安装部署YMIR步骤如下：

1. 登录Git地址：[https://github.com/IndustryEssentials/ymir](https://github.com/IndustryEssentials/ymir)

将部署项目YMIR下拉到本地服务器，克隆仓库地址命令：
`git clone git@github.com:IndustryEssentials/ymir.git`

2. 如无可用显卡，用户需要安装CPU模式，请修改为CPU启动模式，修改.env文件将SERVER_RUNTIME参数修改为runc：

`# nvidia for gpu, runc for cpu.`

`SERVER_RUNTIME=runc`

3. 执行启动命令：`bash ymir.sh start`，建议不要使用```sudo```命令，否则可能会造成权限不足。

*  服务启动时会询问用户是否愿意发送使用报告到YMIR开发团队，不输入默认为愿意。
*  当询问用户是否需要启动label free标注平台时，如果用户需要启动，则需要前往.env配置文件中将ip和port信息改为用户当前所部署的标注工具地址及端口号。

```
# Note format: LABEL_TOOL_HOST_IP=http(s)://(ip)
LABEL_TOOL_HOST_IP=set_your_label_tool_HOST_IP
LABEL_TOOL_HOST_PORT=set_your_label_tool_HOST_PORT

```

修改完成后再执行启动命令：`bash ymir.sh start`。

4. 服务启动成功后，默认配置端口为12001，可以直接访问 [http://localhost:12001/](http://localhost:12001/)  显示登录界面即安装成功。如果需要**停止服务**，运行命令为：`bash ymir.sh stop`

## 2.3. 安装配置LabelStudio （可选）

label studio为YMIR外接的标注系统，选择安装可以完成数据标注的操作流程。

1. 在上一节的YMIR目录下，修改.env文件，配置label studio端口：

```
LABEL_TOOL=label_studio
# Note format: LABEL_TOOL_HOST_IP=http(s)://(ip)
LABEL_TOOL_HOST_IP=set_your_label_tool_HOST_IP
LABEL_TOOL_HOST_PORT=set_your_label_tool_HOST_PORT

```

2. 配置好标注工具（LABEL_TOOL）、IP（LABEL_TOOL_HOST_IP）、端口（LABEL_TOOL_HOST_PORT）后启动安装label studio命令如下：

`docker-compose -f docker-compose.label_studio.yml up -d`

3. 完成后查看label studio状态命令如下：

`docker-compose -f docker-compose.label_studio.yml ps`（默认端口为12007）

可以登录默认地址 [http://localhost:12007/](http://localhost:12007/) 显示登录界面即安装成功。

4. 配置label studio授权token

注册登录label studio后，在页面右上角个人信息图标，选择"Account & Settings"获取Token值并复制，粘贴到YMIR项目的.env配置文件对应的位置（LABEL_STUDIO_TOKEN）。实例如下：

```
LABEL_TOOL_TOKEN="Token token_value"
```

配置好Token值（LABEL_STUDIO_TOKEN）后重启YMIR即可。

5. 停止label studio服务命令如下：

`docker-compose -f docker-compose.label_studio.yml down`

# 3. GUI使用-典型模型生产流程

本次使用一次模型迭代的完整流程来说明YMIR平台的操作过程。

![YMIR-GUI process](docs/images/YMIR-GUI-process.jpeg)

数据和标签是深度学习模型训练的必要条件，模型的训练需要大量带标签的数据。然而在实际情况下，现实中存在的是大量没有标签的数据，如果全部由标注人员手工打上标签，人力和时间成本过高。

因此，YMIR平台通过主动学习的方法，首先通过本地导入或者少量数据来训练出一个初始模型，使用该初始模型，从海量数据中挖掘出对模型能力提高最有利的数据。挖掘完成后，仅针对这部分数据进行标注，对原本的训练数据集进行高效扩充。

使用更新后的数据集再次训练模型，以此来提高模型能力。相比于对全部数据标注后再训练，YMIR平台提供的方法更高效，减少了对低质量数据的标注成本。通过挖掘，标注，训练的循环，扩充高质量数据，提升模型能力。

## 3.1. 标签管理

当用户需要导入的数据集带有标注文件时，请确保标注类型属于系统已有的标签列表，否则需要用户前往标签管理界面新增自定义标签，以便导入数据。如下图所示：

![标签管理](docs/images/%E6%96%B0%E5%A2%9E%E6%A0%87%E7%AD%BE.jpg)

本次我们在标签列表中添加标签helmet_head、no_helmet_head，其中标签的主名与别名表示同一类标签，当某些数据集的标注包含别名时，会在导入时合并变更为主名。如，标签列表中包含标签bike（别名bicycle），导入某数据集A（仅包含标签bicycle），则导入后在数据集详情显示标注为bike。

## 3.2. 项目管理

用户根据自己的训练目标(helmet_head，no_helmet_head)创建项目，并设置目标的mAP值、迭代轮次等目标信息。如下图所示：

## 3.2.1 迭代数据准备

用户准备好用于数据挖掘的挖掘集（可以不需要包含标注文件），以及带有训练目标的数据集（训练集，测试集），用于训练初始模型。针对本身带有标注文件的数据集，在导入之前，需要保证数据集的格式符合格式要求：

*  数据集为.zip格式，其中包含两个文件夹，需分别命名为images和annotations；
*  images文件夹存放数据的图片信息，图像格式限为jpg、jpeg、png；
*  annotations文件夹存放数据的标注信息，标注文件格式为pascal voc（当无标注文件时，该文件夹为空）；

数据集导入支持四种形式：公共数据集导入、网络导入、本地导入和路径导入,如下图所示：

![数据导入引导](docs/images//%E5%AF%BC%E5%85%A51.jpg)

(1) 公共数据集复制：导入公共用户内置的数据集，该数据集存储在公共用户上，以复制的形式导入到当前的操作用户上。如下图所示：

![公共数据集导入1](docs/images/%E5%85%AC%E5%85%B1%E6%95%B0%E6%8D%AE%E9%9B%86%E5%AF%BC%E5%85%A51.jpeg)

![公共数据集导入2](docs/images/%E5%85%AC%E5%85%B1%E6%95%B0%E6%8D%AE%E9%9B%86%E5%AF%BC%E5%85%A52.jpeg)

选择数据集，可根据需求选择是否要同步导入公共数据集包含的标签，点击【确定】即可开始复制。

(2) 网络导入：输入数据集对应的url路径，如下图所示：

![网络导入](docs/images/%E7%BD%91%E7%BB%9C%E5%AF%BC%E5%85%A5.jpeg)

(3) 本地导入：上传本地数据集的压缩包，压缩包大小建议不超过200M。

用户可以下载示例**Sample.zip**作为参考，如下图所示：

![本地导入](docs/images/%E6%9C%AC%E5%9C%B0%E5%AF%BC%E5%85%A5.jpeg)

(4)路径导入：输入数据集在服务器中的绝对路径。如下图所示：

![路径导入](docs/images/%E8%B7%AF%E5%BE%84%E5%AF%BC%E5%85%A5.jpeg)

1.通过在网络中下载开源数据集VOC2012([点击下载VOC2012](http://host.robots.ox.ac.uk/pascal/VOC/voc2012/VOCtrainval_11-May-2012.tar))，解压缩后按要求修改文件夹名称，再分别压缩为符合导入要求的zip包；

2.把VOC2012放到ymir-workplace/importing_pic下面；

3.选择路径导入，填上路径地址/data/sharing/voc2012_train。

如下图所示：

![voc训练集测试集](docs/images/voc%E8%AE%AD%E7%BB%83%E9%9B%86%E6%B5%8B%E8%AF%95%E9%9B%86.jpeg)

完成初始数据集的导入后，点击【迭代数据准备】，完成对应的数据集和挖掘策略设置。其中训练集已设置为创建项目时默认的系统训练集，不可变更。

![迭代数据准备](docs/images/%E8%BF%AD%E4%BB%A3%E6%95%B0%E6%8D%AE%E5%87%86%E5%A4%87.jpg)

## 3.2.2 初始模型准备

用户准备用于初始迭代的模型，可以通过本地导入和模型训练两种方式，本地导入需要保证模型的格式符合要求：

*  仅支持YMIR系统产生的模型；
*  上传文件应小于1024MB；
*  上传的模型文件检测目标应该与项目目标保持一致；

模型训练可以点击数据集列表界面的【训练】操作按钮，跳转至创建模型训练界面，如下图所示：

![训练1](docs/images/training1.jpg)

选择训练集（train1 V1），选择测试集（val V1），选择训练目标（helmet_head，no_helmet_head），选择前置预训练模型（非必填）、训练镜像、训练类型、算法框架、骨干网络结构、GPU个数以及配置训练参数（训练参数提供默认值，默认参数中key值不可修改，value值可修改，如需添加参数可以自行添加）。如下图所示，训练初始模型：

![训练2](docs/images/training2.jpg)

训练成功后，跳转到模型列表界面，可以查看到相应的训练进度和信息，完成后可查看模型的效果（mAP值）。

完成初始模型的导入或者训练后，点击【迭代模型准备】，选择初始模型，完成设置。迭代数据和模型均准备完成后，开启迭代。

## 模型迭代（通过迭代提升模型精度）

开启迭代后，YMIR提供标准化的模型迭代流程，并且会在每一步操作中帮助用户默认填入上一次的操作结果，普通用户按照既定步骤操作，即可完成完整的模型迭代流程。

## 3.2.3. 挖掘数据准备

由于在模型训练的初期，很难一次性找到大量的优质数据来进行训练，导致初始模型的精度不够。因此，寻找有利于模型训练的数据一直是人工智能算法开发的一大问题，在这个过程中，往往会对算法工程师的人力资源产生很大消耗。在此基础上，YMIR提供成熟的挖掘算法，支持百万级数据挖掘，在海量数据中快速寻找到对模型优化最有利的数据，降低标注成本，减少迭代时间，保障模型的持续迭代。

【挖掘数据准备】为用户提供待挖掘的数据，这里的原数据集默认为项目设置的挖掘集。操作流程如下图示：

![挖掘数据准备1](docs/images/%E5%87%86%E5%A4%87%E6%8C%96%E6%8E%98%E6%95%B0%E6%8D%AE.jpg)
![挖掘数据准备2](docs/images/%E5%87%86%E5%A4%87%E6%8C%96%E6%8E%98%E6%95%B0%E6%8D%AE2.jpg)

操作完成后点击【下一步】，开启【数据挖掘】流程。

## 3.2.4. 数据挖掘

接下来使用在迭代模型准备时选择的模型，对待挖掘的数据集进行数据挖掘。点击【数据挖掘】按钮，跳转至数据挖掘界面，如下图所示：

![挖掘1](docs/images/%E6%8C%96%E6%8E%981.jpg)
![挖掘2](docs/images/%E6%8C%96%E6%8E%982.jpg)

默认原数据集为上次挖掘数据准备的结果数据集，默认模型为迭代准备中设置的初始模型，输入筛选测试TOPK=500（前500张成功挖掘的图像）和设定自定义参数（自定义参数提供默认值，默认参数中key值不可修改，value值可修改，如需添加参数可以自行添加）。

创建成功后，跳转到数据集管理界面，可以查看到相应的挖掘进度和信息，挖掘完成后可查挖掘出的结果数据集。

## 3.2.5. 数据标注

如果上一步中挖掘出来的数据没有标签，则需要进行标注。点击【数据标注】按钮，跳转至数据标注界面，如下图所示：

![标注1](docs/images/%E6%A0%87%E6%B3%A81.jpg)

默认原数据集为上次挖掘得到的结果数据集，输入标注人员邮箱（需要提前去标注系统注册，点击最下方“注册标注平台账号”即可跳转到Label Studio标注平台注册标注账号），选择标注目标（helmet_head， no_helmet_head），如需自行到标注平台查看，请勾选“到标注平台查看”，填写自己的标注平台账号（同样需要提前注册），如对标注有更详细的要求，则可以上传标注说明文档供标注人员参考。点击创建，如下图所示：

![标注2](docs/images/%E6%A0%87%E6%B3%A82.jpg)

创建成功后，跳转到数据集管理界面，可以查看到相应的标注进度和信息，标注完成后，系统自动获取完成结果，生成带有新标注的数据集。

## 3.2.6. 更新训练集

标注完成后，将已标注好的数据集合并到训练集中，并将合并结果生成为一个新的训练集版本。如下图所示：

![更新1](docs/images/%E6%9B%B4%E6%96%B01.jpg)
![更新2](docs/images/%E6%9B%B4%E6%96%B02.jpg)

## 3.2.7. 合并训练

![流程-中文](docs/images/%E6%B5%81%E7%A8%8B-%E4%B8%AD%E6%96%87.jpeg)

合并完成后，再次进行模型训练，生成新的模型版本，如下图所示：

![合并训练1](docs/images/%E5%90%88%E5%B9%B6%E8%AE%AD%E7%BB%831.jpg)
![合并训练2](docs/images/%E5%90%88%E5%B9%B6%E8%AE%AD%E7%BB%832.jpg)

用户可对达到预期的模型进行下载。或继续进入下一轮迭代，进一步优化模型。

## 3.2.8. 模型验证

每次训练模型后，可以对模型结果进行验证，即通过可视化的方式查看模型在真实图片中的表现。在【模型管理】页面，点击对应模型的【验证】按钮，跳转到【模型验证】页面，如下图所示：

![模型验证1](docs/images/%E6%A8%A1%E5%9E%8B%E9%AA%8C%E8%AF%811.jpeg)

![模型验证2](docs/images/%E6%A8%A1%E5%9E%8B%E9%AA%8C%E8%AF%812.jpeg)

选择验证镜像，调整参数，点击【上传图片】按钮，选择本地图片上传，点击【模型验证】，显示结果如下：

![模型验证3](docs/images/%E6%A8%A1%E5%9E%8B%E9%AA%8C%E8%AF%813.jpeg)

## 3.2.9. 模型下载

在【模型列表】页面，点击【下载】按钮，下载文件格式为tar包，包含模型的网络结构、为网络权重、超参数配置文件、训练的环境参数及结果，如下图所示：

![模型下载](docs/images/%E6%A8%A1%E5%9E%8B%E4%B8%8B%E8%BD%BD.jpeg)

# 4. 进阶版：Ymir-CMD line使用指南

本章节为YMIR-CMD line的使用说明，如需安装和使用GUI，请参考[GUI安装说明](#2-安装)。

## 4.1 安装

### 方式一：通过pip安装

```
# Requires >= Python3.8.10
$ pip install ymir-cmd
$ mir --vesion
```

### 方式二：通过源码安装
```
$ git clone --recursive git@github.com:IndustryEssentials/ymir.git
$ cd ymir/command
$ python setup.py clean --all install
$ mir --version
```

## 4.2 典型模型生产流程

![流程-中文](docs/images/%E6%B5%81%E7%A8%8B-%E4%B8%AD%E6%96%87.jpeg)

上图所示的是模型训练的一个典型流程：用户准备好外部数据，导入本系统，对数据进行适当筛选，开始训练得到一个（可能是粗精度的）模型，并依据这个模型，在一个待挖掘数据集中挑选适合进一步训练的图片，将这些图片进行标注，标注完成的结果与原训练集合并，用合并以后的结果再次执行训练过程，得到效果更好的模型。
在这一节里，我们需要使用命令行实现上图所示的流程，其他流程也可以类似实现。
以下所有命令前面都加入了$（它也是普通用户下Linux提示符），在实际向控制台输入命令时，$不需要一起输入。

### 4.2.1 准备外部数据

本系统对外部数据有以下要求：

1.标注为[VOC格式](https://towardsdatascience.com/coco-data-format-for-object-detection-a4c5eaf518c5)；

2. 所有图片（本系统中统称为assets或medias）的路径需要统一写入index.tsv文件，同时，所有标注文件都需要位于同一个目录中；

3. 运行命令行的用户需要index.tsv，所有图片文件和所有标注文件的读权限。

我们以 pascal 2017 test 数据集为例，描述一下外部数据集的准备过程。
在官网下载数据集VOC2012test.tar，使用以下命令解压：

```
$ tar -xvf VOC2012test.tar
```
解压以后，可以得到以下目录结构（假设VOCdevkit位于/data目录下）：

```
/data/VOCdevkit
`-- VOC2012
    |-- Annotations
    |-- ImageSets
    |   |-- Action
    |   |-- Layout
    |   |-- Main
    |   `-- Segmentation
    `-- JPEGImages
```

其中，所有标注都位于annotations目录，而所有图片都位于JPEGImages目录。
使用下述命令生成index.tsv文件：

```
$ find /data/VOCdevkit/VOC2012/JPEGImages -type f > index.tsv
```

可以看到index.tsv中有如下内容：

```
/data/VOCdevkit/VOC2012/JPEGImages/2009_001200.jpg
/data/VOCdevkit/VOC2012/JPEGImages/2009_004006.jpg
/data/VOCdevkit/VOC2012/JPEGImages/2008_006022.jpg
/data/VOCdevkit/VOC2012/JPEGImages/2008_006931.jpg
/data/VOCdevkit/VOC2012/JPEGImages/2009_003016.jpg
...
```

这个index.tsv可用于下一步的数据导入。

另外，在Annotations文件夹中，每个标注都拥有和图片相同的主文件名。其中的<name>xxx</name>属性将被提取成为预定义关键字，被用于后面一步的数据筛选。

### 4.2.2 建立本地repo并导入数据

本系统的命令行采用和 git 类似的做法对用户的资源进行管理，用户建立自己的 mir  repository，并在此 mir repo 中完成接下来的所有任务。

想要建立自己的 mir repo，用户只需要：

```
$ mkdir ~/mir-demo-repo && cd ~/mir-demo-repo # 建立目录并进入
$ mir init # 将此目录初始化成一个mir repo
$ mkdir ~/ymir-assets ~/ymir-models # 建立资源和模型存储目录，所有的图像资源都会保存在此目录中，而在mir repo中只会保留对这些资源的引用
```

mir repo 中的标签通过标签文件进行统一管理，打开标签文件 `~/mir-demo-repo/labels.csv`，可以看到以下内容：

```
# type_id, preserved, main type name, alias...
```

在这个文件中，每一行代表一个类别标签，依次是标签 id（从 0 开始增长），留空，主标签名，一个或多个标签别名，例如，如果想要导入的数据集中含有 person, cat 和 tv 这几个标签，可以编辑此文件为：

```
0,,person
1,,cat
2,,tv
```

一个类别标签可以指定一个或多个别名，例如，如果指定 television 作为 tv 的别名，则 `labels.csv` 文件可更改为：

```
0,,person
1,,cat
2,,tv,television
```

可以使用vi，或其他的编辑工具对此文件进行编辑，用户可以添加类别的别名，也可以增加新的类别，但不建议更改或删除已经有的类别的主名和id。

`labels.csv` 文件可以通过建立软链接的方式，在多个 mir repo 之间共享。

用户需要事先准备三个数据集：

1. 训练集 dataset-training，带标注，用于初始模型的训练；

2. 验证集 dataset-val，带标注，用于训练过程中模型的验证；

3. 挖掘集 dataset-mining，这是一个比较大的待挖掘的数据集。

用户通过下述命令导入这三个数据集：

```
$ cd ~/mir-demo-repo
$ mir import --index-file /path/to/training-dataset-index.tsv \ # 数据集index.tsv路径
             --annotation-dir /path/to/training-dataset-annotation-dir \ # 标注路径
             --gen-dir ~/ymir-assets \ # 资源存储路径
             --dataset-name 'dataset-training' \ # 数据集名称
             --dst-rev 'dataset-training@import' # 结果分支及操作任务名称
$ mir checkout master
$ mir import --index-file /path/to/val-dataset-index.tsv \
             --annotation-dir /path/to/val-dataset-annotation-dir \
             --gen-dir ~/ymir-assets \
             --dataset-name 'dataset-val' \
             --dst-rev 'dataset-val@import'
$ mir checkout master
$ mir import --index-file /path/to/mining-dataset-index.tsv \
             --annotation-dir /path/to/mining-dataset-annotation-dir \
             --gen-dir ~/ymir-assets \
             --dataset-name 'dataset-mining' \
             --dst-rev 'dataset-mining@import'
```

任务全部执行成功以后，可以通过以下命令：

```
$ mir branch
```

查看当前 mir repo 的分支情况，现在用户应该可以看到此 repo 有四个分支：master, dataset-training, dataset-val, dataset-mining，并且当前 repo 位于分支dataset-mining上。

用户也可以通过以下命令查看任何一个分支的情况：

```
$ mir show --src-rev dataset-mining
```

系统会有以下输出：

```
person;cat;car;airplane

metadatas.mir: 200 assets, tr: 0, va: 0, te: 0, unknown: 200
annotations.mir: hid: import, 113 assets
tasks.mir: hid: import
```

第一行和第二行分别是预定义关键字和用户自定义关键字（在这个输出中，用户自定义关键字为空），后面几行分别是当前分支下的资源数量，标注数量以及任务情况。

### 4.2.3 合并及筛选
训练模型需要训练集和验证集，通过以下命令将 dataset-training 和 dataset-val 合成一个：

```
$ mir merge --src-revs tr:dataset-training@import;va:dataset-val@import \ # 待合并分支
            --dst-rev tr-va@merged \ # 结果分支及操作任务名称
            -s host # 策略：依据主体分支解决冲突
```

合并完成后，可以看到当前 repo 位于 tr-va 分支下，可以使用 mir show 命令查看合并以后的分支状态：

```
$ mir show --src-revs HEAD # HEAD指代当前分支，也可以用tr-va这个具体的分支名称代替
```

系统会有以下输出：

```
person;cat;car;airplane

metadatas.mir: 3510 assets, tr: 2000, va: 1510, te: 0, unknown: 0
annotations.mir: hid: merged, 1515 assets
tasks.mir: hid: merged
```

假设合并之前的 dataset-training 和 dataset-val 分别有2000和1510张图像，可以看到合并后的分支中有2000张图像作为训练集，1510张图像作为验证集。
假设我们只想训练识别人和猫的模型，我们首先从这个大数据集里面筛选出现人或猫的资源：

```
mir filter --src-revs tr-va@merged \
           --dst-rev tr-va@filtered \
           -p 'person;cat'
```

### 4.2.4 训练第一个模型
首先从 dockerhub 上拉取训练镜像和挖掘镜像：

```
docker pull industryessentials/executor-det-yolov4-training:release-0.1.2
docker pull industryessentials/executor-det-yolov4-mining:release-0.1.2
```

并使用以下命令开始训练过程：

```
mir train -w /tmp/ymir/training/train-0 \
          --media-location ~/ymir-assets \ # import时的资源存储路径
          --model-location ~/ymir-models \ # 训练完成后的模型存储路径
          --task-config-file ~/training-config.yaml \ # 训练参数配置文件，到训练镜像中获取
          --src-revs tr-va@filtered \
          --dst-rev training-0@trained \
          --executor industryessentials/executor-det-yolov4-training:release-0.1.2 # 训练镜像
```

模型训练完成后，系统会输出模型id，用户可以在~/ymir-models中看到本次训练好的模型打包文件。

### 4.2.5 挖掘

上述模型是基于一个小批量数据集训练得到的，通过挖掘，可以从一个大数据集中得到对于下一步训练模型最为有效的资源。
用户使用下述命令完成挖掘过程：

```
mir mining --src-revs dataset-mining@import \ # 导入的挖掘分支
           --dst-rev mining-0@mining \ # 挖掘的结果分支
           -w /tmp/ymir/mining/mining-0 \ # 本次任务的临时工作目录
           --topk 200 \ # 挖掘结果的图片数量
           --model-location ~/ymir-models \
           --media-location ~/ymir-assets \
           --model-hash <hash> \ # 上一步训练出来的模型id
           --cache /tmp/ymir/cache \ # 资源缓存
           --task-config-file ~/mining-config.yaml \ # 挖掘参数配置文件，到挖掘镜像中获取
           --executor industryessentials/executor-det-yolov4-mining:release-0.1.2
```

### 4.2.6 标注
现在，系统已经挖掘出了对于模型训练最有效的200张图像，这些图像被保存在分支mining中，接下来的任务是将这些资源导出，送给标注人员进行标注。
用户可以通过下述命令完成导出过程：

```
mir export --asset-dir /tmp/ymir/export/export-0/assets \ # 资源导出目录
           --annotation-dir /tmp/ymir/export/export-0/annotations \ # 导出标注目录
           --media-location ~/ymir-assets \ # 资源存储目录
           --src-revs mining-0@mining \
           --format none # 不导出标注
find /tmp/ymir/export/export-0/assets > /tmp/ymir/export/export-0/index.tsv
```

导出完成后，可以在/tmp/ymir/export/export-0/assets位置看到导出的图片，用户可以将这些图片送去标注，标注需要按VOC格式保存，假设保存路径仍然为/tmp/ymir/export/export-0/annotations。
标注完成后，用户可以使用与[4.2.2](#422-建立本地repo并导入数据)中的导入命令类似的方式导入数据：

```
$ mir import --index-file /tmp/ymir/export/export-0/index.tsv
             --annotation-dir /tmp/ymir/export/export-0/annotations \ # 标注路径
             --gen-dir ~/ymir-assets \ # 资源存储路径
             --dataset-name 'dataset-mining' \ # 数据集名称
             --dst-rev 'labeled-0@import' # 结果分支及操作任务名称
```

### 4.2.7 合并
现在的工作空间的分支labeled-0中已经包含了挖掘出来的200张新的训练图像，可以通过前述的merge将其和原来的训练集合并在一起：

```
$ mir merge --src-revs tr-va@filtered;tr:labeled-0@import \ # 待合并分支
            --dst-rev tr-va-1@merged \ # 结果分支及操作任务名称
            -s host # 策略：依据主体分支解决冲突
```

### 4.2.8 训练第二个模型
现在在分支tr-va-1上，已经包含了前一次训练所用的训练集和验证集，也包含了后来通过数据挖掘得出的新的200张训练集加人工标注，可以通过以下命令在此集合上训练一个新的模型出来：

```
mir train -w /tmp/ymir/training/train-1 \ # 每个不同的训练和挖掘任务都用不同的工作目录
          --media-location ~/ymir-assets \
          --model-location ~/ymir-models \
          --task-config-file ~/training-config.yaml \ # 训练参数配置文件，到训练镜像中获取
          --src-revs tr-va-1@merged \ # 使用合成以后的分支
          --dst-rev training-1@trained \
          --executor industryessentials/executor-det-yolov4-training:release-0.1.2
```

## 4.3. 命令参数手册

Ymir-command-api.211028

**通用参数格式与定义**

| 参数名         | 变量名      | 类型与格式       | 定义                                                       |
|----------------|----------|-------------|----------------------------------------------------------|
| --root / -r | mir_root | str         | 需要初始化的路径，如果没有指定，则为当前路径                                   |
| --dst-rev   | dst_rev  | str         | 1. 目标rev，仅限单个                                            |
|             |          | rev@tid     | 2. 所有修改将保存在此rev的tid上                                     |
|             |          |             | 3. 如果是一个新的rev则先checkout到第一个src-revs再创建                   |
|             |          |             | 4. tid必须，rev必须                                           |
| --src-revs  | src_revs | str         | 1. 数据来源rev，多个用分号隔开（仅merge支持，其他cmd仅支持单个）                  |
|             |          | typ:rev@bid | 2. typ可选，只在merge有效果，支持前置用途标识符（tr/va/te），为空，则表示使用原rev中的设置 |
|             |          |             | 3. bid可选，若为空则读head task id                               |
|             |          |             | 4. rev不能为空                                               |
|             |          |             | 注意：当出现多个revs，例如a1@b1;a2@b2，需要用引号将其括起来，因为分号是Linux命令分隔符。   |

**mir init**

| DESCRIPTION                                             |          |           |
| ------------------------------------------------------- | -------- | --------- |
| mir init [--root <mir_root>]                            |          |           |
| 将当前路径，或者-root指定的路径初始化为一个mir root。   |          |           |
| ARGS（ARGS名称、run_with_args中的参数名称、类型、说明） |          |           |
| --root / -r                                             | mir_root | str，可选 |
| RETURNS                                                 |          |           |
| 正常初始化：返回0                                       |          |           |
| 异常：其他error code                                    |          |           |

**mir branch**

| DESCRIPTION                    |          |           |
| ------------------------------ | -------- | --------- |
| mir branch [--root <mir_root>] |          |           |
| 列出当前本地或远程的所有分支   |          |           |
| ARGS                           |          |           |
| --root / -r                    | mir_root | str，可选 |
| RETURNS                        |          |           |

# 5.  获取代码

## 5.1  YMIR repos

YMIR项目由三部分组成:

1. 后端 [https://github.com/IndustryEssentials/ymir-backend](https://github.com/IndustryEssentials/ymir/tree/master/ymir/backend)，负责任务分发与管理

2. 前端 [https://github.com/IndustryEssentials/ymir-web](https://github.com/IndustryEssentials/ymir/tree/master/ymir/web)，交互界面

3. 命令行 [https://github.com/IndustryEssentials/ymir-cmd](https://github.com/IndustryEssentials/ymir/tree/master/ymir/command)，CLI界面，管理底层标注与图像数据

## 5.2  代码贡献

YMIR repo中的任何代码都应遵循编码标准，并将在CI测试中进行检查。

- 功能性代码需要进行单元测试。

- 在提交前使用 [flake8](https://flake8.pycqa.org/en/latest/) 或 [black](https://github.com/ambv/black) 来格式化代码。 这两者均遵循 [PEP8](https://www.python.org/dev/peps/pep-0008) 和 [Google Python Style](https://google.github.io/styleguide/pyguide.html) 风格指南。

- [mypy](http://mypy-lang.org/) - Python必须经过静态类型检查。

也可以查看 [MSFT编码风格](https://github.com/Microsoft/Recommenders/wiki/Coding-Guidelines) 来获取更多的建议。

## 5.3 关于训练，推理与挖掘镜像

[查看这篇文档](docs/ymir-cmd-container.md)获取更多细节。

# 6. 设计理念

## 6.1. Life of a dataset

### 6.1.1 数据集介绍

数据集由Metadata（元数据）与媒体文件组成，元数据具有下述特征:

*  它拥有唯一ID，系统有一个初始的默认Metadata状态，为空；
*  它拥有一个资源列表，列表中每个元素都指向一个实际的资源，Metadata不实际保存资源，只维护此资源列表；
*  它拥有若干keywords，用户可以通过这些keywords搜索到某个特定的Metadata状态；
*  用户可以为某个metadata新开分支，并在新开的分支上进行操作，在新分支上的操作不影响原metadata的状态，且原metadata仍可以被用户追溯，这些操作包括但不限于：

    (1)添加资源
    (2)添加或修改标注
    (3)添加或修改关键词
    (4)过滤资源
    (5)合并两个不同的metadatas

*  用户可以在不同metadata之间自由跳转；
*  用户可以查询metadata的历史；
*  用户可以将metadata打上自己的tag，便于通过tag精确查找；
*  用户也可以向metadata添加keywords，便于keywords模糊搜索；
*  用户可以通过某种方式读取一个metadata中所包含的资源，并将这些资源用于浏览、训练等。

从以上描述可以看出，对于metadata的管理，类似于VCS（版本管理系统），用户可以有下面几种完全不同的使用方式与场景：

**场景一**: 直接从最开始的metadata，进行筛选过程，选出并使用符合要求的数据，如下图所示：

![场景一](docs/images/%E5%9C%BA%E6%99%AF%E4%B8%80.jpeg)

每当用户需要开始一项新任务时：
* 用户从当前的主分支内签出一个新的feature分支，得到处于feature#1状态的metadata；
* 用户在此新分支的metadata上进行数据筛选和其他任务，得到处于feature#2状态的metadata；
* 当确认这个metadata适合自己的训练任务，则可以使用这个数据开始训练；
* 此时，其他用户对master分支的metadata进行更改，也不会影响到用户正在使用的训练数据。

**场景二**：通过tag或keywords搜索到某个metadata，并开始筛选过程，直到得出符合要求的数据，然后使用该数据，如下图所示：

![场景二](docs/images/%E5%9C%BA%E6%99%AF%E4%BA%8C.jpeg)

此时，每当用户需要开展一项新任务时：
* 通过keywords和tag等方式，搜索到一个基本符合自己要求的metadata
* 在此基础上，签出一个新分支
* 在新分支上继续进行数据筛选或清洗，得到真正符合要求的数据
* 利用此数据进行训练

**场景三**：增量合并。假设用户已经使用某个metadata完成了模型的训练任务，此时资源库与主分支的metadata有更新，用户希望将这一部分更新合并到当前使用的metadata中：

![场景三](docs/images/%E5%9C%BA%E6%99%AF%E4%B8%89.jpeg)

假设用户现在在feature#2，用户需要进行如下操作：
* 切回主分支master
* 对master#2 - master#1这个增量部分，重复之前做过的任务，得到feature#2+
* 切回feature#2，合并feature#2+，得到feature#3

### 6.1.2 分支与数据集的管理

本节的论述基于以下假设：
* 用户数据以数据集为单位分批导入
* 每个数据集是一个独立分支；
* 对每个数据集的更改及维护都在本分支上进行；
* master分支始终为空。
这种管理方式如下图所示：

![分支及数据集管理](docs/images/%E5%88%86%E6%94%AF%E5%8F%8A%E6%95%B0%E6%8D%AE%E9%9B%86%E7%AE%A1%E7%90%86.jpeg)

我们使用Git中代码版本控制的概念来管理我们的数据和模型。我们使用分支的概念创建新项目，以便同一组映像上的不同任务可以并行运行。数据集的增加、检索、更新和删除以及基本操作都创建提交到分支。从逻辑上讲，每次提交都存储数据集或新模型的更新版本，以及导致此更改的操作的元数据。最后，只有数据更改被合并到主分支，这在概念上，聚合了该平台上许多项目注释的所有数据。

# 7.MISC

## 7.1 常见问题

*  为什么上传本地数据集的压缩包失败？

无论是否有标签，必须创建images文件夹和annotations文件夹。图像放入images文件夹下，格式限为jpg、jpeg、png。标注文件放入annotations文件夹下，格式为pascal（无标注文件，annotations文件夹为空）。将images，annotations放入同一文件夹下，并压缩为.zip压缩包（非.rar压缩格式）。

*  应该如何取得训练和挖掘的配置文件？

默认配置文件模板需要在镜像中提取。

训练镜像 `industryessentials/executor-det-yolov4-training:release-0.1.2` 的配置文件模板位于：`/img-man/training-template.yaml`

挖掘与推理镜像 `industryessentials/executor-det-yolov4-mining:release-0.1.2` 的配置文件模板位于：`/img-man/mining-template.yaml`（挖掘） 以及 `/img-man/infer-template.yaml`（推理）

*  如何在系统外部使用训练出来的模型？

成功完成训练后，系统会输出模型的 id，用户可以根据这个 id 到 `--model-location` 位置找到对应的文件，它事实上是一个 tar 文件，可以直接使用 tar 命令解压，得到 params 和 json 格式的 mxnet 模型文件。

*  在windows系统遇到部署、调试、运行问题如何解决？

尚未在Windows服务器完备测试，暂时无法提供服务支持。

## 7.2 License

YMIR开源项目符合Apache 2.0证书许可。查看 [LICENSE](https://github.com/IndustryEssentials/ymir/blob/master/LICENSE) file for details.

## 7.3 联系我们

当您有其他问题时，请联系我们： contact.viesc@gmail.com

或者加入我们的[Slack community](https://join.slack.com/t/ymir-users/shared_invite/zt-ywephyib-ccghwp8vrd58d3u6zwtG3Q)，我们将会实时解答您的问题。

<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/All%20Contributors-8-brightgreen)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

<a href="https://github.com/phoenix-xhuang"><img src="https://avatars.githubusercontent.com/u/89957974?v=4" class="avatar-user" width="18px;"/></a> 
<a href="https://github.com/IJtLJZ8Rm4Yr"><img src="https://avatars.githubusercontent.com/u/90443055?v=4" class="avatar-user" width="18px;"/></a> 
<a href="https://github.com/elliotmessi"><img src="https://avatars.githubusercontent.com/u/90443217?v=4" class="avatar-user" width="18px;"/></a> 
<a href="https://github.com/Aryalfrat"><img src="https://avatars.githubusercontent.com/u/90443348?v=4" class="avatar-user" width="18px;"/></a> 
<a href="https://github.com/fenrir-z"><img src="https://avatars.githubusercontent.com/u/90444968?v=4" class="avatar-user" width="18px;"/></a> 
<a href="https://github.com/under-chaos"><img src="https://avatars.githubusercontent.com/u/90446262?v=4" class="avatar-user" width="18px;"/></a> 
<a href="https://github.com/Zhang-SJ930104"><img src="https://avatars.githubusercontent.com/u/91466580?v=4" class="avatar-user" width="18px;"/></a> 
<a href="https://github.com/LuciferZap"><img src="https://avatars.githubusercontent.com/u/92283801?v=4" class="avatar-user" width="18px;"/></a> 

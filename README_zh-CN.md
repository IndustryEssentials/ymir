<div align="center">
  <img src="https://github.com/IndustryEssentials/ymir-images/blob/main/doc_images/YMIR.jpg" width="500"/>
  <div>&nbsp;</div>
  <div align="center">
    <b><font size="5">VIESC 官网</font></b>
    <sup>
      <a href="https://www.viesc.com/">
        <i><font size="4">VISIT</font></i>
      </a>
    </sup>
    &nbsp;&nbsp;&nbsp;&nbsp;
    <b><font size="5">试用申请</font></b>
    <sup>
      <a href="https://github.com/IndustryEssentials/ymir#12-apply-for-trial">
        <i><font size="4">TRY IT OUT</font></i>
      </a>
    </sup>
    &nbsp;&nbsp;&nbsp;&nbsp;
    <b><font size="5">SLACK社区</font></b>
    <sup>
      <a href="https://join.slack.com/t/ymir-users/shared_invite/zt-ywephyib-ccghwp8vrd58d3u6zwtG3Q">
        <i><font size="4">WELCOME</font></i>
      </a>
    </sup>
  </div>
  <div>&nbsp;</div>
<div align="center">
  <img src="https://github.com/IndustryEssentials/ymir-images/blob/main/doc_images/for_management.png" width="180"/>
  <img src="https://github.com/IndustryEssentials/ymir-images/blob/main/doc_images/for_mining.png" width="200"/>
  <img src="https://github.com/IndustryEssentials/ymir-images/blob/main/doc_images/for_labeling.png" width="200"/>
  <img src="https://github.com/IndustryEssentials/ymir-images/blob/main/doc_images/for_training.png" width="200"/>
  <div>&nbsp;</div>

[📘使用说明](https://github.com/IndustryEssentials/ymir/wiki/%E6%93%8D%E4%BD%9C%E8%AF%B4%E6%98%8E) |
[🛠️安装教程](README_zh-CN.md#2-%E5%AE%89%E8%A3%85) |
[🚀进行中的项目](https://github.com/IndustryEssentials/ymir/projects) |
[🤔报告问题](https://github.com/IndustryEssentials/ymir/issues/new/choose) |
[📰开源协议](https://github.com/IndustryEssentials/ymir/blob/master/LICENSE)

</div>&nbsp;</div>

<div align="center">
  <img src="https://github.com/IndustryEssentials/ymir-images/blob/main/doc_images/wechat_code.jpg" width="180"/>
  <img src="https://github.com/IndustryEssentials/ymir-images/blob/main/doc_images/contact.jpg" width="400"/>

  📫 使用问题反馈：contact.viesc@gmail.com / 服务器级设备专业咨询：tensor.station@gmail.com

<div>&nbsp;</div>&nbsp;</div>

[English](README.md) | 简体中文

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

# 更新内容

2.0.0版本更新时间为11/08/2022

YMIR平台
- 新增模型性能诊断模块；
- 新增对模型推理结果进行可视化评估的功能；
- 新增公共算法库，内置多种高精度算法；
- 新增一键部署功能，支持将算法部署到认证设备上；
- 新增操作说明文档；
- 优化代码结构。

Docker
- 支持 [yolov5](https://github.com/ultralytics/yolov5)
- 支持 [mmdetection](https://github.com/open-mmlab/mmdetection)
- 支持 [yolov7](https://github.com/wongkinyiu/yolov7)
- 支持 [detectron2](https://github.com/facebookresearch/detectron2)
- 支持 [nanodet](https://github.com/RangiLyu/nanodet)
- 支持 [vidt: An Extendable, Efficient and Effective Transformer-based Object Detector](https://github.com/naver-ai/vidt)
- 支持 [ymir镜像测试工具库](https://github.com/modelai/ymir-executor-verifier)
- 支持 [demo 示例镜像制作文档](https://github.com/modelai/ymir-executor-fork/tree/ymir-dev/det-demo-tmi)
- 支持 [ymir镜像开发扩展库](https://github.com/modelai/ymir-executor-sdk)

查看更多内容 [ymir-executor-fork](https://github.com/modelai/ymir-executor-fork)

在公共镜像内
- 更新yolov5训练镜像：youdaoyzbx/ymir-executor:ymir2.0.0-yolov5-cu111-tmi
- 更新mmdetection训练镜像：youdaoyzbx/ymir-executor:ymir2.0.0-mmdet-cu111-tmi
- 更新支持rv1126芯片部署的yolov5训练镜像：youdaoyzbx/ymir-executor:ymir2.0.0-yolov5-cu111-tmid

更多代码更新请查看 [ymir-dev](https://github.com/modelai/ymir-executor-fork/tree/ymir-dev)。

# 硬件支持 （可选）

YYMIR支持将训练好的模型直接部署到认证设备，需要查看更多硬件参数，请查看[详情](https://i-item.jd.com/10065116628109.html)。

<div align="center">
  <img src="https://github.com/IndustryEssentials/ymir-images/blob/main/doc_images/certified_device.PNG" width="500"/>
  <div>&nbsp;</div>&nbsp;</div>

## 简介

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**目录**

- [文章引用](#文章引用)
- [更新内容](#更新内容)
- [硬件支持 （可选）](#%E7%A1%AC%E4%BB%B6%E6%94%AF%E6%8C%81-%E5%8F%AF%E9%80%89)
- [1. AI SUITE-YMIR介绍](#1--ai-suite-ymir%E4%BB%8B%E7%BB%8D)
  - [1.1.	主要功能](#11-主要功能)
  - [1.2.	申请试用](#12-申请试用)
- [2. 安装](#2-%E5%AE%89%E8%A3%85)
  - [2.1. 环境依赖](#21-%E7%8E%AF%E5%A2%83%E4%BE%9D%E8%B5%96)
  - [2.2. 安装 YMIR-GUI](#22-%E5%AE%89%E8%A3%85-ymir-gui)
  - [2.3. 安装配置LabelStudio （可选）](#23-%E5%AE%89%E8%A3%85%E9%85%8D%E7%BD%AElabelstudio-%E5%8F%AF%E9%80%89)
- [3. GUI使用-典型模型生产流程](#3-gui%E4%BD%BF%E7%94%A8-%E5%85%B8%E5%9E%8B%E6%A8%A1%E5%9E%8B%E7%94%9F%E4%BA%A7%E6%B5%81%E7%A8%8B)
- [4. 进阶版：Ymir-CMD line使用指南](#4-%E8%BF%9B%E9%98%B6%E7%89%88ymir-cmd-line%E4%BD%BF%E7%94%A8%E6%8C%87%E5%8D%97)
  - [4.1 安装](#41-%E5%AE%89%E8%A3%85)
    - [方式一：通过pip安装](#%E6%96%B9%E5%BC%8F%E4%B8%80%E9%80%9A%E8%BF%87pip%E5%AE%89%E8%A3%85)
    - [方式二：通过源码安装](#%E6%96%B9%E5%BC%8F%E4%BA%8C%E9%80%9A%E8%BF%87%E6%BA%90%E7%A0%81%E5%AE%89%E8%A3%85)
  - [4.2 典型模型生产流程](#42-%E5%85%B8%E5%9E%8B%E6%A8%A1%E5%9E%8B%E7%94%9F%E4%BA%A7%E6%B5%81%E7%A8%8B)
- [5.  获取代码](#5--%E8%8E%B7%E5%8F%96%E4%BB%A3%E7%A0%81)
  - [5.1 代码贡献](#51--%E4%BB%A3%E7%A0%81%E8%B4%A1%E7%8C%AE)
  - [5.2 关于训练，推理与挖掘镜像](#52-%E5%85%B3%E4%BA%8E%E8%AE%AD%E7%BB%83%E6%8E%A8%E7%90%86%E4%B8%8E%E6%8C%96%E6%8E%98%E9%95%9C%E5%83%8F)
- [6. 设计理念](#6-设计理念)
- [7.MISC](#7misc)
  - [7.1 常见问题](#71-%E5%B8%B8%E8%A7%81%E9%97%AE%E9%A2%98)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# 1.  AI SUITE-YMIR介绍

YMIR(You Mine In Recursion)是一个简化的模型开发产品，专注于AI SUITE开源系列中的数据集版本和模型迭代。

<div align="center">
  <img src="https://github.com/IndustryEssentials/ymir-images/blob/main/doc_images/%E5%85%A8%E6%B5%81%E7%A8%8B.png" width="1500"/>
<div>&nbsp;</div>&nbsp;</div>

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

| 功能模块     | 一级功能      | 二级功能          | 功能说明      |
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
|项目管理|模型管理|训练模型|支持自选数据集、标签，并根据需求调整训练参数来训练模型，完成后可查看对应的模型效果|
|项目管理|模型管理|模型验证|支持上传单张图片，通过可视化的方式查看模型在真实图片中的表现，以校验模型的精确度|
|标签管理|标签管理|新增标签|支持训练标签的主名和别名的添加|
|模型部署|算法管理|公共算法|支持算法定制化、查看公共算法并试用，支持添加到我的算法中|
|模型部署|算法管理|公共算法|支持发布我的算法到公共算法|
|模型部署|算法管理|我的算法|支持查看和编辑我发布的算法和已添加的算法|
|模型部署|算法管理|部署算法|支持部署我的算法到设备上、查看部署历史|
|模型部署|设备管理|查看设备|支持设备信息和部署历史的查看|
|模型部署|设备管理|编辑设备|支持设备的添加、部署、删除|
|模型部署|设备管理|支持设备|支持对支持设备的查看和购买|
|系统配置|镜像管理|我的镜像|支持添加自定义镜像到系统中（仅管理员可用）|
|系统配置|镜像管理|公共镜像|支持查看其他人上传的公共镜像并复制到自己的系统中|
|系统配置|权限配置|权限管理|支持对用户的权限进行配置（仅管理员可用）|

## 1.2. 申请试用

我们提供一个在线的体验版本，方便您试用，如有需要，请填写[YMIR在线系统申请试用表](https://alfrat.wufoo.com/forms/z2wr9vz0dl1jeo/)，我们会将试用信息发送至您的邮箱。

# 2. 安装

**用户如何选择安装GUI or CMD：**

1.普通用户推荐安装GUI，支持模型的训练、优化完整流程；

2.如需要修改系统默认的配置，推荐安装CMD；

3.如已经部署ymir的已有版本，请参考[升级说明](https://github.com/IndustryEssentials/ymir/blob/dev/ymir/updater/readme_zh-CN.md)。

本章节为YMIR-GUI的安装说明，如需使用CMD，请参考[Ymir-CMD line使用指南](#4-进阶版ymir-cmd-line使用指南)。

## 2.1. 环境依赖

1. GPU版本需要GPU，并安装nvidia驱动: [https://www.nvidia.cn/geforce/drivers/](https://www.nvidia.cn/geforce/drivers/)

2. 需要安装 docker 及 docker compose：
*  docker compose >= 1.29.2, docker >= 20.10
*  Docker & Docker Compose 安装： [https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/)
*  `NVIDIA Docker`安装： [nvidia-docker install-guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#docker)

```sh
## 通过nvidia-smi查看主机显卡驱动支持的最高cuda版本
nvidia-smi
## 对支持CUDA11以上版本的主机, 检查nvidia-docker是否安装成功
sudo docker run --rm --gpus all nvidia/cuda:11.0.3-base-ubuntu20.04 nvidia-smi
## 对支持CUDA10的主机, 检测nvidia-docker是否安装成功
sudo docker run --rm --gpus all nvidia/cuda:10.2-base-ubuntu18.04 nvidia-smi
## 上述命令在终端应输出类似以下的结果 (最高支持cuda 11.6)
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 510.60.02    Driver Version: 510.60.02    CUDA Version: 11.6     |
|-------------------------------+----------------------+----------------------+
| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|                               |                      |               MIG M. |
|===============================+======================+======================|
|   0  Tesla P4            Off  | 00000000:0B:00.0 Off |                    0 |
| N/A   62C    P0    55W /  75W |   4351MiB /  7680MiB |     94%      Default |
|                               |                      |                  N/A |
+-------------------------------+----------------------+----------------------+
+-----------------------------------------------------------------------------+
| Processes:                                                                  |
|  GPU   GI   CI        PID   Type   Process name                  GPU Memory |
|        ID   ID                                                   Usage      |
|=============================================================================|
|    0   N/A  N/A      8132      C                                    4349MiB |
+-----------------------------------------------------------------------------+
```

3. 推荐服务器配置：
*  NVIDIA GeForce RTX 2080 Ti 12G
*  显存最大值到达9974MiB
*  显卡驱动支持的最高CUDA 版本 >= 11.2

## 2.2. 安装 YMIR-GUI

需要保证[环境依赖](#211-环境依赖)中所有条件已满足才能部署，否则容易出现各种不可控问题。

YMIR-GUI项目包在DockerHub上，安装部署YMIR步骤如下：

1. 登录Git地址：[https://github.com/IndustryEssentials/ymir](https://github.com/IndustryEssentials/ymir)

将部署项目YMIR下拉到本地服务器，克隆仓库地址命令：
`git clone https://github.com/IndustryEssentials/ymir.git`

2. 如无可用显卡，用户需要安装CPU模式，请修改为CPU启动模式，修改.env文件将SERVER_RUNTIME参数修改为runc：

`# nvidia for gpu, runc for cpu.`

`SERVER_RUNTIME=runc`

3. 执行启动命令：`bash ymir.sh start`，建议不要使用```sudo```命令，否则可能会造成权限不足。

*  服务启动时会询问用户是否愿意发送使用报告到YMIR开发团队，不输入默认为愿意。
*  当询问用户是否需要启动标注平台时，用户可以选择 label_free 或 label_studio
*  YMIR的模型部署模块默认端口号为18801，如有冲突需要修改，则需要前往YMIR目录下修改.env文件，配置 ModelDeployment 端口和 MySQL 访问密码：

```
DEPLOY_MODULE_HOST_PORT=18801
DEPLOY_MODULE_URL=${DEPLOY_MODULE_HOST_PORT}
DEPLOY_MODULE_MYSQL_ROOT_PASSWORD=deploy_db_passwd
```

修改完成后再执行启动命令：`bash ymir.sh start`。

4. 服务启动成功后，默认配置端口为12001，可以直接访问 [http://localhost:12001/](http://localhost:12001/)  显示登录界面即安装成功。如果需要**停止服务**，运行命令为：`bash ymir.sh stop`

5. 默认初始用户权限为超级管理员，可以通过项目路径下.env文件查看账号密码，部署前可自行设置修改。建议在服务部署完成后，通过用户管理界面修改密码。
<div align="left">
  <img src="https://github.com/IndustryEssentials/ymir-images/blob/main/doc_images/first_admin.png" width="600"/>
  <div>&nbsp;</div>
  
6.进入.env 文件配置，设置发信邮箱信息，配置完成后才可以发送邮件通知。
  
  ```raw
# Email Notification
EMAILS_ENABLED=True
FRONTEND_ENTRYPOINT=<YMIR FRONTEND URL>
SMTP_TLS=
SMTP_PORT=
SMTP_HOST=
SMTP_USER=
SMTP_PASSWORD=
EMAILS_FROM_EMAIL= <SENDER EMAIL ADDRESS>
EMAILS_FROM_NAME=ymir-project
EMAIL_RESET_TOKEN_EXPIRE_HOURS=1
EMAIL_TEMPLATES_DIR=/app/email-templates/build
```

## 2.3. 安装配置LabelStudio （可选）

label studio同时也是YMIR所支持的外接标注系统，可以作为备选标注工具安装。

1. 在上一节的YMIR目录下，修改.env文件，配置 LABEL_TOOL

```
LABEL_TOOL=label_studio
```

2. 配置好标注工具（LABEL_TOOL）后启动安装 label studio 命令如下：

```sh
docker-compose -f docker-compose.label_studio.yml up -d
```

3. 完成后查看label studio状态命令如下：

```sh
docker-compose -f docker-compose.label_studio.yml ps`
```

可以登录默认地址 [http://localhost:8763/](http://localhost:8763/) 显示登录界面即安装成功。

4. 停止label studio服务命令如下：

```sh
docker-compose -f docker-compose.label_studio.yml down
```

# 3. GUI使用-典型模型生产流程

![YMIR-GUI process](https://github.com/IndustryEssentials/ymir-images/blob/main/doc_images/YMIR-GUI-process.jpeg)

数据和标签是深度学习模型训练的必要条件，模型的训练需要大量带标签的数据。然而在实际情况下，现实中存在的是大量没有标签的数据，如果全部由标注人员手工打上标签，人力和时间成本过高。

因此，YMIR平台通过主动学习的方法，首先通过本地导入或者少量数据来训练出一个初始模型，使用该初始模型，从海量数据中挖掘出对模型能力提高最有利的数据。挖掘完成后，仅针对这部分数据进行标注，对原本的训练数据集进行高效扩充。

使用更新后的数据集再次训练模型，以此来提高模型能力。相比于对全部数据标注后再训练，YMIR平台提供的方法更高效，减少了对低质量数据的标注成本。通过挖掘，标注，训练的循环，扩充高质量数据，提升模型能力。

本次使用一次模型迭代的完整流程来说明YMIR平台的操作过程。具体的操作流程请查看[操作说明](https://github.com/IndustryEssentials/ymir/wiki/%E6%93%8D%E4%BD%9C%E8%AF%B4%E6%98%8E)。

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
$ git clone --recursive https://github.com/IndustryEssentials/ymir.git
$ cd ymir/ymir/command
$ python setup.py clean --all install
$ mir --version
```

## 4.2 典型模型生产流程

![流程-中文](https://github.com/IndustryEssentials/ymir-images/blob/main/doc_images/%E6%B5%81%E7%A8%8B-%E4%B8%AD%E6%96%87.jpeg)

上图所示的是模型训练的一个典型流程：用户准备好外部数据，导入本系统，对数据进行适当筛选，开始训练得到一个（可能是粗精度的）模型，并依据这个模型，在一个待挖掘数据集中挑选适合进一步训练的图片，将这些图片进行标注，标注完成的结果与原训练集合并，用合并以后的结果再次执行训练过程，得到效果更好的模型。
在这一节里，我们需要使用命令行实现上图所示的流程，其他流程也可以类似实现。具体操作请查看[命令行使用说明](https://github.com/IndustryEssentials/ymir/wiki/%E5%91%BD%E4%BB%A4%E8%A1%8C%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E)。

# 5.  获取代码

## 5.1  代码贡献

YMIR repo中的任何代码都应遵循编码标准，并将在CI测试中进行检查。

- 功能性代码需要进行单元测试。

- 在提交前使用 [flake8](https://flake8.pycqa.org/en/latest/) 或 [black](https://github.com/ambv/black) 来格式化代码。 这两者均遵循 [PEP8](https://www.python.org/dev/peps/pep-0008) 和 [Google Python Style](https://google.github.io/styleguide/pyguide.html) 风格指南。

- [mypy](http://mypy-lang.org/) - Python必须经过静态类型检查。

也可以查看 [MSFT编码风格](https://github.com/Microsoft/Recommenders/wiki/Coding-Guidelines) 来获取更多的建议。

## 5.2 关于训练，推理与挖掘镜像

[查看这篇文档](https://github.com/IndustryEssentials/ymir/blob/dev/dev_docs/ymir-cmd-container.md)获取更多细节。

# 6. 设计理念

我们使用Git中代码版本控制的概念来管理我们的数据和模型。我们使用分支的概念创建新项目，以便同一组映像上的不同任务可以并行运行。数据集的增加、检索、更新和删除以及基本操作都创建提交到分支。从逻辑上讲，每次提交都存储数据集或新模型的更新版本，以及导致此更改的操作的元数据。最后，只有数据更改被合并到主分支，这在概念上，聚合了该平台上许多项目注释的所有数据。具体设计理念请查看
[Life of a dataset](https://github.com/IndustryEssentials/ymir/wiki/%E6%95%B0%E6%8D%AE%E9%9B%86%E6%B5%81%E8%BD%AC%E8%BF%87%E7%A8%8B)。

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

*  如何导入外部模型

参考[此文档](https://github.com/IndustryEssentials/ymir/blob/dev/dev_docs/import-extra-models.md)。

<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/All%20Contributors-9-brightgreen)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

<a href="https://github.com/phoenix-xhuang"><img src="https://avatars.githubusercontent.com/u/89957974?v=4" class="avatar-user" width="18px;"/></a>
<a href="https://github.com/IJtLJZ8Rm4Yr"><img src="https://avatars.githubusercontent.com/u/90443055?v=4" class="avatar-user" width="18px;"/></a>
<a href="https://github.com/elliotmessi"><img src="https://avatars.githubusercontent.com/u/90443217?v=4" class="avatar-user" width="18px;"/></a>
<a href="https://github.com/Aryalfrat"><img src="https://avatars.githubusercontent.com/u/90443348?v=4" class="avatar-user" width="18px;"/></a>
<a href="https://github.com/fenrir-z"><img src="https://avatars.githubusercontent.com/u/90444968?v=4" class="avatar-user" width="18px;"/></a>
<a href="https://github.com/under-chaos"><img src="https://avatars.githubusercontent.com/u/90446262?v=4" class="avatar-user" width="18px;"/></a>
<a href="https://github.com/Zhang-SJ930104"><img src="https://avatars.githubusercontent.com/u/91466580?v=4" class="avatar-user" width="18px;"/></a>
<a href="https://github.com/LuciferZap"><img src="https://avatars.githubusercontent.com/u/92283801?v=4" class="avatar-user" width="18px;"/></a>
<a href="https://github.com/yzbx"><img src="https://avatars.githubusercontent.com/u/5005182?v=4" class="avatar-user" width="18px;"/></a>


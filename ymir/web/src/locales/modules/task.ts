const task = {
  "task.type.train": { cn: "训练", en: "Train", },
  "task.type.mining": { cn: "挖掘", en: "Mining", },
  "task.type.label": { cn: "标注", en: "Label", },
  "task.type.fusion": { cn: "预处理", en: "Pretreat", },
  "task.type.inference": { cn: "推理", en: "Inference", },
  "task.type.import": { cn: "数据集导入", en: "Dataset Import", },
  "task.type.copy": { cn: "复制", en: "Copy", },
  "task.type.modelimport": { cn: "导入模型", en: "Model Import", },
  "task.type.modelcopy": { cn: "复制模型", en: "Copy Model", },
  "task.type.sys": { cn: "项目训练集", en: "Project Training Dataset", },
  "task.state.pending": { cn: "排队中", en: "Queuing", },
  "task.state.doing": { cn: "进行中", en: "In-Progress", },
  "task.state.finish": { cn: "完成", en: "Finish", },
  "task.state.failure": { cn: "失败", en: "Failure", },
  "task.state.terminated": { cn: '终止', en: 'Terminated', },
  "task.state.terminating": { cn: '正在终止，请耐心等待结果', en: 'Terminating', },
  "task.column.state.timeleft.label": { cn: "剩余时间：", en: "Time Left: ", },
  "task.column.duration": { cn: "时长", en: "Duration", },
  "task.action.terminate": { cn: "终止", en: "Terminate", },
  "task.action.copy": { cn: "复制", en: "Copy", },
  "task.action.terminate.confirm.content": { cn: "确认要终止：{name}？", en: "Are you sure to terminate: {name}?", },
  "task.detail.label.train_goal": { cn: "训练目标", en: "Train Classes", },
  "task.detail.label.framework": { cn: "算法框架", en: "Network", },
  "task.detail.label.create_time": { cn: "创建时间", en: "Created", },
  "task.detail.label.backbone": { cn: "骨干网络结构", en: "Backbone", },
  "task.detail.label.hyperparams": { cn: "高级参数", en: "Senior Config", },
  "task.detail.label.training.image": { cn: "训练镜像", en: "Training Image", },
  "task.detail.label.mining.image": { cn: "挖掘镜像", en: "Mining Image", },
  "task.detail.state.title": { cn: "任务状态", en: "Task State", },
  "task.detail.state.current": { cn: "当前状态", en: "Current State", },
  "task.detail.error.code": { cn: "失败原因", en: "Error Reason", },
  "task.detail.error.desc": { cn: "失败描述", en: "Error Desc", },
  "task.detail.label.download.btn": { cn: "下载标注描述文档", en: "Download Label Desc Doc", },
  "task.detail.error.title": { cn: "失败", en: "Failure", },
  "task.fusion.create.success.msg": { cn: "创建成功", en: "Create Task Success!", },
  "task.fusion.form.dataset": { cn: "原数据集", en: "Original Dataset", },
  "task.fusion.form.datasets.placeholder": { cn: "请选择数据集", en: "Select/Fusion Datasets", },
  "task.fusion.form.include.label": { cn: "保留标签", en: "Keep Keywords", },
  "task.fusion.form.exclude.label": { cn: "排除标签", en: "Exclude Keywords", },
  "task.fusion.form.sampling": { cn: "采样数量", en: "Samples", },
  "task.train.form.trainsets.label": { cn: "训练集", en: "Train Sets", },
  "task.train.form.testsets.label": { cn: "测试集", en: "Test Sets", },
  "task.train.form.keywords.label": { cn: "训练目标", en: "Train Classes", },
  "task.train.form.traintype.label": { cn: "训练类型", en: "Train Type", },
  "task.train.form.network.label": { cn: "算法框架", en: "Network", },
  "task.train.form.backbone.label": { cn: "骨干网络结构", en: "Backbone", },
  "task.train.form.hyperparam.label": { cn: "高级参数", en: "Senior Config", },
  "task.train.form.traintypes.detect": { cn: "目标检测", en: "Object Detection", },
  "task.train.form.image.label": { cn: "镜像选择", en: "Docker Image", },
  "task.train.form.image.placeholder": { cn: "请选择镜像", en: "Please select a docker image", },
  "task.train.form.image.required": { cn: "请选择镜像", en: "Please select a docker image", },
  "task.train.total.label": { cn: "共 {total} 个", en: "Total {total} assets", },
  "task.train.form.repeatdata.label": { cn: "当数据重复时", en: "Found duplicate data", },
  "task.train.form.repeatdata.terminate": { cn: "终止任务", en: "Terminate Task", },
  "task.train.form.repeatdata.latest": { cn: "采用最新的标注", en: "Use Data With Latest Annotation", },
  "task.train.form.repeatdata.original": { cn: "采用最初的标注", en: "Use Data With Original Annotation", },
  "task.mining.form.model.label": { cn: "模型", en: "Model", },
  "task.mining.form.model.required": { cn: "请选择模型", en: "Plese select a model", },

  "task.mining.form.mining.model.required": { cn: "请选择用于数据挖掘的模型", en: "please select the model used for data mining", },

  "task.mining.form.algo.label": { cn: "挖掘算法", en: "Mining Algorithm", },
  "task.mining.form.strategy.label": { cn: "筛选策略", en: "Filter Strategy", },
  "task.mining.form.topk.label": { cn: "TOPK", en: "TOP K", },
  "task.label.form.type.newer": { cn: "未标注部分", en: "Unlabel", },
  "task.mining.form.dataset.label": { cn: "挖掘集", en: "Mining Dataset", },
  "task.mining.form.dataset.required": { cn: "挖掘集为必选项", en: "Mining dataset is required", },
  "task.mining.form.dataset.placeholder": { cn: "请选择挖掘集", en: "Please select mining dataset", },
  "task.mining.form.label.label": { cn: "是否产生新标注", en: "With Annotations", },
  "task.mining.topk.tip": { cn: "TOPK值大于选中数据集大小时，返回全部数据", en: "Top k large than total data will return all data", },
  "task.inference.form.dataset.label": { cn: "数据集", en: "Datasets", },
  "task.inference.form.dataset.required": { cn: "数据集为必选项", en: "Dataset is required", },
  "task.inference.form.dataset.placeholder": { cn: "请选择数据集", en: "Please select dataset", },
  'task.inference.form.desc': { en: 'Description', cn: '备注', },
  "task.inference.form.image.placeholder": { cn: "请选择用于推理的镜像", en: "Please select a docker image for inference", },
  "task.inference.form.image.required": { cn: "请选择用于推理的镜像", en: "Please select a docker image for inference", },
  "task.inference.form.model.required": { cn: "请选择用于数据推理的模型", en: "please select the model used for data inference", },
  "task.inference.model.iters": { cn: "迭代产生的模型", en: "Models from iterations", },
  "task.validator.same.param": { cn: "参数key重复", en: "Duplicate key of params", },
  "task.label.form.type.all": { cn: "全部重新标注", en: "All", },
  "task.label.form.member": { cn: "标注人员", en: "Labeller", },
  "task.label.form.member.required": { cn: "请输入标注人员的邮箱", en: "Please enter labeller's email", },
  "task.label.form.member.placeholder": { cn: "请输入标注人员的邮箱", en: "Please input labeller's email", },

  "task.label.form.member.labelplatacc": { cn: "请输入当前用户在标注平台上的注册邮箱", en: "Please enter the current user's registered email on the labeling platform", },
  "task.label.form.member.labeltarget": { cn: "请选择用于标注的目标标签，可多选", en: "Please select target keyword for marking, multiple options available", },

  "task.label.form.member.email.msg": { cn: "请输入正确的邮箱格式", en: "Please input valid EMAIL", },
  "task.label.form.target.label": { cn: "标注目标", en: "Label Classes", },
  "task.label.form.target.placeholder": { cn: "请选择标注目标", en: "Please select label classes", },
  "task.label.form.desc.label": { cn: "标注描述文件", en: "Desc File", },
  "task.label.form.desc.info": { cn: "1. 允许上传doc、docx、pdf等文档{br} 2. 文件大小不超过50M", en: "1. *.doc, *.docx, *.pdf allowed {br} 2. file size < 50M", },
  "task.label.form.plat.checker": { cn: "到标注平台查看", en: "View In Label Platform", },
  "task.label.form.plat.label": { cn: "标注平台账号", en: "Label Platform Account", },
  "task.label.form.plat.go": { cn: "到标注平台注册账号", en: "Label Platform", },
  "task.label.form.keep_anno.label": { cn: "保留原标注", en: "Keep Annotations", },
  "task.train.fold": { cn: '收起参数配置', en: 'Fold', },
  "task.train.unfold": { cn: '展开参数配置', en: 'Unfold', },
  "task.train.parameter.add.label": { cn: '添加自定义参数', en: 'Add Custom Parameter', },
  "task.label.bottomtip": { cn: '没有标注人员账号or邮箱，我要{link}', en: 'None of labeller account, {link}', },
  "task.label.bottomtip.link.label": { cn: '注册标注平台账号>>', en: 'sign up Label Platform Account >>', },
  "task.btn.back": { cn: '返回', en: 'Back', },
  "task.gpu.count": { cn: 'GPU个数', en: 'GPU Count', },
  "task.train.gpu.invalid": { cn: 'GPU个数必须在{min}-{max}之间', en: 'GPU Count must between {min} - {max}', },
  "task.gpu.tip": { cn: '当前可用GPU个数为 {count}', en: 'Valid GPU count: {count}', },
  'task.detail.label.go.platform': { cn: '跳转到标注平台>>', en: 'Go to Label Platform >>' },
  "task.terminate.label.nodata": { cn: '不获取数据终止', en: 'Terminate', },
  "task.terminate.label.withdata": { cn: '获取结果终止', en: 'Terminate & Fetch Result', },
  "task.detail.tensorboard.link.label": { cn: '到TensorBoard查看训练详情', en: 'View in Tensorboard', },
  "tip.task.train.model": { cn: '此次训练将会基于选择的模型的基础上继续训练，迭代次数将会累加，目前训练目标需要和模型保持一致', en: 'This training task will base on the model selected, and training target will be ', },
  "task.train.form.model.placeholder": { cn: '请选择模型', en: 'Please select a model', },
  "task.fusion.header.merge": { cn: '数据集合并', en: 'Dataset Merge', },
  "task.fusion.header.filter": { cn: '数据集筛选', en: 'Dataset Filter', },
  "task.fusion.header.sampling": { cn: '数据集采样', en: 'Dataset Sampling', },
  "task.fusion.form.merge.include.label": { cn: '合并数据集', en: 'Merge Datasets', },
  "task.fusion.form.merge.exclude.label": { cn: '排除数据集', en: 'Exclude Datasets', },
  "task.train.form.training.datasets.placeholder": { cn: "请选择数据集", en: "Please select a dataset", },
  "task.train.form.testset.required": { cn: "测试集为必选项", en: "Test dataset is required", },
  "task.train.form.trainset.required": { cn: "训练集为必选项", en: "Training dataset is required", },
  "task.train.form.miningset.required": { cn: "挖掘集为必选项", en: "Mining dataset is required", },
  "task.train.form.test.datasets.placeholder": { cn: "请选择测试集", en: "Please select a test dataset", },
  "task.origin.dataset": { cn: "来源数据集", en: "Original Dataset", },
  "task.detail.include_datasets.label": { cn: "合并数据集", en: "Merge Datasets", },
  "task.detail.exclude_datasets.label": { cn: "排除数据集", en: "Exclude Datasets", },
  "task.detail.include_labels.label": { cn: "保留标签", en: "Include Keywords", },
  "task.detail.exclude_labels.label": { cn: "排除标签", en: "Exclude Keywords", },
  "task.detail.samples.label": { cn: "采样数", en: "Sampling Count", },
  "task.detail.source.sys": { cn: "系统自动生成项目训练集", en: "Project training dataset generated by system", },
  "task.infer.gpu.tip": { cn: "，请输入每个模型分配到的GPU个数", en: ", input for each model", },
}

export default task

const task = {
  'task.type.train': { cn: '训练', en: 'Train' },
  'task.type.mining': { cn: '挖掘', en: 'Mining' },
  'task.type.label': { cn: '标注', en: 'Label' },
  'task.type.fusion': { cn: '预处理', en: 'Pretreat' },
  'task.type.merge': { cn: '合并', en: 'Merge' },
  'task.type.filter': { cn: '筛选', en: 'Filter' },
  'task.type.inference': { cn: '推理', en: 'Inference' },
  'task.type.import': { cn: '添加数据集', en: 'Dataset Add' },
  'task.type.copy': { cn: '复制', en: 'Copy' },
  'task.type.modelimport': { cn: '导入模型', en: 'Model Import' },
  'task.type.modelcopy': { cn: '复制模型', en: 'Copy Model' },
  'task.type.sys': { cn: '项目训练集', en: 'Project Training Dataset' },
  'task.state.pending': { cn: '排队中', en: 'Queuing' },
  'task.state.doing': { cn: '进行中', en: 'In-Progress' },
  'task.state.finish': { cn: '完成', en: 'Finish' },
  'task.state.failure': { cn: '失败', en: 'Failure' },
  'task.state.terminated': { cn: '终止', en: 'Terminated' },
  'task.state.terminating': {
    cn: '正在终止，请耐心等待结果',
    en: 'Terminating',
  },
  'task.column.state.timeleft.label': { cn: '剩余时间：', en: 'Time Left: ' },
  'task.column.duration': { cn: '时长', en: 'Duration' },
  'task.action.terminate': { cn: '终止', en: 'Terminate' },
  'task.action.copy': { cn: '复制', en: 'Copy' },
  'task.action.training': { cn: '训练过程', en: 'Training Process' },
  'task.action.training.batch': {
    cn: '多模型训练过程',
    en: 'Models Training Process',
  },
  'task.action.terminate.confirm.content': {
    cn: '确认要终止：{name}？',
    en: 'Are you sure to terminate: {name}?',
  },
  'task.detail.label.train_goal': { cn: '训练目标', en: 'Target' },
  'task.detail.label.framework': { cn: '算法框架', en: 'Network' },
  'task.detail.label.create_time': { cn: '创建时间', en: 'Created' },
  'task.detail.label.premodel': { cn: '预训练模型', en: 'Pre-Training Model' },
  'task.detail.label.backbone': { cn: '骨干网络结构', en: 'Backbone' },
  'task.detail.label.training.image': { cn: '训练镜像', en: 'Training Image' },
  'task.detail.label.mining.image': { cn: '挖掘镜像', en: 'Mining Image' },
  'task.detail.label.inference.image': {
    cn: '推理镜像',
    en: 'Inference Image',
  },
  'task.detail.state.title': { cn: '状态', en: 'State' },
  'task.detail.state.current': { cn: '当前进度', en: 'Progress' },
  'task.detail.error.code': { cn: '失败原因', en: 'Error Reason' },
  'task.detail.error.desc': { cn: '失败描述', en: 'Error Desc' },
  'task.detail.label.download.btn': {
    cn: '下载标注描述文档',
    en: 'Download Label Desc Doc',
  },
  'task.detail.error.title': { cn: '失败', en: 'Failure' },
  'task.fusion.create.success.msg': {
    cn: '创建成功',
    en: 'Create Task Success!',
  },
  'task.fusion.form.dataset': { cn: '当前数据集', en: 'Current Dataset' },
  'task.fusion.form.datasets.placeholder': {
    cn: '请选择数据集',
    en: 'Select/Fusion Datasets',
  },
  'task.fusion.form.include.label': { cn: '保留类别', en: 'Keep Classes' },
  'task.fusion.form.exclude.label': { cn: '排除类别', en: 'Exclude Classes' },
  'task.fusion.form.sampling': { cn: '采样数量', en: 'Samples' },
  'task.train.form.trainsets.label': { cn: '训练集', en: 'Train Sets' },
  'task.train.form.testsets.label': { cn: '验证集', en: 'Validation Sets' },
  'task.train.form.keywords.label': { cn: '训练目标', en: 'Target' },
  'task.train.form.traintype.label': { cn: '训练类型', en: 'Train Type' },
  'task.train.form.network.label': { cn: '算法框架', en: 'Network' },
  'task.train.form.backbone.label': { cn: '骨干网络结构', en: 'Backbone' },
  'task.train.form.hyperparam.label': {
    cn: '超参数配置',
    en: 'Hyper Parameters Config',
  },
  'task.train.form.hyperparam.label.tip': {
    cn: '（点击切换展开/收起）',
    en: ' (click to toggle unfold/fold)',
  },
  'task.train.form.traintypes.detect': {
    cn: '目标检测',
    en: 'Object Detection',
  },
  'task.train.form.image.label': { cn: '训练镜像', en: 'Training Image' },
  'task.inference.form.image.label': { cn: '推理镜像', en: 'Inference Image' },
  'task.mining.form.image.label': { cn: '挖掘镜像', en: 'Mining Image' },
  'task.train.form.image.placeholder': {
    cn: '请选择镜像',
    en: 'Please select a docker image',
  },
  'task.train.form.image.required': {
    cn: '镜像为必选项',
    en: 'Training docker image is required',
  },
  'task.train.total.label': { cn: '共 {total} 个', en: 'Total {total} assets' },
  'task.train.form.repeatdata.label': {
    cn: '当数据重复时',
    en: 'Found duplicate data',
  },
  'task.train.form.repeatdata.terminate': {
    cn: '终止任务',
    en: 'Terminate Task',
  },
  'task.train.form.repeatdata.latest': {
    cn: '采用最新的标注',
    en: 'Use Data With Latest Annotation',
  },
  'task.train.form.repeatdata.original': {
    cn: '采用最初的标注',
    en: 'Use Data With Original Annotation',
  },
  'task.mining.form.model.label': { cn: '模型', en: 'Model' },
  'task.mining.form.model.required': {
    cn: '请选择模型',
    en: 'Plese select a model',
  },
  'task.train.form.keywords.placeholder': {
    en: 'Please select classes',
    cn: '请选择训练目标',
  },
  'task.mining.form.mining.model.required': {
    cn: '请选择用于数据挖掘的模型',
    en: 'please select the model used for data mining',
  },

  'task.mining.form.algo.label': { cn: '挖掘算法', en: 'Mining Algorithm' },
  'task.mining.form.topk.label': { cn: 'TOPK', en: 'TOP K' },
  'task.label.form.type.newer': { cn: '未标注部分', en: 'Unlabel' },
  'task.mining.form.dataset.label': { cn: '挖掘集', en: 'Mining Dataset' },
  'task.mining.form.dataset.required': {
    cn: '挖掘集为必选项',
    en: 'Mining dataset is required',
  },
  'task.mining.form.dataset.placeholder': {
    cn: '请选择挖掘集',
    en: 'Please select mining dataset',
  },
  'task.mining.form.label.label': {
    cn: '是否产生新标注',
    en: 'With Annotations',
  },
  'task.mining.topk.tip': {
    cn: 'TOPK值大于选中数据集大小时，返回全部数据',
    en: 'Top k large than total data will return all data',
  },
  'task.inference.form.dataset.label': { cn: '数据集', en: 'Datasets' },
  'task.inference.form.dataset.required': {
    cn: '数据集为必选项',
    en: 'Dataset is required',
  },
  'task.inference.form.dataset.placeholder': {
    cn: '请选择数据集',
    en: 'Please select dataset',
  },
  'task.inference.form.desc': { en: 'Description', cn: '备注' },
  'task.inference.form.image.placeholder': {
    cn: '请选择用于推理的镜像',
    en: 'Please select a docker image for inference',
  },
  'task.inference.form.image.required': {
    cn: '请选择用于推理的镜像',
    en: 'Please select a docker image for inference',
  },
  'task.inference.form.model.required': {
    cn: '请选择用于数据推理的模型',
    en: 'please select the model used for data inference',
  },
  'task.inference.model.iters': {
    cn: '迭代产生的模型',
    en: 'Model generated by iteration process',
  },
  'task.inference.failure.some': {
    cn: '部分推理失败',
    en: 'Part of inference tasks fail',
  },
  'task.validator.same.param': {
    cn: '参数key重复',
    en: 'Duplicate key of params',
  },
  'task.label.form.type.all': { cn: '全部重新标注', en: 'All' },
  'task.label.form.member': { cn: '标注人员', en: 'Labeller' },
  'task.label.form.member.required': {
    cn: '请输入标注人员的邮箱',
    en: "Please enter labeller's email",
  },
  'task.label.form.member.placeholder': {
    cn: '请输入标注人员的邮箱',
    en: "Please input labeller's email",
  },

  'task.label.form.member.labelplatacc': {
    cn: '请输入当前用户在标注平台上的注册邮箱',
    en: "Please enter the current user's registered email on the labeling platform",
  },
  'task.label.form.member.labeltarget': {
    cn: '请选择用于标注的目标类别，可多选',
    en: 'Please select classes for marking, multiple options available',
  },

  'task.label.form.member.email.msg': {
    cn: '请输入正确的邮箱格式',
    en: 'Please input valid EMAIL',
  },
  'task.label.form.target.label': { cn: '标注目标', en: 'Label Classes' },
  'task.label.form.target.placeholder': {
    cn: '请选择标注目标',
    en: 'Please select label classes',
  },
  'task.label.form.desc.label': { cn: '标注描述文件', en: 'Desc File' },
  'task.label.form.desc.info': {
    cn: '1. 允许上传doc、docx、pdf等文档{br} 2. 文件大小不超过50M',
    en: '1. *.doc, *.docx, *.pdf allowed {br} 2. file size < 50M',
  },
  'task.label.form.plat.checker': {
    cn: '到标注平台查看',
    en: 'View In Label Platform',
  },
  'task.label.form.plat.label': {
    cn: '标注平台账号',
    en: 'Label Platform Account',
  },
  'task.label.form.plat.go': { cn: '到标注平台注册账号', en: 'Label Platform' },
  'task.label.form.keep_anno.label': {
    cn: '保留原标注',
    en: 'Keep Annotations',
  },
  'task.label.form.keep_anno.none': { cn: '不保留原标注', en: 'No' },
  'task.label.form.keep_anno.gt': { cn: '保留标注', en: 'Keep GT' },
  'task.label.form.keep_anno.pred': {
    cn: '保留预测标注',
    en: 'Keep Prediction',
  },
  'task.train.fold': { cn: '收起参数配置', en: 'Fold' },
  'task.train.unfold': { cn: '展开参数配置', en: 'Unfold' },
  'task.train.parameter.add.label': {
    cn: '添加自定义参数',
    en: 'Add Custom Parameter',
  },
  'task.label.bottomtip': { cn: '前往{link}标注', en: 'Go to {link}' },
  'task.label.bottomtip.link.label': { cn: '标注平台', en: 'Label Platform' },
  'task.btn.back': { cn: '返回', en: 'Back' },
  'task.gpu.count': { cn: '空闲GPU数量', en: 'Idle GPU Count' },
  'task.train.gpu.invalid': {
    cn: 'GPU个数必须在{min}-{max}之间',
    en: 'GPU Count must between {min} - {max}',
  },
  'task.gpu.tip': {
    cn: '当前可用空闲GPU个数为 {count}',
    en: 'Valid Idle GPU count: {count}',
  },
  'task.detail.label.go.platform': {
    cn: '跳转到标注平台>>',
    en: 'Go to Label Platform >>',
  },
  'task.detail.label.processing': { cn: '训练过程', en: 'Training Processing' },
  'task.detail.label.function': { cn: '训练方式', en: 'Training Function' },
  'task.detail.function.live': { cn: '远端训练', en: 'Livecode Training' },
  'task.detail.function.local': { cn: '本地训练', en: 'Local Training' },
  'task.terminate.label.nodata': { cn: '不获取数据终止', en: 'Terminate' },
  'task.terminate.label.withdata': {
    cn: '获取结果终止',
    en: 'Terminate & Fetch Result',
  },
  'task.detail.tensorboard.link.label': { cn: '去查看>>', en: 'View Training' },
  'tip.task.train.model': {
    cn: '此次训练将会基于选择的模型的基础上继续训练，迭代次数将会累加，目前训练目标需要和模型保持一致',
    en: 'This training task will base on the model selected, and training target will be ',
  },
  'task.train.form.model.placeholder': {
    cn: '请选择模型',
    en: 'Please select a model',
  },
  'task.fusion.header.merge': { cn: '数据集合并', en: 'Dataset Merge' },
  'task.fusion.header.filter': { cn: '数据集筛选', en: 'Dataset Filter' },
  'task.fusion.header.sampling': { cn: '数据集采样', en: 'Dataset Sampling' },
  'task.fusion.form.merge.include.label': {
    cn: '合并数据集',
    en: 'Merge Datasets',
  },
  'task.fusion.form.merge.exclude.label': {
    cn: '排除数据集',
    en: 'Exclude Datasets',
  },
  'task.train.form.training.datasets.placeholder': {
    cn: '请选择数据集',
    en: 'Please select a dataset',
  },
  'task.fusion.form.includes.label': {
    cn: '添加挖掘数据',
    en: 'Merge Mining Datasets',
  },
  'task.fusion.form.excludes.label': {
    cn: '排除挖掘数据',
    en: 'Exclude Mining Datasets',
  },
  'task.fusion.form.class.include.label': {
    cn: '选择数据类别',
    en: 'Select Classes',
  },
  'task.fusion.form.class.exclude.label': {
    cn: '排除数据类别',
    en: 'Exclude Classes',
  },
  'task.train.form.testset.required': {
    cn: '验证集为必选项',
    en: 'Validation dataset is required',
  },
  'task.train.form.trainset.required': {
    cn: '训练集为必选项',
    en: 'Training dataset is required',
  },
  'task.train.form.miningset.required': {
    cn: '挖掘集为必选项',
    en: 'Mining dataset is required',
  },
  'task.train.form.test.datasets.placeholder': {
    cn: '请选择验证集',
    en: 'Please select a validation dataset',
  },
  'task.origin.dataset': { cn: '来源数据集', en: 'Original Dataset' },
  'task.detail.include_datasets.label': {
    cn: '合并数据集',
    en: 'Merge Datasets',
  },
  'task.detail.exclude_datasets.label': {
    cn: '排除数据集',
    en: 'Exclude Datasets',
  },
  'task.detail.include_labels.label': { cn: '保留类别', en: 'Include Classes' },
  'task.detail.exclude_labels.label': { cn: '排除类别', en: 'Exclude Classes' },
  'task.detail.samples.label': { cn: '采样数', en: 'Sampling Count' },
  'task.detail.source.sys': {
    cn: '系统自动生成项目训练集',
    en: 'Project training dataset generated by system',
  },
  'task.infer.gpu.tip': {
    cn: '请输入单个模型在单个数据集上推理需要的GPU个数，目前已选中{selected}/{total}',
    en: 'Input GPU count for single model infer single dataset, currently {selected}/{total} selected.',
  },
  'task.inference.unmatch.keywrods': {
    cn: '选中的模型中的训练目标{keywords}不在当前用户的类别列表中，推理对这些目标无效',
    en: 'Inference partial invalidity by {keywords} for selected model out of KEYWORD LIST of current user.',
  },
  'task.train.live.title': { en: 'Live Code Configure', cn: '远程代码配置' },
  'task.train.live.url': { en: 'GitHub Repo. URL', cn: 'GitHub仓库地址' },
  'task.train.live.id': { en: 'Commit ID', cn: '提交ID' },
  'task.train.live.config': { en: 'Config Filename', cn: '配置文件名称' },
  'task.train.live.url.placeholder': {
    en: 'Plese input your GitHub repo. URL, http(s) supported',
    cn: '请输入GitHub仓库地址, 请使用http或https协议，暂不支持git协议',
  },
  'task.train.live.id.placeholder': {
    en: 'Please input your commit ID',
    cn: '请输入提交ID',
  },
  'task.train.live.config.placeholder': {
    en: 'Please input relative path to your config filename， e.g. config/white.yaml',
    cn: '请输入配置文件名称的相对路径, 如 config/white.yaml',
  },
  'task.train.form.platform.label': { en: 'Use Openpai', cn: '使用Openpai' },
  'task.train.device.local': { en: 'Local', cn: '本地训练' },
  'task.train.device.openpai': { en: 'OpenPAI', cn: 'OpenPAI训练' },
  'task.train.export.format': { en: 'Format For Training', cn: '数据导出格式' },
  'task.infer.diagnose.tip': {
    en: 'Are Models not yet test?',
    cn: '尚未对模型进行测试？',
  },
  'task.train.action.duplicated': { en: 'Check Duplication', cn: '检测重复性' },
  'task.train.duplicated.option.train': {
    en: 'duplicated as trainset data',
    cn: '重复数据仅用于训练集',
  },
  'task.train.duplicated.option.validation': {
    en: 'duplicated as validation data',
    cn: '重复数据仅用于验证集',
  },
  'task.train.duplicated.tip': {
    en: '{duplicated} assets duplicated, please select strategy: ',
    cn: '检测到训练集和验证集有{duplicated}张重复数据，请选择策略：',
  },
  'task.train.action.duplicated.no': {
    en: 'None of duplicated assets',
    cn: '无重复数据',
  },
  'task.train.action.duplicated.all': {
    en: 'Duplicated completely, please select another training dataset or validation dataset.',
    cn: '数据完全重复，请重新选择训练集或验证集',
  },
  'task.train.preprocess.title': { en: 'Image Preprocess', cn: '图像前处理' },
  'task.train.preprocess.resize': {
    en: 'Maximum Side Length Resize',
    cn: '最长边长缩放',
  },
  'task.train.preprocess.resize.tip': {
    en: 'Images will resize as original scale which longest width/height equal to input value',
    cn: '图像将按原始比例缩放至最长边为设置值',
  },
  'task.train.preprocess.resize.placeholder': {
    en: 'Max width/height',
    cn: '最大高/宽',
  },
  'task.filter.includes.placeholder': {
    en: 'Please select inclusion classes',
    cn: '请选择保留的类别',
  },
  'task.filter.excludes.placeholder': {
    en: 'Please select exclusion classes',
    cn: '请选择需要排除掉的类别',
  },
  'task.state': { en: 'Task Status', cn: '任务状态' },
  'task.detail.terminated.label': { en: 'Terminated', cn: '终止' },
  'task.detail.terminated': { en: 'Terminated by user', cn: '用户手动终止' },
  'task.inference.header.tip': {
    en: "Inference result dataset will generate prediction, and inherit original testing set's GT.",
    cn: '推理结果数据集将生成新的预测标注，并包含原测试集的标注。',
  },
  'task.label.header.tip': {
    en: 'Labelling result dataset will generate GT.',
    cn: '标注结果数据集会生成新的标注。',
  },
  'task.merge.type.label': { en: 'Merge Type', cn: '合并方式' },
  'task.merge.type.new': { en: 'Generate a new dataset', cn: '生成新数据集' },
  'task.merge.type.exist': {
    en: 'Generate a version for original dataset',
    cn: '在当前数据集上生成新版本',
  },
  'task.train.btn.calc.negative': {
    en: 'Calculate Positive/Negative Samples',
    cn: '计算正负样本',
  },
  'task.panel.settings.advanced': { en: 'Advanced Settings', cn: '高级设置' },
  'task.train.keywords.disabled.tip': { en: 'Training dataset required', cn: '请先选择训练集' },
  'task.train.validation.disabled.tip': { en: 'Training target required', cn: '请先选择训练目标' },
}

export default task

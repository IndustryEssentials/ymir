const tip = {
  'tip.image.add.name': {
    cn: "镜像地址，dockerhub上镜像的名称，可以带tag，不带tag默认latest",
    en: "Image name from Docker Hub. E.G. image_name:tag. Default tag: latest.",
  },
  'tip.image.add.url': {
    cn: "镜像名称",
    en: "Image name",
  },
  'tip.image.add.desc': {
    cn: "描述镜像的类型，功能以及使用注意等等",
    en: "Image description for type, function etc.",
  },
  "tip.task.fusion.includelable": {
    cn: "期望生成的数据集包含选中的标签值",
    en: "Filtering tips: the generated dataset  expect to contain the selected keyword",
  },
  "tip.task.fusion.excludelable": {
    cn: "期望生成的数据集不包含选中的标签值",
    en: "Excluding tips: the generated dataset expect to not contain the selected keyword",
  },
  "tip.task.fusion.sampling": {
    cn: "期望的最大采样数量",
    en: "Samples expected.",
  },
  "tip.task.filter.testsets": {
    cn: "训练集和测试集的图片不可重复",
    en: "The images of the training set and the testing set cannot be duplicated.",
  },
  "tip.task.filter.keywords": {
    cn: "训练目标标签必须同时包含在训练集和测试集中",
    en: "Both the training and testing sets must contain target keyword",
  },
  "tip.task.train.image": {
    cn: "平台提供默认训练镜像，同时支持开发者自主开发并接入。镜像会附带默认配置参数，可按需调整。",
    en: "Default training image supported, and you can add your own training image. Training docker image have its own senior config, you can modify it for training task.",
  },
  "tip.task.mining.image": {
    cn: "平台提供默认挖掘镜像，同时支持开发者自主开发并接入。镜像会附带默认配置参数，可按需调整。",
    en: "Default mining image supported, and you can add your own image. Mining docker image have its own senior config, you can modify it for training task.",
  },
  "tip.task.inference.image": {
    cn: "平台提供默认推理镜像，同时支持开发者自主开发并接入。镜像会附带默认配置参数，可按需调整。",
    en: "Default Inferential image supported, and you can add your own image. Mining docker image have its own senior config, you can modify it for training task.",
  },
  "tip.task.filter.gpucount": {
    cn: "所选GPU个数越多，训练速度越快，请注意资源合理分配",
    en: "GPU number tips: The more GPUs you select, the faster the training speed will be, please allocate resources reasonably",
  },
  "tip.task.filter.hyperparams": {
    cn: "训练镜像中需传入的运行参数，默认为最佳推荐配置",
    en: "Hyperparameter tips: the operation parameters to be entered in the training docker, the default value is the best recommended configuration",
  },
  "tip.task.filter.model": {
    cn: "初始模型用于第一轮迭代时的数据挖掘，可以通过导入或者训练添加。",
    en: "The initial model is used for data mining during the first iteration and can be added by importing or training.",
  },
  "tip.task.filter.strategy": {
    cn: "用户自定义挖掘结果数据集的大小，即希望保留TopK个最有利于模型优化的数据。在选择多个数据集时，由于可能存在重复数据，合并后的结果小于所选数据集之和，当用户自定义TopK值大于合并后的数据集大小时，则返回全部数据。",
    en: "User-defined size of the mined result dataset, i.e., you want to keep the TopK data that are most conducive to model optimization.When multiple datasets are selected, the merged result may be smaller than the sum of the selected datasets due to the possible existence of duplicate data. When the user-defined TopK value is larger than the size of the merged dataset, all data are returned.",
  },
  "tip.task.filter.newlable": {
    cn: "通过所选模型对数据集进行推理，产生新的标注结果",
    en: "The selected model will be used to infer the dataset and generate new annotations",
  },
  "tip.task.filter.mgpucount": {
    cn: "所选GPU个数越多，挖掘速度越快，请注意资源合理分配",
    en: "The more GPUs you select, the faster the mining speed will be, please allocate resources reasonably",
  },
  "tip.task.filter.mhyperparams": {
    cn: "挖掘镜像中需传入的运行参数，默认为最佳推荐配置",
    en: "The operation parameters to be entered in the mining docker, the default value is the best recommended configuration",
  },
  "tip.task.filter.imodel": {
    cn: "推理出来的数据一般用于该模型的效果优化",
    en: "The inferential dataset is generally used for the optimization of the selected model",
  },
  "tip.task.filter.igpucount": {
    cn: "所选GPU个数越多，推理速度越快，请注意资源合理分配",
    en: "The more GPUs you select, the faster the inferential speed will be, please allocate resources reasonably",
  },
  "tip.task.filter.ihyperparams": {
    cn: "推理镜像中需传入的运行参数，默认为最佳推荐配置",
    en: "The operation parameters to be entered in the inferential docker, the default value is the best recommended configuration",
  },
  "tip.task.filter.labelmember": {
    cn: "请确保标注人员的账号已提前注册",
    en: "Please make sure the annotator account has been registered in advance",
  },
  "tip.task.filter.labelplatacc": {
    cn: "该账号可到标注平台查看标注进度，请提前注册",
    en: "The account can be used to view the labeling progress on the labeling platform, please register in advance",
  },
  "tip.task.filter.labeltarget": {
    cn: "仅支持在当前用户标签列表中选择，如果当前列表没有期望标注的目标标签，请前往标签列表添加",
    en: "Only support the current user‘s keyword list to choose,if the current list does not have the target keyword, please go to the keyword list to add ",
  },
  "tip.task.filter.datasets": {
    cn: "公共数据集为系统内置数据集，支持用户复用",
    en: "Dataset tips: public dataset is the system built-in dataset, support user to reuse",
  },
  "tip.task.filter.alias": {
    cn: "和主名表示同一类标签，当导入的数据集标签为别名时，界面展示为主名",
    en: "The same type of keyword as the main name, when the imported dataset contains an alias keyword, the interface shows the keyword's main name",
  },
  "project.add.trainset.tip": {
    cn: '每轮迭代都会更新该训练集的训练数据，需要包含目标标注',
    en: 'Classes annotations required, training data will update in every iterations',
  },
  "project.add.testset.tip": {
    cn: '用于指导训练集进行训练和测试，可获得更客观的模型效果评估结果，该数据集需要有标注。',
    en: 'It is used to guide the training set for training and testing, which can obtain more objective results for model effect evaluation. This dataset needs to be annotated.',
  },
  "project.add.miningset.tip": {
    cn: '一般情况下无标注且数据量大，通过数据挖掘在该数据集下找到更贴合目标业务场景的数据。',
    en: 'Generally unlabeled and with a large amount of data, data mining is used to find data that better fits the target business scenario under that data set.',
  },

}

export default tip

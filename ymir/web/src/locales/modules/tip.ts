const tip = {
  // 新建筛选标签
  "tip.task.filter.includelable": { cn: "期望生成的数据集包含选中的标签值", en: "", },
  "tip.task.filter.excludelable": { cn: "期望生成的数据集不包含选中的标签值", en: "", },

  // 新建训练任务
  "tip.task.filter.testsets": { cn: "训练集和测试集的图片不可重复", en: "", },
  "tip.task.filter.keywords": { cn: "训练目标标签必须同时包含在训练集和测试集中", en: "", },
  // "tip.task.filter.traintype": { cn: "训练类型提示", en: "", },
  // "tip.task.filter.network": { cn: "算法框架提示", en: "", },
  // "tip.task.filter.backbone": { cn: "骨干网络结构提示", en: "", },
  "tip.task.filter.gpucount": { cn: "所选GPU个数越多，训练速度越快，请注意资源合理分配", en: "", },
  "tip.task.filter.hyperparams": { cn: "训练镜像中需传入的运行参数，默认为最佳推荐配置", en: "", },

  // 新建挖掘任务
  "tip.task.filter.title": { cn: "通过挖掘在大量数据中选出最有利于模型优化的数据", en: "", },
  "tip.task.filter.excludeset": { cn: "选中的数据集将不会出现在挖掘结果中", en: "", },
  "tip.task.filter.model": { cn: "挖掘出来的数据一般用于该模型的效果优化", en: "", },
  // "tip.task.filter.miningalgo": { cn: "挖掘算法", en: "", },
  "tip.task.filter.strategy": { cn: "用户自定义挖掘结果数据集的大小，即希望保留TopK个最有利于模型优化的数据。在选择多个数据集时，由于可能存在重复数据，合并后的结果小于所选数据集之和，当用户自定义TopK值大于合并后的数据集大小时，则返回全部数据。", en: "", },
  "tip.task.filter.newlable": { cn: "通过所选模型对数据集进行推理，产生新的标注结果", en: "", },
  "tip.task.filter.mgpucount": { cn: "所选GPU个数越多，挖掘速度越快，请注意资源合理分配", en: "", },
  "tip.task.filter.mhyperparams": { cn: "挖掘镜像中需传入的运行参数，默认为最佳推荐配置", en: "", },

  // 新建标注任务
  "tip.task.filter.labelmember": { cn: "请确保标注人员的账号已提前注册", en: "", },
  "tip.task.filter.labelplatacc": { cn: "该账号可到标注平台查看标注进度，请提前注册", en: "", },
  "tip.task.filter.labeltarget": { cn: "仅支持在当前用户标签列表中选择，如果当前列表没有期望标注的目标标签，请前往标签列表添加", en: "", },

  // 导入数据集
  
  "tip.task.filter.datasets": { cn: "公共数据集为系统内置数据集，支持用户复用", en: "", },
  // "tip.task.filter.type": { cn: "导入类型", en: "", },
  // "tip.task.filter.addlable": { cn: "包含标注", en: "", },
 

}

export default tip

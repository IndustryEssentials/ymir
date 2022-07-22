const dataset = {
  "dataset.list": { cn: "数据集管理", en: "Datasets", },
  "dataset.detail.title": { cn: "数据集详情", en: "Dataset Detail", },
  "dataset.asset.title": { cn: "数据详情", en: "Dataset Assets", },
  "dataset.state.ready": { cn: "进行中", en: "Running", },
  "dataset.state.valid": { cn: "可用", en: "Valid", },
  "dataset.state.invalid": { cn: "不可用", en: "Invalid", },
  "dataset.column.name": { cn: "版本", en: "Version", },
  "dataset.column.source": { cn: "数据集来源", en: "Dataset Source", },
  "dataset.column.asset_count": { cn: "图片数", en: "Assets' Count", },
  "dataset.column.keyword": { cn: "标签", en: "Keywords", },
  "dataset.column.ignored_keyword": { cn: "忽略标签", en: "Ignored Keywords", },
  "dataset.column.state": { cn: "状态", en: "Status", },
  "dataset.column.create_time": { cn: "创建时间", en: "Create Time", },
  "dataset.column.hidden_time": { cn: "隐藏时间", en: "Hidden Time", },
  "dataset.column.model": { cn: "模型名称", en: "Model Name", },
  "dataset.column.map": { cn: "mAP(平均IoU)", en: "mAP(Average of IoU)", },
  "dataset.column.action": { cn: "操作", en: "Actions", },
  "dataset.column.keyword.label": { cn: "{keywords} 共{total}个", en: "{keywords} total {total}.", },
  "dataset.action.fusion": { cn: "预处理", en: "Pretreat", },
  "dataset.action.train": { cn: "训练", en: "Train", },
  "dataset.action.mining": { cn: "挖掘", en: "Mining", },
  "dataset.action.label": { cn: "标注", en: "Label", },
  "dataset.action.del": { cn: "删除", en: "Remove", },
  "dataset.action.detail": { cn: "详情", en: "Detail", },
  "dataset.action.edit": { cn: "编辑", en: "Rename", },
  'dataset.action.inference': { cn: '推理', en: 'Inference', },
  "dataset.empty.label": { cn: "去导入一个数据集", en: "Import A Dataset", },
  "dataset.import.label": { cn: "添加数据集", en: "Add Dataset", },
  "dataset.query.name": { cn: "名称", en: "Dataset Name", },
  "dataset.action.del.confirm.content": { cn: "确认要删除数据集版本：{name}？", en: "Are you sure to remove this dataset version:{name}?", },
  "dataset.action.hide.confirm.content": { cn: "确认要隐藏数据集版本：{name}？", en: "Are you sure to hide dataset versions: {name}?", },
  "dataset.hide.single.invalid": { cn: "该版本不能隐藏", en: "This version can not be hide", },
  "dataset.action.hide.confirm.exclude": {
    cn: "以下版本因与项目、迭代等关联不能隐藏：{labels}",
    en: "The following related to project or iterations can not be hide: {name}.",
  },
  "dataset.action.delgroup.confirm.content": {
    en: "Are you sure to remove this dataset:{name}, all of versions will be deleted.",
    cn: "确认要删除数据集：{name}？这个操作将删除此数据集下的所有版本",
  },
  "dataset.query.name.placeholder": { cn: "数据集名称", en: "Dataset Name", },
  "dataset.detail.pager.total": { cn: "共 {total} 图像", en: "Total {total} Pictures", },
  "dataset.detail.keyword.label": { cn: "标签：", en: "Keywords: ", },
  "dataset.detail.randompage.label": { cn: "随机页", en: "Random Page", },
  "dataset.detail.assets.keywords.total": { cn: "共{total}个标签", en: "{total} keywords", },
  "dataset.asset.info": { cn: "数据信息", en: "Asset Info", },
  "dataset.asset.info.id": { cn: "标识", en: "ID", },
  "dataset.asset.info.size": { cn: "大小", en: "Size", },
  "dataset.asset.info.width": { cn: "宽", en: "Width", },
  "dataset.asset.info.height": { cn: "高", en: "Height", },
  "dataset.asset.info.channel": { cn: "通道", en: "Channels", },
  "dataset.asset.info.timestamp": { cn: "时间戳", en: "Timestamp", },
  "dataset.asset.info.keyword": { cn: "标签", en: "Keywords", },
  "dataset.asset.random": { cn: "随机图像", en: "Random Asset", },
  "dataset.asset.back": { cn: "上一个", en: "Previous Asset", },
  "dataset.asset.empty": { cn: "查询不到指定asset", en: "Invalid Asset", },
  "dataset.asset.annotation.hide": { cn: "隐藏所有标注", en: "Hide All", },
  "dataset.asset.annotation.show": { cn: "显示所有标注", en: "Show All", },
  "dataset.add.types.internal": { cn: "公共数据集", en: "Public Dataset", },
  "dataset.add.types.copy": { cn: "复制数据集", en: "Copy Dataset From Other Project", },
  "dataset.add.types.net": { cn: "网络导入", en: "Net Import", },
  "dataset.add.types.local": { cn: "本地导入", en: "Local Import", },
  "dataset.add.types.path": { cn: "路径导入", en: "Path Import", },
  "dataset.add.success.msg": { cn: "导入正在进行中", en: "Dataset Importing", },
  "dataset.add.form.name.label": { cn: "数据集名称", en: "Dataset Name", },
  "dataset.add.form.name.required": { cn: "请输入数据集名称", en: "Dataset Name", },
  "dataset.add.form.type.label": { cn: "添加类型", en: "Type", },
  "dataset.add.form.label.label": { cn: "标注", en: "Labeling Status", },
  "dataset.add.form.newkw.label": { cn: " ", en: " ", },
  "dataset.add.newkw.asname": { cn: "添加标签", en: "As Keyword", },
  "dataset.add.newkw.asalias": { cn: "添加为别名", en: "As Alias", },
  "dataset.add.newkw.ignore": { cn: "忽略此标签", en: "Ignore", },
  "dataset.add.form.newkw.link": { cn: "前往标签列表添加>>", en: "Go to the keyword list to add>>", },
  "dataset.add.form.newkw.tip": {
    cn: "当导入模型的标签内容不在当前的用户标签列表时，选择导入策略。",
    en: "Select an import policy when the tag of the imported dataset does not belong to the current list of user tags.",
  },
  "dataset.add.label_strategy.exclude": { cn: "不包含标注", en: "Only Assets", },
  "dataset.add.label_strategy.ignore": { cn: "只添加已有标签的标注", en: "Ignore unknown keywords and annotations", },
  "dataset.add.label_strategy.add": { cn: "添加所有标注", en: "Add Keywords", },
  "dataset.add.form.internal.label": { cn: "数据集", en: "Dataset", },
  "dataset.add.form.internal.required": { cn: "请选择公共数据集", en: "Please select public dataset", },
  "dataset.add.form.internal.placeholder": { cn: "请选择一个公共数据集", en: "Select A Public Dataset", },
  "dataset.add.form.net.label": { cn: "URL地址", en: "URL", },
  "dataset.add.form.net.tip": { cn: "请输入压缩文件的url地址", en: "Please input a url of zip file", },
  "dataset.add.form.path.label": { cn: "相对路径", en: "Relative Path", },
  "dataset.add.form.path.tip": {
    cn: "将数据文件夹存放到ymir工作空间目录下的ymir-sharing目录，如 /home/ymir/ymir-workspace/ymir-sharing/VOC2012, 输入基于ymir-sharing相对路径：VOC2012",
    en: "Save the data in 'ymir-sharing' under ymir workspace directory, such as /home/ymir/ymir-workspace/ymir-sharing/VOC2012, and input relative path base on ymir-sharing: VOC2012",
  },
  "dataset.add.form.path.placeholder": { cn: "请输入路径", en: "Please input path on server", },
  "dataset.add.form.upload.btn": { cn: "上传文件", en: "Upload", },
  "dataset.add.form.upload.tip": {
    cn: `1. 仅支持zip格式压缩包文件上传；{br}
      2. 局域网内压缩包大小 < 1G, 互联网建议 < 200MB；{br}
      3. 压缩包内图片格式要求为：图片格式为*.jpg、*.jpeg、*.png、*.bmp，格式不符的图片将不会导入，标注文件格式为Pascal VOC。{br}
      4. 压缩包文件内图片文件需放入images文件夹内，标注文件需放入annotations文件夹内，如以下示例：{sample}{br}
      5. 压缩包内文件结构如下：{br}{pic}`,
    en: `1. Only zip file allowed;{br} 
      2. Size < 1G;{br}
      3. Images format allowed *.jpg, *.jpeg, *.png, *.bmp, images with unmatched format can not be imported, annotations format supported pascal(*.xml){br}
      4. Sample: {sample}{br}
      5. zip structure: {br}{pic}`
  },
  "dataset.copy.form.dataset": { cn: "原数据集", en: "Original Dataset", },
  "dataset.copy.form.desc.label": { cn: '备注', en: 'Description', },
  "dataset.copy.success.msg": { cn: "数据集正在复制，请稍等", en: "Dataset copying", },
  'dataset.detail.action.fusion': { cn: '数据预处理', en: 'Data Pretreatment', },
  'dataset.detail.action.train': { cn: '训练模型', en: 'Train Model', },
  'dataset.detail.action.mining': { cn: '挖掘数据', en: 'Mining', },
  'dataset.detail.action.label': { cn: '数据标注', en: 'Label', },
  'dataset.import.public.include': { cn: '添加新标签', en: 'New Keywords', },
  'dataset.add.newkeyword.empty': { cn: '无新标签', en: 'None of new keywords', },
  'dataset.add.local.file.empty': { cn: '请上传本地文件', en: 'Please upload a zip file', },
  'dataset.samples.negative': { cn: '负样本', en: 'Negative Samples', },
  'dataset.train.form.samples': { cn: '标签占比', en: 'Keywords Ratio', },
  'dataset.detail.label.name': { cn: '数据集名称', en: 'Dataset Name', },
  'dataset.detail.label.assets': { cn: '图片数', en: 'Assets Count', },
  'dataset.detail.label.keywords': { cn: '标签', en: 'Keywords', },
  'dataset.add.form.copy.label': { cn: '源数据集', en: 'Original Dataset', },
  'dataset.add.form.copy.required': { cn: '源数据集不能为空', en: 'Original dataset is required', },
  'dataset.add.form.copy.placeholder': { cn: '请选择待复制的数据集版本', en: 'Select a dataset version for copy', },
  'dataset.add.validate.url.invalid': { cn: '不是合法的网络地址', en: 'Invalid url', },
  'dataset.fusion.validate.inputs': { cn: '请输入至少一项预处理条件', en: 'Please input at less one condition for pretreating', },
  'dataset.add.internal.newkeywords.label': { en: 'Add following keywords and related annotations:', cn: '添加以下标签及相应标注：'},
  'dataset.add.internal.ignore.all': { en: 'Ignore All', cn: '全部忽略'},
  'dataset.add.internal.ignorekeywords.label': { en: 'Ignore following keywords and related annotations:', cn: '忽略以下标签及相应标注：'},
  'dataset.add.internal.add.all': { en: 'Add All', cn: '全部添加'},
}

export default dataset

const model = {
  "model.detail.title": { en: "Model Detail", cn: "模型详情", },
  "model.diagnose": { en: "Model Diagnose", cn: "模型诊断", },
  "model.management": { en: "Model Management", cn: "模型管理", },
  "model.list": { en: "Model List", cn: "模型列表", },
  "model.column.name": { en: "Version", cn: "版本", },
  "model.column.source": { en: "Source", cn: "来源", },
  "model.column.target": { en: "Train Classes", cn: "训练目标", },
  "model.column.map": { en: "mAP", cn: "精度均值(mAP)", },
  "model.column.stage": { en: "Stage", cn: "阶段模型", },
  "model.column.create_time": { en: "Create Time", cn: "创建时间", },
  "model.column.action": { en: "Actions", cn: "操作", },
  "model.action.download": { en: "Download", cn: "下载", },
  "model.action.verify": { en: "Verify", cn: "验证", },
  "model.empty.label": { en: "Train A Model", cn: "训练出一个模型", },
  "model.empty.btn.label": { en: "Import Model", cn: '导入模型', },
  "model.import.label": { en: "Import Model", cn: "导入模型", },
  "model.query.name": { en: "Model Name", cn: "模型名称", },
  "model.action.del.confirm.content": { en: "Are you sure to remove this model version:{name}?", cn: "确认要删除模型版本：{name}？", },
  "model.action.hide.confirm.content": { en: "Are you sure to hide model versions: {name}?", cn: "确认要隐藏模型版本：{name}？", },
  "model.action.delgroup.confirm.content": { en: "Are you sure to remove this model:{name}, all of versions will be deleted.", cn: "确认要删除模型：{name}？这个操作将删除此模型下的所有版本", },
  "model.query.name.placeholder": { en: "Model Name", cn: "模型名称", },
  "model.pager.total.label": { en: "Total {total} items", cn: "共 {total} 项", },
  'model.detail.label.name': { en: 'Model Name', cn: '模型名称', },
  'model.detail.label.map': { en: 'mAP', cn: 'mAP值', },
  'model.detail.label.stage': { en: 'Stages', cn: '阶段模型', },
  'model.detail.label.source': { en: 'Source', cn: '模型来源', },
  'model.detail.label.image': { en: 'Train Image', cn: '训练镜像', },
  'model.detail.label.training_dataset': { en: 'Training Dataset', cn: '训练集', },
  'model.detail.label.test_dataset': { en: 'Validation Dataset', cn: '验证集', },
  'model.detail.label.train_type': { en: 'Train Type', cn: '训练类型', },
  'model.detail.label.train_goal': { en: 'Train Classes', cn: '训练目标', },
  'model.detail.label.framework': { en: 'Network', cn: '算法框架', },
  'model.detail.label.backbone': { en: 'Backbone', cn: '骨干网络结构', },
  'model.add.types.copy': { en: 'Share', cn: '复制模型', },
  'model.add.types.net': { en: 'Net', cn: '网络导入', },
  'model.add.types.local': { en: 'Local', cn: '本地导入', },
  'model.add.success': { en: 'Import model success!', cn: '导入模型成功！', },
  'model.add.form.name': { en: 'Name', cn: '名称', },
  'model.add.form.name.placeholder': { en: 'Model Name', cn: '请输入模型名称', },
  'model.add.form.type': { en: 'Import Type', cn: '导入类型', },
  'model.add.form.project': { en: 'Original Model', cn: '待复制模型', },
  'model.add.form.upload.btn': { en: 'Upload', cn: '上传文件', },
  'model.add.form.url': { en: 'Url', cn: '网络地址', },
  'model.add.form.url.tip': { en: 'Please input valid url for model', cn: '请输入正确的网络地址，指向模型文件', },
  'model.add.form.url.placeholder': { en: 'Please input model url from internet', cn: '请输入模型文件的网络地址', },
  'model.file.required': { en: 'Please upload model', cn: '请上传模型', },
  'model.add.form.upload.info': { en: `1. Only support model generating on YMIR; {br} 2. Size <= {max}M.`, cn: `1. 仅支持YMIR系统产生的模型；{br} 2. 上传文件应小于 {max}MB 。`, },
  'model.verify.upload.info': {cn: '支持jpg, png, bmp格式, 图片大小 < {size}M', en: 'Support *.jpg, *.png, *.bmp, size < {size}M'},
  'model.verify.confidence': { cn: '置信度', en: 'Confidence' },
  'model.verify.upload.label': { cn: '上传图片', en: 'Upload Image' },
  'model.verify.model.info.title': { cn: '模型信息', en: 'Model Info.' },
  'model.verify.model.param.title': { cn: '参数调整', en: 'Parameter Adjustment' },
  "model.verify.model.param.fold": { cn: '点击收起', en: 'Fold', },
  "model.verify.model.param.unfold": { cn: '点击展开', en: 'Unfold', },
  'model.verify.upload.tip': { cn: '模型验证需要较长时间，请耐心等待', en: 'Verification need more time, be patient...' },
  "model.diagnose.tab.analysis": { cn: '数据分析', en: 'Data Analysis', },
  "model.diagnose.tab.metrics": { cn: '衡量指标', en: 'Metrics', },
  "model.diagnose.tab.training": { cn: '训练过程', en: 'Training Fitting', },
  "model.diagnose.tab.visualization": { cn: '图像可视化', en: 'Image Visualization', },
  "model.diagnose.form.model": { cn: '诊断模型', en: 'Diagnosing Models', },
  'model.diagnose.form.testset': { cn: '测试集', en: 'Testing Datasets', },
  'model.diagnose.form.gt': { cn: '真值(Ground Truth)', en: 'Ground Truth', },
  'model.diagnose.form.confidence': { cn: '置信度', en: 'Confidence', },
  'model.diagnose.form.iou': { cn: '重叠度(IoU)', en: 'IoU(Intersection over Union)', },
  'model.diagnose.restart': { cn: '重新比对', en: 'Compare Again', },
  "model.action.diagnose.training.retry": { cn: '重新诊断', en: 'Retry', },

  "model.diagnose.analysis.column.name": { cn: "数据集", en: "Dataset", },
  "model.diagnose.analysis.validator.dataset.count": { cn: "最多选择{count}个数据集", en: "Select {count} datasets at most", },
  "model.diagnose.analysis.column.version": { cn: "版本", en: "Version", },
  "model.diagnose.analysis.column.size": { cn: "数据集大小", en: "Dataset Size", },
  "model.diagnose.analysis.column.box_count": { cn: "标注框总数", en: "Annotations Count", },
  "model.diagnose.analysis.column.average_labels": { cn: "标注框总数/总图片数", en: "Total Annotations/Total Assets", },
  "model.diagnose.analysis.column.overall": { cn: "已标注图片数/总图片数", en: "Labelled Assets/Total Assets", },
  "model.diagnose.analysis.param.title": { cn: "选择", en: "Select", },
  "model.diagnose.analysis.btn.start_diagnose": { cn: "开始诊断", en: "Diagnose", },
  "model.diagnose.analysis.btn.retry": { cn: "重新诊断", en: "Retry", },
  "model.diagnose.analysis.title.asset_bytes": { cn: "图像大小分布", en: "Image Size Distribution", },
  "model.diagnose.analysis.title.asset_hw_ratio": { cn: "图像高宽比分布", en: "Image Aspect Ratio Distribution", },
  "model.diagnose.analysis.title.asset_area": { cn: "图像分辨率分布", en: "Image Resolution Distribution", },
  "model.diagnose.analysis.title.asset_quality": { cn: "图像质量分布", en: "Image Quality Distribution", },
  "model.diagnose.analysis.title.anno_area_ratio": { cn: "标注框分辨率分布", en: "Annotation Box Resolution Distribution", },
  "model.diagnose.analysis.title.keyword_ratio": { cn: "标签占比", en: "Keywords Ratio", },
  "model.diagnose.analysis.bar.asset.tooltip": { cn: " 占比：{ratio} 数量：{amount} 张", en: " Ratio：{ratio} Amount：{amount}", },
  "model.diagnose.analysis.bar.anno.tooltip": { cn: " 占比：{ratio} 数量：{amount} 个", en: " Ratio：{ratio} Amount：{amount}", },
  "model.diagnose.label.model": { cn: "模型", en: "Models", },
  "model.diagnose.label.testing_dataset": { cn: "测试集", en: "Testing Datasets", },
  "model.diagnose.label.config": { cn: "推理配置", en: "Infer Configs", },
  "model.diagnose.stage.label": { cn: "设置模型Stage", en: "Set Recommended Stage", },
  "model.diagnose.metrics.precision.label": {cn: '精确率', en: 'Precision', },
  "model.diagnose.metrics.precision.average.label": {cn: '平均召回率', en: 'Average Recall', },
  "model.diagnose.metrics.precision.target.label": {cn: '{label}召回率 | 置信度', en: '{label} Recall | Confidence', },
  "model.diagnose.metrics.recall.label": {cn: '召回率', en: 'Recall', },
  "model.diagnose.metrics.recall.average.label": {cn: '平均精确率', en: 'Average Precision', },
  "model.diagnose.metrics.recall.target.label": {cn: '{label}精确率 | 置信度', en: '{label} Precision | Confidence', },
  "model.diagnose.metrics.confidence.average.label": {cn: '平均置信度', en: 'Average Confidence', },
  "model.diagnose.medtric.tabs.map": {cn: 'mAP', en: 'mAP', },
  "model.diagnose.medtric.tabs.curve": {cn: 'PR曲线', en: 'PR Curve', },
  "model.diagnose.medtric.tabs.rp": {cn: '指定召回率', en: 'Recall', },
  "model.diagnose.medtric.tabs.pr": {cn: '指定精确率', en: 'Precision', },
  'model.diagnose.metrics.ck.placeholder': {en: "Please select a custom Keyword", cn: "请选择一类自定义标签", },
  'model.diagnose.metrics.keyword.placeholder': {en: "Please select keywords", cn: "请选择标签", },
  'model.diagnose.metrics.view.label': {en: "View", cn: "视图", },
  'model.diagnose.metrics.dimension.label': {en: "Dimension:", cn: "维度：", },
  'model.diagnose.v.tasks.require': {en: "Please select infered testing dataset and config", cn: "请选择推理过的测试集及配置", },
  'model.diagnose.metrics.x.dataset': {en: "Testing Dataset", cn: "测试集", },
  'model.diagnose.metrics.x.keyword': {en: "Keyword", cn: "标签", },
}

export default model

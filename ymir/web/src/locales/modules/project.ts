const project = {
  "projects.title": { en: "Project List", cn: "项目列表", },
  "project.title": { en: "Project Detail", cn: "项目详情", },
  "project.add.title": { en: "Create Project", cn: "创建项目", },
  "project.interation.initmodel": { en: "Initial Model", cn: "初始模型准备", },
  "project.settings.title": { en: "Project Settings", cn: "设置项目", },
  "project.iterations.title": { en: "Project Iterations", cn: "项目迭代", },
  "project.action.edit": { en: "Edit Project", cn: "编辑项目", },
  "project.action.del": { en: "Delete Project", cn: "删除", },
  "project.new.label": { en: "Create Project", cn: "创建项目", },
  "project.query.name": { en: "Project Search", cn: "项目搜索", },
  "project.query.name.placeholder": { en: "Please input project name", cn: "请输入项目名称", },
  "project.list.total": { en: "Total {total} projects", cn: "共有项目{total}个", },
  "project.train_classes": { en: "Object Classes", cn: "训练目标", },
  "project.target.map": { en: "Target mAP", cn: "目标mAP", },
  "project.iteration.current": { en: "Iteration Stage", cn: "迭代进度", },
  "project.train_set": { en: "Training Set", cn: "训练集", },
  "project.test_set": { en: "Test Set", cn: "测试集", },
  "project.mining_set": { en: "Mining Set", cn: "挖掘集", },
  "project.iteration.number": { en: "Iteration Number", cn: "迭代轮次", },
  "project.content.desc": { en: "Description", cn: "描述", },
  "project.tab.set.title": { en: "Datasets", cn: "数据集", },
  "project.tab.model.title": { en: "Models", cn: "模型", },
  'project.add.form.name.invalid': { en: 'Project name allow letters, numbers, and underline, and start with letter', cn: '项目名称只允许大小写字母及下划线，且只能以字母开头', },
  'project.create.success': { en: 'Project Created!', cn: '项目创建成功', },
  'project.update.success': { en: 'Project Updated!', cn: '项目设置成功', },
  'project.add.form.name': { en: 'Project Name', cn: '项目名称', },
  'project.add.form.name.required': { en: 'Project name is required', cn: '项目名称为必填项', },
  'project.add.form.name.placeholder': { en: 'Please input your project name', cn: '请输入项目名称', },
  'project.add.form.type': { en: 'Training Type', cn: '训练类型', },
  'project.add.form.type.placeholder': { en: 'Please select training type', cn: '请选择训练类型', },
  'project.add.form.keyword.label': { en: 'Training Classes', cn: '训练目标', },
  'project.add.form.keyword.required': { en: 'Training classes is required', cn: '训练目标为必选项', },
  'project.add.form.keyword.placeholder': { en: 'Please select training classes', cn: '请输入训练目标', },
  'project.add.form.target': { en: 'Project Target', cn: '目标设置', },
  'project.add.form.target.map': { en: 'mAP', cn: 'mAP', },
  'project.add.form.target.map.placeholder': { en: 'Please input mAP as target', cn: '请输入目标mAP', },
  'project.add.form.target.iterations': { en: 'Iterations\' Number', cn: '迭代轮次', },
  'project.add.form.target.iterations.placeholder': { en: 'Please input your iterations number as target', cn: '请输入目标迭代轮次', },
  'project.add.form.target.dataset': { en: 'Dataset Assets', cn: '数据集大小', },
  'project.add.form.target.dataset.placeholder': { en: 'Please input your dataset assets number as target', cn: '请输入目标数据集大小', },
  'project.add.form.desc': { en: 'Description', cn: '备注', },
  'project.update.submit': { en: 'Update Project', cn: '设置项目', },
  'project.add.submit': { en: 'Create Project', cn: '创建项目', },
  'project.iteration.stage.datasets': { en: 'Dataset Settings', cn: '迭代数据准备', },
  'project.iteration.stage.model': { en: 'Select Model', cn: '迭代模型准备', },
  'project.iteration.stage.start': { en: 'Create Iteration', cn: '开启迭代', },
  'project.iteration.stage.ready': { en: 'Prepare Mining Dataset', cn: '准备挖掘数据', },
  'project.iteration.stage.mining': { en: 'Mining', cn: '数据挖掘', },
  'project.iteration.stage.label': { en: 'Label', cn: '数据标注', },
  'project.iteration.stage.merge': { en: 'Merge', cn: '更新训练集', },
  'project.iteration.stage.training': { en: 'Training', cn: '模型训练', },
  'project.iteration.stage.next': { en: 'Next Iteration', cn: '开启下一轮迭代', },
  'project.iteration.stage.ready.react': { en: 'Rehandle', cn: '重新处理', },
  'project.iteration.stage.mining.react': { en: 'Rehandle', cn: '重新挖掘', },
  'project.iteration.stage.label.react': { en: 'Rehandle', cn: '重新标注', },
  'project.iteration.stage.merge.react': { en: 'Rehandle', cn: '重新更新', },
  'project.iteration.stage.training.react': { en: 'Rehandle', cn: '重新训练', },
  'project.stage.state.pending': { en: 'Pending', cn: '未完成', },
  'project.iteration.settings.title': { en: 'Iterations Settings', cn: '迭代设置', },
  'project.add.form.training.set': { en: 'Training Dataset', cn: '训练集', },
  'project.add.form.test.set': { en: 'Test Dataset', cn: '测试集', },
  'project.add.form.mining.set': { en: 'Mining Dataset', cn: '挖掘集', },
  'project.add.form.mining.strategy': { en: 'Mining Strategy', cn: '挖掘策略', },
  'project.mining.strategy.block': { en: 'Chunk Mining', cn: '分块挖掘（在迭代中对挖掘集进行分块处理）', },
  'project.mining.strategy.unique': { en: 'Dedup Mining', cn: '去重挖掘（在迭代中会将之前迭代的挖掘数据排除出去）', },
  'project.mining.strategy.custom': { en: 'Customer Mining', cn: '自定义挖掘（在迭代中不对挖掘数据进行额外处理）', },
  'project.detail.info.iteration': { en: 'iterations: {current}/{target}', cn: '您当前处于项目迭代的{current}/{target}次迭代', },
  'project.iteration.initmodel': { en: 'Initial Model Setting', cn: '初始模型设置', },
}

export default project

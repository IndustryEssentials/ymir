const project = {
  "projects.title": { en: "Project List", cn: "项目列表", },
  "project.title": { en: "Project Detail", cn: "项目详情", },
  "project.summary": { en: "Project Summary", cn: "项目概览", },
  "project.add.title": { en: "Create Project", cn: "创建项目", },
  "project.settings.title": { en: "Project Settings", cn: "设置项目", },
  "project.iterations.title": { en: "Project Iterations", cn: "项目迭代", },
  "project.hidden.title": { en: "Hidden List", cn: "隐藏列表", },
  "project.action.edit": { en: "Edit Project", cn: "编辑项目", },
  "project.action.del": { en: "Delete Project", cn: "删除", },
  "project.new.label": { en: "Create Project", cn: "创建项目", },
  "project.query.name": { en: "Project Search", cn: "项目搜索", },
  "project.query.name.placeholder": { en: "Please input project name", cn: "请输入项目名称", },
  "project.list.total": { en: "Total {total} projects", cn: "共有项目{total}个", },
  "project.train_classes": { en: "Training Classes", cn: "训练类别", },
  "project.target.map": { en: "Target mAP", cn: "目标mAP", },
  "project.iteration.current": { en: "Iteration Stage", cn: "迭代进度", },
  "project.train_set": { en: "Training Set", cn: "训练集", },
  "project.test_set": { en: "Validation Set", cn: "验证集", },
  "project.mining_set": { en: "Mining Set", cn: "挖掘集", },
  "project.iteration.number": { en: "Iteration Number", cn: "迭代轮次", },
  "project.content.desc": { en: "Description", cn: "描述", },
  "project.tab.set.title": { en: "Datasets", cn: "数据集", },
  "project.tab.model.title": { en: "Models", cn: "模型", },
  'project.add.form.name.invalid': {
    en: 'Project name allow letters, numbers, and underline, and start with letter',
    cn: '项目名称只允许大小写字母及下划线，且只能以字母开头',
  },
  'project.create.success': { en: 'Project Created!', cn: '项目创建成功', },
  'project.update.success': { en: 'Project Updated!', cn: '项目设置成功', },
  'project.add.form.name': { en: 'Project Name', cn: '项目名称', },
  'project.add.form.name.required': { en: 'Project name is required', cn: '项目名称为必填项', },
  'project.add.form.name.placeholder': { en: 'Please input your project name', cn: '请输入项目名称', },
  'project.add.form.type': { en: 'Training Type', cn: '训练类型', },
  'project.add.form.keyword.required': { en: 'Training classes is required', cn: '训练目标为必选项', },
  'project.add.form.keyword.placeholder': {
    en: 'Please select training classes, or input new classes, separated by comma',
    cn: '请输入训练目标，可选择已有的或输入新标签，英文逗号分隔',
  },
  'project.add.form.keyword.tip': {
    en: 'The target tags used for training need to match the categories in the user\'s tag list. If the input tag does not exist in the current user\'s tag list, it will be prompted to add it to the list when creating the project.',
    cn: '用于训练的目标标签，需要和用户的标签列表里的类别一致，如果输入的标签在当前用户的标签列表中不存在，则会在创建项目时提示将其加入列表。',
  },
  'project.add.form.enableIteration': { en: 'Open A Semi-automated Iterative Process', cn: '开启半自动化迭代流程', },
  'project.add.form.enableIteration.tip': {
    en: 'To assist users to achieve iterative optimization of the model through a fixed process, recommended for novice users.',
    cn: '通过固定流程辅助用户实现模型的迭代优化，推荐新手用户选择。',
  },
  'project.add.form.testingset.required': { en: 'Testing dataset is required', cn: '测试集为必选项', },
  'project.add.form.testingset.tip': {
    en: 'Used to test the effect of the model in various data sets, note: the test set cannot be used for training.',
    cn: '用于测试模型在各类数据集的效果指标，注：测试集不可用于训练。',
  },
  'project.add.form.target': { en: 'Project Target', cn: '目标设置', },
  'project.add.form.target.map': { en: 'mAP', cn: 'mAP', },
  'project.add.form.target.map.placeholder': { en: 'Please input mAP as target', cn: '请输入目标mAP', },
  'project.add.form.target.iterations': { en: 'Iterations\' Number', cn: '迭代轮次', },
  'project.add.form.target.iterations.placeholder': { en: 'Please input your iterations number as target', cn: '请输入目标迭代轮次', },
  'project.add.form.target.dataset': { en: 'Training Assets', cn: '训练集大小', },
  'project.add.form.target.dataset.placeholder': { en: 'Please input your training dataset assets number as target', cn: '请输入目标训练集大小', },
  'project.add.form.desc': { en: 'Description', cn: '备注', },
  'project.add.submit': { en: 'Create Project', cn: '创建项目', },
  'project.iteration.stage.prepare': { en: 'Iterations Prepare', cn: '迭代准备中', },
  'project.iteration.stage.datasets': { en: 'Dataset Settings', cn: '迭代数据准备', },
  'project.iteration.stage.model': { en: 'Select Model', cn: '迭代模型准备', },
  'project.iteration.stage.start': { en: 'Create Iteration', cn: '开启迭代', },
  'project.iteration.stage.ready': { en: 'Prepare Mining Dataset', cn: '准备挖掘数据', },
  'project.iteration.stage.mining': { en: 'Mining', cn: '数据挖掘', },
  'project.iteration.stage.label': { en: 'Label', cn: '数据标注', },
  'project.iteration.stage.merge': { en: 'Merge', cn: '更新训练集', },
  'project.iteration.stage.training': { en: 'Training', cn: '模型训练', },
  'project.iteration.stage.next': { en: 'Next Iteration', cn: '开启下一轮迭代', },
  'project.iteration.stage.datasets.react': { en: 'Re-process', cn: '重新设置数据', },
  'project.iteration.stage.model.react': { en: 'Re-process', cn: '重新选择模型', },
  'project.iteration.stage.ready.react': { en: 'Re-process', cn: '重新处理', },
  'project.iteration.stage.mining.react': { en: 'Re-process', cn: '重新挖掘', },
  'project.iteration.stage.label.react': { en: 'Re-process', cn: '重新标注', },
  'project.iteration.stage.merge.react': { en: 'Re-process', cn: '重新更新', },
  'project.iteration.stage.training.react': { en: 'Re-process', cn: '重新训练', },
  'project.stage.state.pending': { en: 'Unfinished', cn: '未完成', },
  'project.stage.state.pending.current': { en: 'Pending', cn: '待完成', },
  'project.iteration.settings.title': { en: 'Iterations Settings', cn: '迭代设置', },
  'project.add.form.training.set': { en: 'Training Dataset', cn: '训练集', },
  'project.add.form.test.set': { en: 'Validation Dataset', cn: '验证集', },
  'project.add.form.testing.set': { en: 'Testing Dataset', cn: '测试集', },
  'project.add.form.mining.set': { en: 'Mining Dataset', cn: '挖掘集', },
  'project.add.form.mining.strategy': { en: 'Mining Strategy', cn: '挖掘策略', },
  'project.add.form.mining.chunksize': { en: 'Chunk Size', cn: '每块数据量大小', },
  'project.mining.strategy.0': { en: 'Chunk Mining', cn: '分块挖掘（在迭代中对挖掘集进行分块处理）', },
  'project.mining.strategy.1': { en: 'Dedup Mining', cn: '去重挖掘（在迭代中会将之前迭代的挖掘数据排除出去）', },
  'project.mining.strategy.2': { en: 'Customer Mining', cn: '自定义挖掘（在迭代中不对挖掘数据进行额外处理）', },
  'project.mining.strategy.0.label': { en: 'Exclude Chunked Dataset', cn: '排除已分块的数据集', },
  'project.mining.strategy.1.label': { en: 'Exclude Mining Result Dataset', cn: '排除已挖掘的数据集', },
  'project.mining.strategy.2.label': { en: 'Exclude Mining Result Dataset', cn: '排除已挖掘的数据集', },
  'project.detail.info.iteration': {
    en: 'you are on stage {stageLabel}, iterations: {current}',
    cn: '您当前处于项目迭代的{stageLabel}, 第 {current} 次迭代',
  },
  'project.iteration.initmodel': { en: 'Initial Model Setting', cn: '初始模型设置', },
  'iteration.round.label': { en: 'Round {round}', cn: '第 {round} 次', },
  'iteration.column.round': { en: 'Iteration Round', cn: '迭代轮次', },
  'iteration.column.premining': { en: 'Mining Data', cn: '待挖掘数据', },
  'iteration.column.mining': { en: 'Mining Result', cn: '挖掘结果', },
  'iteration.column.label': { en: 'Labelling Result', cn: '标注结果', },
  'iteration.column.merging': { en: 'Training Dataset', cn: '训练数据', },
  'iteration.column.training': { en: 'Model', cn: '训练结果|mAP', },
  'iteration.column.test': { en: 'Validation Dataset', cn: '验证集', },
  'project.detail.desc': { en: 'Description', cn: '描述', },
  'project.detail.datavolume': { en: 'Data Volume', cn: '数据量', },
  'project.detail.runningtasks': { en: 'Running Tasks', cn: '运行中任务', },
  'project.detail.totaltasks': { en: 'Total Tasks', cn: '总任务', },
  'project.target.dataset': { en: 'Training Dataset\'s Assets', cn: '目标训练集大小', },
  'project.initmodel.success.msg': { en: 'Initial model prepared', cn: '设置初始模型成功', },
  'project.tag.train': { en: 'Training Dataset', cn: '训练集', },
  'project.tag.test': { en: 'Validation Dataset {version}', cn: '验证集 {version}', },
  'project.tag.mining': { en: 'Mining Dataset {version}', cn: '挖掘集 {version}', },
  'project.tag.testing': { en: 'Testing Dataset', cn: '测试集', },
  'project.tag.model': { en: 'Initial Model {version}', cn: '初始模型 {version}', },
  'iteration.tag.round': { en: 'Round {round}', cn: '迭代{round}', },
  'project.del.confirm.content': {
    en: 'Remove all datasets and models in this project, confirm?',
    cn: '删除项目会将项目中的所有资源（数据集、模型）删除，请谨慎操作！',
  },
  'project.add.confirm.title': {
    en: 'Whether this new keywords will add to your KEYWORD LIST?',
    cn: '标签管理列表未查询到下列标签，是否要添加至标签列表',
  },
  'project.add.confirm.ok': { en: 'Add Keywords and Create Project', cn: '添加标签并创建项目', },
  'project.add.confirm.cancel': { en: 'Cancel Create Project', cn: '取消创建项目', },
  'project.empty.label': {
    en: 'You can manage datasets, train models, and create data iterations.',
    cn: '在项目中可以管理数据集、训练模型、迭代数据',
  },
  'project.new.example.label': { en: 'Create Example Project', cn: '创建示例项目', },
  'project.keywords.invalid': { en: 'Invalid training keywords', cn: '训练目标不合法', },
  'project.workspace.status.dirty': {
    en: 'Project is {dirtyLabel}, training is disabled, please check again. if it is persistence, contact to administrator.',
    cn: '项目当前状态为{dirtyLabel}，无法创建训练任务，请重新检查状态。若状态持续异常，请联系管理员。',
  },
  'project.workspace.status.clean': { en: 'Project is {cleanLabel}, Training is enabled.', cn: '项目当前状态为{cleanLabel}, 可以正常创建训练任务', },
}

export default project

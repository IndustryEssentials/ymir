const common = {
  'common.top.menu.logout': { cn: '退出', en: 'Logout', },
  'common.top.menu.user': { cn: '用户管理', en: 'User', },
  'common.top.menu.community': { cn: '开源社区', en: 'GitHub', },
  'common.top.menu.home': { cn: "主页", en: "Home", },
  'common.top.menu.task': { cn: "任务管理", en: "Task", },
  'common.top.menu.dataset': { cn: "数据集管理", en: "Dataset", },
  'common.top.menu.model': { cn: "模型管理", en: "Model", },
  'common.top.menu.data': { cn: "数据管理", en: "Data", },
  'common.top.menu.keyword': { cn: "标签管理", en: "Keyword", },
  'common.top.menu.configure': { cn: "系统配置", en: "Configure", },
  'common.top.menu.permission': { cn: "权限配置", en: "Permission", },
  'common.top.menu.resource': { cn: "资源配置", en: "Resource", },
  'common.top.menu.mirror': { cn: "我的镜像", en: "Mirror", },
  'common.top.menu.mirror.center': { cn: "公共资源", en: "Mirror Center", },
  'common.top.search.item.dataset': { cn: '包含 {searchValue} 的数据集', en: 'Dataset Name include: {searchValue}', },
  'common.top.search.item.model': { cn: '包含 {searchValue} 的模型', en: 'Model Name include: {searchValue}', },
  'common.top.search.item.task': { cn: '包含 {searchValue} 的任务', en: 'Task Name include: {searchValue}', },
  'common.top.search.placeholder': { cn: '任务、数据集、模型的名称', en: 'Task, Dataset or Model Name', },
  'common.history.node.title': { cn: '节点详情', en: 'Node Detail', },
  'common.history.task.mining': { cn: '挖掘', en: 'Mining', },
  'common.history.task.training': { cn: '训练', en: 'Training', },
  'common.history.task.filter': { cn: '筛选', en: 'Filter', },
  'common.history.task.label': { cn: '标注', en: 'Label', },
  'common.back': { cn: '返回>', en: 'Back>', },
  'common.fold': { cn: '收起', en: 'Fold', },
  'common.unfold': { cn: '展开', en: 'Unfold', },
  'common.editbox.action.edit': { cn: '编辑名称', en: 'Edit Name', }, 
  'common.editbox.name': { cn: '名称', en: 'Name', }, 
  'common.editbox.form.name.required': { cn: '要修改的名称不能为空', en: 'A new name is required', }, 
  'common.editbox.form.name.placeholder': { cn: '请输入新的名称', en: 'Please input a new name', }, 
  'common.guide.title': { cn: '模型优化操作指引', en: 'How to Optimize Model', },
  'common.guide.step1.title': { cn: '准备数据', en: 'Datasets', },
  'common.guide.step1.content': { cn: '进入数据集页面，导入或复制一个带标注的数据集。', en: 'Import trainset and testset on dataset page.', },
  'common.guide.step1.btn': { cn: '去导入', en: 'Import', },
  'common.guide..step2.title': { cn: '模型训练', en: 'Training', },
  'common.guide.step2.content': { cn: '创建训练任务，调整训练参数，生成一个初始模型。', en: 'Select a labelled dataset for creating a train task.', },
  'common.guide.step2.btn': { cn: '去训练', en: 'Train', },
  'common.guide..step3.title': { cn: '数据挖掘', en: 'Mining', },
  'common.guide.step3.content': { cn: '使用初始模型，在海量数据中挖掘出对模型优化最有利的数据。', en: 'Mine better data in unlabelled dataset.', },
  'common.guide.step3.btn': { cn: '去挖掘', en: 'Mining', },
  'common.guide..step4.title': { cn: '挖掘结果标注', en: 'Label', },
  'common.guide.step4.content': { cn: '针对挖掘出来的数据，进行标注，生成带标注的数据集。', en: 'Label mining data.', },
  'common.guide.step4.btn': { cn: '去标注', en: 'Label', },
  'common.guide.step5.title': { cn: '模型再训练', en: 'Train Again', },
  'common.guide.step5.content': { cn: '将标注后的结果和原数据集合并再训练，实现模型的优化。', en: 'Optimize model by training merging dataset of labelled and origin data.', },
  'common.guide.nevershow': { cn: '下次不再显示', en: 'Never show again', },
  'common.guide.action.label': {cn: '操作指引', en: 'Guide', },
  'common.qa.action.import': {cn: '导入{br}数据集', en: 'Import Dataset', },
  'common.qa.action.train': {cn: '训练{br}模型', en: 'Train Model', },
  'common.qa.action.guide': {cn: '操作{br}指引', en: 'Guide', },
  'common.empty.keywords': {cn: '无标签', en: 'None', },
  'common.modify': {cn: '修改', en: 'Modify', },
  'common.all': {cn: '全部', en: 'All', },
  'common.yes': {cn: '是', en: 'Yes', },
  'common.no': {cn: '否', en: 'No', },
  'common.hot': {cn: '最热', en: 'Hot', },
  'common.latest': {cn: '最新', en: 'Latest', },
  'common.uploader.format.error': {cn: '上传文件格式不正确', en: 'Invalid format', },
  'common.uploader.size.error': {cn: '文件大小最大不超过 {max}MB', en: 'File must smaller than {max}MB!', },
  'common.action': {cn: '操作', en: 'Action', },
  'common.state': {cn: '状态', en: 'State', },
}

export default common

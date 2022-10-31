const SysName = "YMIR"
const generateItem = (cn: string, en: string) => {
  const prefix = (title: string) => `${SysName} - ${title}`
  return {
    cn: prefix(cn),
    en: prefix(en),
  }
}
const routeTitle = {
  "portal.title": generateItem('首页', 'Home'),
  "login.title": generateItem('登录', 'Login'),
  "signup.title": generateItem('注册', 'Sign Up'),
  "modify_pwd.title": generateItem('修改密码', 'Modify Password'),
  "forget.title": generateItem('忘记密码', 'Forget Password'),
  "reset_pwd.title": generateItem('重置密码', 'Reset Password'),
  "datasets.title": generateItem('数据集列表', 'Dataset List'),
  "dataset.title": generateItem('数据集详情', 'Dataset Detail'),
  "dataset.add.title": generateItem('添加数据集', 'Add Dataset'),
  "dataset.analysis.title": generateItem('数据集分析', 'Dataset Analysis'),
  "dataset.copy.title": generateItem('数据集复制', 'Dataset Copy'),
  "assets.title": generateItem('数据列表', 'Asset List'),
  "asset.title": generateItem('数据详情', 'Asset Detail'),
  "models.title": generateItem('模型列表', 'Model List'),
  "model.title": generateItem('模型详情', 'Model Detail'),
  "model.diagnose.title": generateItem('模型诊断', 'Model Diagnose'),
  "model.verify.title": generateItem('模型验证', 'Model Verify'),
  "task.fusion.title": generateItem('挖掘数据准备', 'Data Pretreatment'),
  "task.merge.title": generateItem('数据合并', 'Data Merge'),
  "task.filter.title": generateItem('数据筛选', 'Data Filter'),
  "task.train.title": generateItem('模型训练', 'Model Training'),
  "task.mining.title": generateItem('数据挖掘', 'Dataset Mining'),
  "task.inference.title": generateItem('数据推理', 'Dataset Inference'),
  "task.label.title": generateItem('数据标注', 'Dataset Labeling'),
  "history.title": generateItem('历史树', 'History Tree'),
  "keywords.title": generateItem('类别管理', 'Classes'),
  "projects.title": generateItem('项目管理', 'Project'),
  "project.title": generateItem('项目详情', 'Project Detail'),
  "project.add.title": generateItem('项目设置', 'Project Settings'),
  "project.iteration.add.title": generateItem('迭代设置', 'Iteration Settings'),
  "project.iteration.title": generateItem('迭代详情', 'Project Iteration'),
  "user.title": generateItem('个人中心', 'User'),
}

export default routeTitle

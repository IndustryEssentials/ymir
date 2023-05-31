import config from '@/../package.json'

const SysName = config.displayName
type ItemType = { cn: string; en: string }
const generateItem = ({ cn, en }: ItemType) => {
  const prefix = (title: string) => `${SysName} - ${title}`
  return {
    cn: prefix(cn),
    en: prefix(en),
  }
}
const withPrefix = (titles: { [key: string]: ItemType }) => {
  const items = Object.keys(titles)
  return items.reduce((prev, curr) => {
    const item = titles[curr]
    return {
      ...prev,
      [curr]: generateItem(item),
    }
  }, {})
}
const routeTitle = withPrefix({
  'portal.title': { cn: '首页', en: 'Home' },
  'login.title': { cn: '登录', en: 'Login' },
  'signup.title': { cn: '注册', en: 'Sign Up' },
  'modify_pwd.title': { cn: '修改密码', en: 'Modify Password' },
  'forget.title': { cn: '忘记密码', en: 'Forget Password' },
  'reset_pwd.title': { cn: '重置密码', en: 'Reset Password' },
  'datasets.title': { cn: '数据集列表', en: 'Dataset List' },
  'dataset.title': { cn: '数据集详情', en: 'Dataset Detail' },
  'dataset.add.title': { cn: '添加数据集', en: 'Add Dataset' },
  'dataset.analysis.title': { cn: '数据集分析', en: 'Dataset Analysis' },
  'dataset.copy.title': { cn: '数据集复制', en: 'Dataset Copy' },
  'assets.title': { cn: '数据列表', en: 'Asset List' },
  'asset.title': { cn: '数据详情', en: 'Asset Detail' },
  'models.title': { cn: '模型列表', en: 'Model List' },
  'model.title': { cn: '模型详情', en: 'Model Detail' },
  'model.diagnose.title': { cn: '结果分析', en: 'Result Analysis' },
  'model.verify.title': { cn: '模型验证', en: 'Model Verify' },
  'task.fusion.title': { cn: '挖掘数据准备', en: 'Data Pretreatment' },
  'task.merge.title': { cn: '数据合并', en: 'Data Merge' },
  'task.filter.title': { cn: '数据筛选', en: 'Data Filter' },
  'task.train.title': { cn: '模型训练', en: 'Model Training' },
  'task.mining.title': { cn: '数据挖掘', en: 'Dataset Mining' },
  'task.inference.title': { cn: '数据推理', en: 'Dataset Inference' },
  'task.label.title': { cn: '数据标注', en: 'Dataset Labeling' },
  'history.title': { cn: '历史树', en: 'History Tree' },
  'keywords.title': { cn: '类别管理', en: 'Classes' },
  'projects.title': { cn: '项目管理', en: 'Project' },
  'project.title': { cn: '项目详情', en: 'Project Detail' },
  'project.add.title': { cn: '项目设置', en: 'Project Settings' },
  'project.iteration.add.title': { cn: '迭代设置', en: 'Iteration Settings' },
  'project.iteration.title': { cn: '迭代详情', en: 'Project Iteration' },
  'user.title': { cn: '个人中心', en: 'User' },
  'llmm.inference.title': { cn: '多模态大模型推理', en: 'LLMM Inference' },
})

export default routeTitle

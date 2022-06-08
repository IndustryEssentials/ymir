import { useState } from "react"
import { Menu, Layout } from "antd"
import { useHistory, useLocation } from "umi"
import t from '@/utils/t'
import { BarchartIcon, FlagIcon, GithubIcon } from '@/components/common/icons'

const { Sider } = Layout

const getItem = (label, key, icon, children, type = '') => ({
  key, icon, children, label, type,
})

const getGroupItem = (label, key, children) => getItem(label, key, undefined, children, 'group')

const LeftMenu = () => {
  const history = useHistory()
  const location = useLocation()
  const [defaultKeys, setDefaultKeys] = useState(null)
  console.log('location:', location)

  const items = [
    getGroupItem('项目管理', 'project', [
      getItem('项目概览', '/home/project/detail', <BarchartIcon />, ),
      getItem('数据集管理', '/home/project/dataset', <BarchartIcon />, ),
      getItem('模型管理', 'model', <BarchartIcon />, [
        getItem('模型列表', '/home/project/models'),
        getItem('模型训练', '/home/task/training'),
        getItem('模型诊断', '/home/project/diagnose'),
      ]),
    ]),
    getGroupItem('标签管理', 'keyword', [
      getItem('标签管理', '/home/keyword', <FlagIcon />, ),
    ]),
    getGroupItem('系统配置', 'settings', [
      getItem('镜像列表', '/home/image', <FlagIcon />, ),
      getItem('权限配置', '/home/permission', <FlagIcon />, ),
    ]),
    { type: 'divider' },
    getItem('个人中心', '/home/user', <FlagIcon />, ),
    getItem(<a target="_blank" href='https://github.com/IndustryEssentials/ymir'><GithubIcon /> {t('common.top.menu.community')}</a>, 'github', ),
    getItem('帮助中心', 'help', <FlagIcon />, ),
  ]

  const clickHandle = ({ key }) => {
    setDefaultKeys([key])
    history.push(key)
  }
  
  return items.length ? (
    <Sider style={{ background: '#fff' }}>
      <Menu items={items} mode='inline' inlineCollapsed={false} defaultOpenKeys={['model']} onClick={clickHandle} selectedKeys={defaultKeys}>

      </Menu>
    </Sider>
  ) : null
}

export default LeftMenu

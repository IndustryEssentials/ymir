import { FC, ReactNode, useEffect, useState } from 'react'
import { Menu, Layout, MenuProps, MenuItemProps } from 'antd'
import { useHistory, useLocation, withRouter } from 'umi'
import { useSelector } from 'react-redux'
import t from '@/utils/t'
import { getDeployUrl, getPublicImageUrl } from '@/constants/common'
import { isSuperAdmin } from '@/constants/user'
import {
  BarchartIcon,
  FlagIcon,
  GithubIcon,
  FileHistoryIcon,
  MymodelIcon,
  NavDatasetIcon,
  UserIcon,
  UserSettingsIcon,
  DiagnosisIcon,
  EditIcon,
  EyeOffIcon,
  TrainIcon,
  DeviceListIcon,
  DeviceSupportedIcon,
  MyAlgoIcon,
  StoreIcon,
  BarChart2LineIcon,
  ProjectIcon,
  VectorIcon,
  BookIcon,
} from '@/components/common/Icons'
import IterationIcon from '@/components/icon/Xiangmudiedai'
import type { IconProps } from './icons/IconProps'
type MenuItem = Required<MenuProps>['items'][number]
type Handler = Required<MenuProps>['onClick']

const { Sider } = Layout

const projectModule = /^.*\/project\/(\d+).*$/

const getItem = (label: ReactNode, key: string, Icon?: FC<IconProps>, children?: MenuItem[], type?: 'group'): MenuItem => ({
  key,
  icon: Icon ? <Icon size="20" fill="rgba(0, 0, 0, 0.6)" /> : null,
  label,
  children,
  type,
})

const getGroupItem = (label: string, key: string, children: MenuItem[]) => getItem(label, key, undefined, children, 'group')

function LeftMenu() {
  const { role } = useSelector<YStates.Root, YStates.UserState>((state) => state.user)
  const { projects } = useSelector<YStates.Root, YStates.ProjectState>((state) => state.project)
  const history = useHistory()
  const { pathname } = useLocation()
  const [defaultKeys, setDefaultKeys] = useState<string[]>()
  const [items, setItems] = useState<MenuItem[]>([])
  const [id, setId] = useState(0)
  const [project, setProject] = useState<YModels.Project>()

  useEffect(() => {
    setDefaultKeys([pathname])
    const id = pathname.replace(projectModule, '$1')
    setId(Number(id))
  }, [pathname])

  useEffect(() => {
    id && projects && setProject(projects[id] || {})
  }, [id, projects])

  useEffect(() => {
    const showProjectList= projectModule.test(pathname)
    setItems([
      getGroupItem(t('breadcrumbs.projects'), 'project', [
        getItem(t('projects.title'), `/home/project`, ProjectIcon),
        showProjectList
          ? getItem(project?.name, `project.summary`, VectorIcon, [
              getItem(t('project.summary'), `/home/project/${id}/detail`, BarchartIcon),
              project?.enableIteration ? getItem(t('project.iterations.title'), `/home/project/${id}/iterations`, IterationIcon) : null,
              getItem(t('dataset.list'), `/home/project/${id}/dataset`, NavDatasetIcon),
              getItem(t('breadcrumbs.dataset.analysis'), `/home/project/${id}/dataset/analysis`, BarChart2LineIcon),
              getItem(t('model.management'), `/home/project/${id}/model`, MymodelIcon),
              getItem(t('model.diagnose'), `/home/project/${id}/diagnose`, DiagnosisIcon),
              getItem(t('breadcrumbs.task.training'), `/home/project/${id}/train`, TrainIcon),
              getItem(t('common.hidden.list'), `/home/project/${id}/hidden`, EyeOffIcon),
              getItem(t('project.settings.title'), `/home/project/${id}/add`, EditIcon),
            ])
          : null,
      ]),
      getGroupItem(t('image.leftmenu.label'), 'public_image', [
        getItem(t('common.top.menu.image'), '/home/image', FileHistoryIcon),
        getPublicImageUrl() ? getItem(t('common.top.menu.public_image'), '/home/public_image', FileHistoryIcon) : null,
      ]),
      getGroupItem(t('breadcrumbs.keyword'), 'keyword', [getItem(t('breadcrumbs.keyword'), '/home/keyword', FlagIcon)]),
      getDeployUrl()
        ? getGroupItem(t('algo.label'), 'algo', [
            getItem(t('algo.public.label'), '/home/algo', StoreIcon),
            getItem(t('algo.mine.label'), '/home/algo/mine', MyAlgoIcon),
            getItem(t('algo.device.label'), '/home/algo/device', DeviceListIcon),
            getItem(t('algo.support.label'), '/home/algo/support', DeviceSupportedIcon),
          ])
        : null,
      { type: 'divider' },
      isSuperAdmin(role) ? getItem(t('common.top.menu.permission'), '/home/permission', UserSettingsIcon) : null,
      getItem(
        <a target="_blank" href="/docs/#/README.md">
          <BookIcon />
          <span style={{ display: 'inline-block', marginLeft: 10 }}>{t('common.menu.docs')}</span>
        </a>,
        'outer/docs',
      ),
      getItem(t('user.settings'), '/home/user', UserIcon),
      getItem(
        <a target="_blank" href="https://github.com/IndustryEssentials/ymir">
          <GithubIcon />
          <span style={{ display: 'inline-block', marginLeft: 10 }}>{t('common.top.menu.community')}</span>
        </a>,
        'outer/github',
      ),
    ])
  }, [id, project, role])

  const clickHandle: Handler = ({ key }) => {
    const outer = /^outer\//.test(key)
    if (!outer) {
      setDefaultKeys([key])
      history.push(key)
    }
  }

  return items.length ? (
    <Sider className="sidebar scrollbar">
      <Menu items={items} mode="inline" defaultOpenKeys={['project.summary']} onClick={clickHandle} selectedKeys={defaultKeys} />
    </Sider>
  ) : null
}
export default withRouter(LeftMenu)

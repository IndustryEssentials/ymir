import { Breadcrumb } from "antd"
import { Link, useHistory, useParams, useRouteMatch, } from "umi"
import { homeRoutes } from '@/config/routes'
import t from '@/utils/t'
import s from './common.less'

const { Item } = Breadcrumb

const getCrumbs = () => {
  return homeRoutes.map(({ path, breadcrumbLabel, pid, id }) => ({
    path, label: breadcrumbLabel, pid, id,
  }))
}

function getCrumbItems(path, crumbs) {
  const crumb = crumbs.find(crumb => crumb.path === path)
  if (!(crumb && crumb.id)) {
    return []
  }
  return loop(crumb.id, crumbs)
}

function loop(id = 1, crumbs) {
  const current = crumbs.find(crumb => crumb.id === id)
  if (current.pid > 0) {
    return [...loop(current.pid, crumbs), current]
  } else {
    return [current]
  }
}

function Breadcrumbs({ suffix = '', titles = {} }) {
  const { path } = useRouteMatch()
  const params = useParams() || {}
  const crumbs = getCrumbs()
  const crumbItems = getCrumbItems(path, crumbs)
  return <div className='breadcrumb'>
    <Breadcrumb className='breadcrumbContent' separator='/'>
      {crumbItems.map((crumb, index) => {
        const last = index === crumbItems.length - 1
        const link = crumb.path.replace(/:([^\/]+)/g, (str, key) => {
          return params[key] ? params[key] : ''
        })
        const label = titles[index] ? titles[index] : t(crumb.label)
        return <Item key={crumb.path}>
          {last ? <span>{label} {suffix}</span> : <Link to={link}>{label}</Link>}
        </Item>
      })}
    </Breadcrumb>
  </div>
}

export default Breadcrumbs

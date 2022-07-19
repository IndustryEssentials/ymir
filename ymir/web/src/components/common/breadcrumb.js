import { useEffect } from "react"
import { Breadcrumb } from "antd"
import { Link, useHistory, useParams, useRouteMatch, useSelector } from "umi"
import { homeRoutes } from '@/config/routes'
import t from '@/utils/t'
import useFetch from '@/hooks/useFetch'
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
  const [project, getProject] = useFetch('project/getProject', {})
  const crumbs = getCrumbs()
  const crumbItems = getCrumbItems(path, crumbs)

  useEffect(() => {
    setTimeout(() => {
      if (crumbItems.some(crumb => crumb.id === 25) && params.id) {
        getProject({ id: params.id })
      }
    }, 500)
  }, [params.id])

  const getLabel = (crumb, customTitle) => {
    return (crumb.id === 25 ? project.name : customTitle) || t(crumb.label)
  }
  return <div className='breadcrumb'>
    <Breadcrumb className='breadcrumbContent' separator='/'>
      {crumbItems.map((crumb, index) => {
        const last = index === crumbItems.length - 1
        const link = crumb.path.replace(/:([^\/]+)/g, (str, key) => {
          return params[key] ? params[key] : ''
        })
        const label = getLabel(crumb, titles[index])
        return <Item key={crumb.path}>
          {last ? <span>{label} {suffix}</span> : <Link to={link}>{label}</Link>}
        </Item>
      })}
    </Breadcrumb>
  </div>
}

export default Breadcrumbs

import React, { useCallback, useEffect, useState } from "react"
import { Card } from "antd"
import { useLocation, useParams } from "umi"

import useFetch from '@/hooks/useFetch'
import Breadcrumbs from "@/components/common/breadcrumb"
import Detail from './detail'
import NoIterationDetail from "./noIterationDetail"

import s from "../detail.less"

const ListHOC = (Module) => {

  function List() {
    const location = useLocation()
    const { id } = useParams()
    const [iterations, getIterations] = useFetch('iteration/getIterations', [])
    const [groups, setGroups] = useState([])
    const [project, getProject] = useFetch('project/getProject', {})

    useEffect(() => {
      id && getProject({ id, force: true })
      id && getIterations({ id })
    }, [id])

    useEffect(() => {
      const gids = location.hash.replace(/^#/, '')
      if (gids) {
        setGroups(gids.split(','))
      }
    }, [location.hash])

    const fresh = useCallback(() => {
      getProject({ id, force: true })
    }, [id])

    return (
      <div className={s.projectDetail}>
        <Breadcrumbs />
        <div className={s.header}>
          {project.enableIteration ? <Detail project={project} iterations={iterations} fresh={fresh} /> : <NoIterationDetail project={project} />}
        </div>
        <Card className='noShadow'
          style={{ margin: '10px -20px 0', background: 'transparent' }}
          bodyStyle={{ padding: '0 20px' }}
        >
          <Module pid={id} project={project} groups={groups} iterations={iterations} />
        </Card>
      </div>
    )
  }
  return List
}

export default ListHOC

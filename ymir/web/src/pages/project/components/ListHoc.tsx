import { FC, useEffect, useState } from 'react'
import { Card } from 'antd'
import { useLocation, useParams, useSelector } from 'umi'

import useRequest from '@/hooks/useRequest'
import Breadcrumbs from '@/components/common/breadcrumb'

import s from '../detail.less'
import { Iteration, Project } from '@/constants'

type ListType = (m: ModuleType) => FC
export type ModuleType = FC<{
  pid: number
  project?: Project
  iterations?: Iteration[]
  groups?: number[]
}>

const ListHOC: ListType = (Module) => {
  function List() {
    const location = useLocation()
    const params = useParams<{ id: string }>()
    const id = Number(params.id)
    const [groups, setGroups] = useState<number[]>([])
    const project = useSelector(({ project }) => project.projects[id])
    const { run: getProject } = useRequest<null, [{ id: number; force?: boolean }]>('project/getProject', {
      loading: false,
    })
    const { data: iterations, run: getIterations } = useRequest<Iteration[], [{ id: number }]>('iteration/getIterations', {
      loading: false,
    })

    useEffect(() => {
      id && getProject({ id })
      id && getIterations({ id })
    }, [id])

    useEffect(() => {
      const gids = location.hash.replace(/^#/, '')
      if (gids) {
        setGroups(gids.split(',').map(Number))
      }
    }, [location.hash])

    useEffect(() => {
      getProject({ id, force: true })
    }, [groups])

    return (
      <div className={s.projectDetail}>
        <Breadcrumbs />
        <Card className="noShadow" style={{ margin: '10px -20px 0', background: 'transparent' }} bodyStyle={{ padding: '0 20px' }}>
          <Module pid={id} project={project} groups={groups} iterations={iterations} />
        </Card>
      </div>
    )
  }
  return List
}

export default ListHOC

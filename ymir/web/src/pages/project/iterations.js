import React, { useCallback, useEffect, useState } from "react"
import { useParams } from "umi"

import t from "@/utils/t"
import useFetch from '@/hooks/useFetch'
import Breadcrumbs from "@/components/common/breadcrumb"
import Iteration from './iterations/iteration'
import Prepare from "./iterations/prepare"
import Current from './iterations/detail'
import List from "./iterations/list"

import s from "./iterations/index.less"
import { CardTabs } from "@/components/tabs/cardTabs"
import ProjectDetail from "./components/detail"

function Iterations() {
  const { id } = useParams()
  const [iterations, getIterations] = useFetch('iteration/getIterations', [])
  const [project, getProject, setProject] = useFetch('project/getProject', {})

  const tabs = [
    { tab: t('project.iteration.tabs.current'), key: 'current', content: <Current project={project} /> },
    { tab: t('project.iteration.tabs.list'), key: 'list', content: <List project={project} /> },
  ]

  useEffect(() => {
    id && getProject({ id, force: true })
    id && getIterations({ id })
  }, [id])

  const fresh = useCallback(project => {
    if (project) {
      setProject(project)
    } else {
      getProject({ id, force: true })
    }
  }, [id])

  return (
    <div className={s.iterations}>
      <Breadcrumbs />
      <div className={s.header}>
        <ProjectDetail project={project} />
        {project.round > 0 ?
          <Iteration project={project} iterations={iterations} fresh={fresh} /> : <Prepare project={project} iterations={iterations} fresh={fresh} />}
      </div>
      <CardTabs data={tabs} />
    </div>
  )
}


export default Iterations

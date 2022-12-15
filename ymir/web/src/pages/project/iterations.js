import React, { useCallback, useEffect, useState } from 'react'
import { useParams, useSelector } from 'umi'

import t from '@/utils/t'
import useFetch from '@/hooks/useFetch'
import useRequest from '@/hooks/useRequest'
import Breadcrumbs from '@/components/common/breadcrumb'
import Iteration from './iterations/iteration'
import Prepare from './iterations/prepare'
import Current from './iterations/detail'
import List from './iterations/list'

import s from './iterations/index.less'
import { CardTabs } from '@/components/tabs/cardTabs'
import ProjectDetail from './components/detail'

function Iterations() {
  const { id } = useParams()
  const project = useSelector(({ project }) => project.projects[id] || {})
  const { run: getProject } = useRequest('project/getProject', {
    loading: false,
  })

  const tabs = [
    { tab: t('project.iteration.tabs.current'), key: 'current', content: <Current project={project} /> },
    { tab: t('project.iteration.tabs.list'), key: 'list', content: <List project={project} /> },
  ]

  useEffect(() => {
    id && getProject({ id })
  }, [id])

  const fresh = useCallback(() => {
    getProject({ id, force: true })
  }, [id])

  return (
    <div className={s.iterations}>
      <Breadcrumbs />
      <div className={s.header}>
        <ProjectDetail project={project} />
        {project.round > 0 ? <Iteration project={project} fresh={fresh} /> : <Prepare project={project} fresh={fresh} />}
      </div>
      <CardTabs data={tabs} />
    </div>
  )
}

export default Iterations

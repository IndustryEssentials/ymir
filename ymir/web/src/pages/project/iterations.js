import React, { useCallback, useEffect } from 'react'
import { Alert } from 'antd'
import { useParams, useSelector } from 'umi'

import t from '@/utils/t'
import useRequest from '@/hooks/useRequest'
import Breadcrumbs from '@/components/common/breadcrumb'
import Iteration from './iterations/iteration'
import Prepare from './iterations/prepare'
import Current from './iterations/detail'
import List from './iterations/list'

import s from './iterations/index.less'
import CardTabs from '@/components/tabs/CardTabs'
import ProjectDetail from './components/Detail'
import ActionPanel from './components/IterationTopActionPanel'

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
        <Alert message={t('iteration.training.target.warning')} showIcon type='warning' style={{ marginBottom: 10 }} />
        <ProjectDetail project={project} extra={<ActionPanel fold={project.round > 0} />} />
        {project.round > 0 ? <Iteration project={project} fresh={fresh} /> : <Prepare project={project} fresh={fresh} />}
      </div>
      <CardTabs data={tabs} />
    </div>
  )
}

export default Iterations

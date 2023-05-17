import React, { useEffect, useState } from 'react'
import { Card } from 'antd'
import { useLocation, useParams, useHistory } from 'umi'

import t from '@/utils/t'
import useFetch from '@/hooks/useFetch'

import Breadcrumbs from '@/components/common/breadcrumb'
import Training from './diagnose/training'
import Predictions from './diagnose/Predictions'

import s from './detail.less'
const TabsKey = ['infer_datasets', 'training']
const tab = (key) => ({ tab: `model.diagnose.tab.${key}`, key })
const tabs = TabsKey.map((key) => tab(key))

const content = {
  [TabsKey[0]]: Predictions,
  [TabsKey[1]]: Training,
}

const DynamicContent = ({ active, id, project }) => {
  const Content = content[active]
  return id && active ? <Content pid={id} project={project} /> : null
}

function Diagnose() {
  const history = useHistory()
  const location = useLocation()
  const tabKey = location.hash.replace(/^#/, '')
  const active = tabKey || TabsKey[0]
  const { id } = useParams()
  const [project, fetchProject] = useFetch('project/getProject')

  useEffect(() => id && fetchProject({ id }), [id])

  function tabChange(key) {
    history.push(`#${key}`)
  }

  return (
    <div className={s.projectDetail}>
      <Breadcrumbs />
      <Card
        tabList={tabs.map((tab) => ({ ...tab, tab: t(tab.tab) }))}
        activeTabKey={active}
        onTabChange={tabChange}
        className="noShadow"
        headStyle={{ background: '#fff', marginBottom: '10px' }}
        bodyStyle={{ padding: '0 20px' }}
      >
        <DynamicContent active={active} id={id} project={project} />
      </Card>
    </div>
  )
}

export default Diagnose

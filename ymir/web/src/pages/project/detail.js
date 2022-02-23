import React, { useState } from "react"
import { Card } from "antd"
import { useParams } from "umi"

import t from "@/utils/t"
import Breadcrumbs from "@/components/common/breadcrumb"
import Interation from './components/interation'
import Datasets from './components/datasets'
import Models from './components/models'

import styles from "./detail.less"

const tabsTitle = [
  { tab: t('project.tab.set.title'), key: 'set', },
  { tab: t('project.tab.model.title'), key: 'model', },
]

function ProjectDetail() {
  const { id } = useParams()
  const [active, setActive] = useState(tabsTitle[0].key)
  const content = {
    'set': <Datasets />,
    'model': <Models />
  }

  console.log('project detail id: ', id)

  return (
    <div className={styles.projectDetail}>
      <Breadcrumbs />
      <Interation id={id} />
      <Card tabList={tabsTitle} activeTabKey={active} onTabChange={(key) => setActive(key)} 
        style={{ margin: '0 -5vw', background: 'transparent'}}
        headStyle={{ padding: '0 5vw', background: '#fff', marginBottom: '20px'}}
        bodyStyle={{ padding: '0 5vw'}}>
        {content[active]}
      </Card>
    </div>
  )
}

export default ProjectDetail

import React, { useEffect, useState } from "react"
import { Card } from "antd"
import { useLocation, useParams } from "umi"

import t from "@/utils/t"
import Breadcrumbs from "@/components/common/breadcrumb"
import Interation from './components/interation'
import Datasets from '@/components/dataset/list'
import Models from '@/components/model/list'

import styles from "./detail.less"

const tabsTitle = [
  { tab: t('project.tab.set.title'), key: 'set', },
  { tab: t('project.tab.model.title'), key: 'model', },
]

function ProjectDetail() {
  const location = useLocation()
  const { id } = useParams()
  const [active, setActive] = useState(tabsTitle[0].key)
  const content = {
    'set': <Datasets pid={id} />,
    'model': <Models pid={id} />
  }
  
  useEffect(() => {
    const locationHash = location.hash.replace(/^#/, '')
    if (locationHash) {
      setActive(locationHash)
    }
  }, [location.hash])

  return (
    <div className={styles.projectDetail}>
      <Breadcrumbs />
      <Interation id={id} />
      <Card tabList={tabsTitle} activeTabKey={active} onTabChange={(key) => setActive(key)} 
        style={{ margin: '-20px -5vw 0', background: 'transparent'}}
        headStyle={{ padding: '0 5vw', background: '#fff', marginBottom: '20px'}}
        bodyStyle={{ padding: '0 5vw'}}>
        {content[active]}
      </Card>
    </div>
  )
}

export default ProjectDetail

import { Card, Col, Row } from "antd"
import { useEffect, useState } from "react"
import { connect } from 'dva'

import t from '@/utils/t'
import Title from "./components/boxTitle"
import QuickCreate from "./components/quickCreate"
import { AddtaskIcon, MydatasetIcon } from '@/components/common/icons'
import { cardHead, cardBody } from "./components/styles"
import styles from './index.less'

import { Lists } from '@/components/project/list'

const MyProject = ({ count = 6, getProjects }) => {

  const [projects, setProjects] = useState([])

  useEffect(() => {
    getData()
  }, [])

  async function getData() {
    const result = await getProjects(count)
    if (result) {
      setProjects(result.items)
    }
  }

  return (
    <Card id='mydataset' className={`${styles.box} ${styles.myProject}`} bordered={false}
      headStyle={cardHead} bodyStyle={cardBody}
      title={<Title title={<><MydatasetIcon className={styles.headIcon} /><span className={styles.headTitle}>{t('portal.project.my.title')}</span></>} link='/home/project'>
      </Title>}
    >
      <div className={styles.rowContainer}>
        <Row gutter={10} wrap='nowrap'>
          <Col span={24}><QuickCreate style={{ height: 42 }}
            icon={<AddtaskIcon style={{ fontSize: 20, color: '#36cbcb' }} />}
            label={t('portal.action.new.project')}
            link={'/home/project/add'}
          /></Col>
        </Row>
        <Row gutter={10} wrap='nowrap'>
          <Col span={24}>
            {projects.length ? <Lists projects={projects}/> : null}
          </Col>
        </Row>
      </div>
    </Card>
  )
}

const actions = (dispatch) => {
  return {
    getProjects: (limit) => {
      return dispatch({
        type: 'project/getProjects',
        payload: { limit },
      })
    },
  }
}

export default connect(null, actions)(MyProject)

import { Card, Col, message, Row } from "antd"
import { useEffect, useState } from "react"
import { connect } from 'dva'

import t from '@/utils/t'
import Title from "./components/boxTitle"
import { AddtaskIcon, MydatasetIcon } from '@/components/common/icons'
import { cardHead, cardBody } from "./components/styles"
import styles from './index.less'

import { Lists } from '@/components/project/list'
import { Link } from "umi"

const MyProject = ({ count = 6, ...func }) => {

  const [projects, setProjects] = useState([])

  useEffect(() => {
    getData()
  }, [])

  async function getData() {
    const result = await func.getProjects(count)
    if (result) {
      setProjects(result.items)
    }
  }

  const addExample = async () => {
    const result = await func.addExampleProject()
    if (result) {
      message.success(t('project.create.success'))
      getData()
    }
  }

  return (
    <Card id='mydataset' className={`${styles.box} ${styles.myProject}`} bordered={false}
      headStyle={cardHead} bodyStyle={cardBody}
      title={<Title title={<><MydatasetIcon className={styles.headIcon} /><span className={styles.headTitle}>{t('portal.project.my.title')}</span></>} link='/home/project'>
      </Title>}
    >
      <div className={styles.rowContainer}>
        <div className={styles.addBtn}>
          <Link className={styles.emptyBoxAction} to={'/home/project/add'}>
            <AddtaskIcon style={{ fontSize: 20, color: '#36cbcb' }} />
            <span style={{ color: '#36cbcb', fontSize: 16, marginLeft: 10 }}>{t('portal.action.new.project')}</span>
          </Link>
        </div>
        {projects.length ? <Lists projects={projects} /> : 
        <div className={styles.addBtn} style={{ marginTop: 20 }}>
          <Link className={styles.emptyBoxAction} to={''} onClick={() => addExample()}>
            <AddtaskIcon style={{ fontSize: 20, color: '#36cbcb' }} />
            <span style={{ color: '#36cbcb', fontSize: 16, marginLeft: 10 }}>{t('project.new.example.label')}</span>
          </Link>
        </div>
        }
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
    addExampleProject() {
      return dispatch({
        type: 'project/addExampleProject',
      })
    },
  }
}

export default connect(null, actions)(MyProject)

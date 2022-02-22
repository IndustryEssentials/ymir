import React, { useEffect, useRef, useState } from "react"
import { Descriptions, List, Space, Tag, Card, Button, Row, Col } from "antd"
import { connect } from 'dva'
import { useParams, Link, useHistory } from "umi"

import t from "@/utils/t"
import Breadcrumbs from "@/components/common/breadcrumb"
import { ROLES } from '@/constants/user'
import Del from './components/del'
import styles from "./detail.less"
import { EditIcon, VectorIcon, TrainIcon, } from '@/components/common/icons'
// import ProjectsLink from "./components/projectsLink"

const { Item } = Descriptions

function ProjectDetail({ role, getProject }) {
  const { id } = useParams()
  const history = useHistory()
  const [project, setProject] = useState({ id })
  const shareModalRef = useRef(null)
  const linkModalRef = useRef(null)
  const delRef = useRef(null)

  useEffect(async () => {
    fetchProject()
  }, [id])

  async function fetchProject() {
    const result = await getProject(id)
    if (result) {
      setProject(result)
    }
  }

  const del = () => {
    delRef.current.del(id, project.name)
  }

  const delOk = () => {
    history.push('/home/project')
  }

  function renderTitle() {
    return (
      <Row>
        <Col flex={1}>{project.name} { isAdmin() ? <Link to={`/home/project/add/${id}`}><EditIcon /></Link> : null }</Col>
        <Col><Button type='link' onClick={() => history.goBack()}>{t('common.back')}&gt;</Button></Col>
      </Row>
    )
  }

  return (
    <div className={styles.projectDetail}>
      <Breadcrumbs />
      <Card title={renderTitle()}>
        <div className={styles.infoTable} >
        <Descriptions bordered column={2} labelStyle={{ width: '200px'}} title={t('project.detail.title')}>
          <Item label={t('project.detail.label.name')}>{project.name}</Item>
          <Item label={t('project.detail.label.share')}>{project.is_shared ? t('common.yes') : t('common.no')}</Item>
         
        </Descriptions>
        </div>
      </Card>
      <Del ref={delRef} ok={delOk} />
    </div>
  )
}


const props = (state) => {
  return {
    role: state.user.role,
  }
}

const actions = (dispatch) => {
  return {
    getProject(id) {
      return dispatch({
        type: 'project/getProject',
        payload: id,
      })
    },
  }
}

export default connect(props, actions)(ProjectDetail)

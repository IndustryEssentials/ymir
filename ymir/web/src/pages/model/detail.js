import React, { useEffect, useState } from "react"
import { Descriptions, List, Space, Tag, Card, Button, Row, Col } from "antd"
import { connect } from 'dva'
import { useParams, Link, useHistory } from "umi"

import t from "@/utils/t"
import Breadcrumbs from "@/components/common/breadcrumb"
import TaskDetail from "@/components/task/detail"
import TripleRates from "@/components/form/tripleRates"
import styles from "./detail.less"
import { percent } from "../../utils/number"
import TaskProgress from "@/components/task/progress"

const { Item } = Descriptions

function ModelDetail({ getModel }) {
  const { id } = useParams()
  const history = useHistory()
  const [model, setModel] = useState({ id })

  useEffect(async () => {
    const result = await getModel(id)
    if (result) {
      console.log('model: ', result)
      setModel(result)
    }
  }, [id])

  function renderTitle() {
    return (
      <Row>
        <Col flex={1}>{model.name}</Col>
        <Col><Button type='link' onClick={() => history.goBack()}>{t('common.back')}&gt;</Button></Col>
      </Row>
    )
  }

  return (
    <div className={styles.modelDetail}>
      <Breadcrumbs suffix={model.name} />
      <Card title={renderTitle()}>
        {/* {<h3 className={styles.title}>{t("dataset.detail.title")}</h3> } */}
        <Descriptions bordered column={2} labelStyle={{ width: '200px' }} title={t('model.detail.title')} className={styles.infoTable}>
          <Item label={t('model.detail.label.name')}>{model.name}</Item>
          <Item label={t('model.detail.label.id')}>{model.id}</Item>
          <Item label={t('model.detail.label.map')}><span title={model.map}>{percent(model.map)}</span></Item>
        </Descriptions>
        <TaskProgress state={model.state} task={model.task} duration={''} progress={model?.task?.percent} />
        <TaskDetail task={model.task}></TaskDetail>
        <Space style={{ width: "100%", justifyContent: "flex-end" }}>
          <Button><Link target="_blank" to={model.url}>{t('model.action.download')}</Link></Button>
          <Button onClick={() => history.push(`/home/model/verify/${model.id}`)}>{t('model.action.verify')}</Button>
          <Button type='primary' onClick={() => history.push(`/home/task/mining/${model.project_id}?mid=${model.id}`)}>{t('dataset.action.mining')}</Button>
          <Button type='primary' onClick={() => history.push(`/home/task/train/${model.project_id}?mid=${model.id}`)}>{t('dataset.action.train')}</Button>
        </Space>
      </Card>
    </div>
  )
}


const props = (state) => {
  return {
    logined: state.user.logined,
  }
}

const actions = (dispatch) => {
  return {
    getModel(payload) {
      return dispatch({
        type: 'model/getModel',
        payload,
      })
    },
  }
}

export default connect(props, actions)(ModelDetail)

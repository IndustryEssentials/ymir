import React, { useEffect, useState } from "react"
import { Descriptions, List, Space, Tag, Card, Button, Row, Col } from "antd"
import { connect } from 'dva'
import { useParams, Link, useHistory } from "umi"

import t from "@/utils/t"
import Breadcrumbs from "@/components/common/breadcrumb"
import TaskDetail from "@/components/task/detail"
import styles from "./detail.less"
import { percent } from "../../utils/number"
import TaskProgress from "@/components/task/progress"
import Error from "@/components/task/error"

const { Item } = Descriptions

function ModelDetail({ modelCache, getModel }) {
  const { mid: id } = useParams()
  const history = useHistory()
  const [model, setModel] = useState({ id })

  useEffect(async () => {
    id && fetchModel(true)
  }, [id])

  useEffect(() => {
    console.log('modelCache:', modelCache)
    if (modelCache[id]?.needReload) {
      fetchModel(true)
    } else {
      modelCache[id] && setModel(modelCache[id])
    }
  }, [modelCache])

  async function fetchModel(force) {
    await getModel(id, force)
  }

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
        <Descriptions bordered column={2} labelStyle={{ width: '200px' }} title={t('model.detail.title')} className={styles.infoTable}>
          <Item label={t('model.detail.label.name')}>{model.name} {model.versionName}</Item>
          <Item label={t('model.detail.label.map')}><span title={model.map}>{percent(model.map)}</span></Item>
        </Descriptions>
        <TaskProgress state={model.state} result={model} task={model.task} duration={model.durationLabel} progress={model.progress} fresh={() => fetchModel(true)} />
        { model?.task?.error_code ? <Error code={model.task?.error_code} msg={model.task?.error_message} /> : null }
        <TaskDetail task={model.task}></TaskDetail>
        <Space style={{ width: "100%", justifyContent: "flex-end" }}>
          {model.url ? <Button><Link target="_blank" to={model.url}>{t('model.action.download')}</Link></Button> : null}
          <Button onClick={() => history.push(`/home/project/${model.projectId}/model/${model.id}/verify`)}>{t('model.action.verify')}</Button>
          <Button type='primary' onClick={() => history.push(`/home/task/mining/${model.projectId}?mid=${id}`)}>{t('dataset.action.mining')}</Button>
          <Button type='primary' onClick={() => history.push(`/home/task/inference/${model.projectId}?mid=${id}`)}>{t('dataset.action.inference')}</Button>
          <Button type='primary' onClick={() => history.push(`/home/task/train/${model.projectId}?mid=${id}`)}>{t('dataset.action.train')}</Button>
        </Space>
      </Card>
    </div>
  )
}

const props = (state) => {
  return {
    modelCache: state.model.model,
  }
}

const actions = (dispatch) => {
  return {
    getModel(id, force) {
      return dispatch({
        type: 'model/getModel',
        payload: { id, force },
      })
    },
  }
}

export default connect(props, actions)(ModelDetail)

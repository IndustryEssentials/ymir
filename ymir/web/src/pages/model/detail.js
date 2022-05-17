import React, { useEffect, useRef, useState } from "react"
import { Descriptions, List, Space, Tag, Card, Button, Row, Col } from "antd"
import { connect } from 'dva'
import { useParams, Link, useHistory } from "umi"

import t from "@/utils/t"
import { getTaskTypeLabel } from "@/constants/task"
import Breadcrumbs from "@/components/common/breadcrumb"
import TaskDetail from "@/components/task/detail"
import styles from "./detail.less"
import { percent } from "../../utils/number"
import TaskProgress from "@/components/task/progress"
import Error from "@/components/task/error"
import Hide from "@/components/common/hide"
import useRestore from "@/hooks/useRestore"

const { Item } = Descriptions

function ModelDetail({ modelCache, getModel }) {
  const { mid: id, id: pid } = useParams()
  const history = useHistory()
  const [model, setModel] = useState({ id })
  const hideRef = useRef(null)
  const restoreAction = useRestore(pid)

  useEffect(async () => {
    id && fetchModel(true)
  }, [id])

  useEffect(() => {
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
        <Col flex={1}>{model.name} &gt; {t(getTaskTypeLabel(model.taskType))}</Col>
        <Col><Button type='link' onClick={() => history.goBack()}>{t('common.back')}&gt;</Button></Col>
      </Row>
    )
  }


  const hide = (version) => {
    if (model?.project?.hiddenDatasets?.includes(version.id)) {
      return message.warn(t('dataset.hide.single.invalid'))
    }
    hideRef.current.hide([version])
  }

  const hideOk = () => {
    fetchModel(true)
  }

  async function restore() {
    const result = await restoreAction('model', [id])
    if (result) {
      fetchModel(true)
    }
  }

  return (
    <div className={styles.modelDetail}>
      <Breadcrumbs suffix={model.name} />
      <Card title={renderTitle()}>
        <div className={styles.content}>
          <Descriptions bordered column={2} labelStyle={{ width: '200px' }} title={t('model.detail.title')} className='infoTable'>
            <Item label={t('model.detail.label.name')}>{model.name} {model.versionName}</Item>
            {model.hidden ? <Item label={t("common.hidden.label")}>{t('common.state.hidden')}</Item> : null}
            <Item label={t('model.detail.label.map')}><span title={model.map}>{percent(model.map)}</span></Item>
          </Descriptions>
          <TaskProgress state={model.state} result={model} task={model.task} duration={model.durationLabel} progress={model.progress} fresh={() => fetchModel(true)} />
          {model?.task?.error_code ? <Error code={model.task?.error_code} msg={model.task?.error_message} /> : null}
          <TaskDetail task={model.task}></TaskDetail>
          <Space style={{ width: "100%", justifyContent: "flex-end" }}>{!model.hidden ? <>
            {model.url ? <Button><Link target="_blank" to={model.url}>{t('model.action.download')}</Link></Button> : null}
            <Button onClick={() => history.push(`/home/project/${model.projectId}/model/${model.id}/verify`)}>{t('model.action.verify')}</Button>
            <Button type='primary' onClick={() => history.push(`/home/task/mining/${model.projectId}?mid=${id}`)}>{t('dataset.action.mining')}</Button>
            <Button type='primary' onClick={() => history.push(`/home/task/inference/${model.projectId}?mid=${id}`)}>{t('dataset.action.inference')}</Button>
            <Button type='primary' onClick={() => history.push(`/home/task/train/${model.projectId}?mid=${id}`)}>{t('dataset.action.train')}</Button>
            <Button type='primary' onClick={() => hide(model)}>{t('common.action.hide')}</Button>
          </> :
            <Button type="primary" onClick={restore}>
              {t("common.action.restore")}
            </Button>
          }
          </Space>
        </div>
      </Card>
      <Hide ref={hideRef} type={1} msg='model.action.hide.confirm.content' ok={hideOk} />
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

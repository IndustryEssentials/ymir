import React, { useEffect, useRef, useState } from 'react'
import { Descriptions, List, Space, Tag, Card, Button, Row, Col, Progress } from 'antd'
import { connect } from 'dva'
import { useParams, Link, useHistory, useSelector } from 'umi'

import t from '@/utils/t'
import TaskDetail from '@/components/task/detail'
import { percent } from '../../utils/number'
import useFetch from '@/hooks/useFetch'
import { getRecommendStage } from '@/constants/model'

import Breadcrumbs from '@/components/common/breadcrumb'
import TaskProgress from '@/components/task/progress'
import Error from '@/components/task/error'
import Hide from '@/components/common/hide'
import useRestore from '@/hooks/useRestore'
import keywordsItem from '@/components/task/items/keywords'
import { DescPop } from '../../components/common/DescPop'
import useRerunAction from '../../hooks/useRerunAction'
import useCardTitle from '@/hooks/useCardTitle'
import VersionName from '@/components/result/VersionName'
import EditDescBox from '@/components/form/editDescBox'

import styles from './detail.less'

const { Item } = Descriptions

function ModelDetail() {
  const { mid: id, id: pid } = useParams()
  const history = useHistory()
  const model = useSelector(({ model }) => model.model[id] || {})
  const [_, getModel] = useFetch('model/getModel')
  const hideRef = useRef(null)
  const restoreAction = useRestore(pid)
  const generateRerunBtn = useRerunAction('btn')
  const cardTitle = useCardTitle(null, model?.name)
  const [editing, setEditing] = useState({})

  useEffect(async () => {
    ;(id || model?.needReload) && getModel({ id, force: true })
  }, [id, model?.needReload])

  function editDesc() {
    setEditing({})
    setTimeout(() => setEditing(model), 0)
  }

  const hide = (version) => {
    if (model?.project?.hiddenDatasets?.includes(version.id)) {
      return message.warn(t('dataset.hide.single.invalid'))
    }
    hideRef.current.hide([version])
  }

  function restore() {
    restoreAction('model', [id])
  }

  function getModelStage() {
    const stage = model.recommendStage
    return stage ? [id, stage].toString() : ''
  }

  function renderMetrics() {
    const stage = getRecommendStage(model)
    return stage ? (
      <Descriptions
        layout="vertical"
        column={4}
        labelStyle={{ display: 'block', fontWeight: 'bold', textAlign: 'center' }}
        bordered
        style={{ width: 'calc(100% + 240px)' }}
      >
        <Descriptions.Item label={'mAP'} style={{ width: '25%' }}>
          <Progress type="circle" percent={stage.map * 100} />
        </Descriptions.Item>
        <Descriptions.Item label={'Recall'} style={{ width: '25%' }}>
          {typeof stage.metrics.ar === 'undefined' ? <Progress type="circle" percent={stage.metrics.ar * 100} /> : null}
        </Descriptions.Item>
        <Descriptions.Item label={'FN'} style={{ width: '25%' }}>
          <Progress type="circle" percent={100} format={() => stage.metrics.fn} strokeColor={'rgba(255, 0, 255, 0.1)'} />
        </Descriptions.Item>
        <Descriptions.Item label={'FP'} style={{ width: '25%' }}>
          <Progress type="circle" percent={100} format={() => stage.metrics.fp} strokeColor={'rgba(255, 0, 0, 0.1)'} />
        </Descriptions.Item>
      </Descriptions>
    ) : null
  }

  return (
    <div className={styles.modelDetail}>
      <Breadcrumbs suffix={model.name} />
      <Card title={cardTitle}>
        <div className={styles.content}>
          <Descriptions bordered column={2} labelStyle={{ width: '200px' }} title={t('model.detail.title')} className="infoTable">
            <Item label={t('model.detail.label.name')}>
              <VersionName result={model} />
            </Item>
            {model.hidden ? <Item label={t('common.hidden.label')}>{t('common.state.hidden')}</Item> : null}
            {keywordsItem(model.keywords)}
            <Item label={t('model.detail.label.stage')} span={2}>
              <div style={{ width: '100%' }}>
                {model.stages?.map((stage) => (
                  <Tag key={stage.id} title={stage.map}>
                    {stage.name} mAP: {percent(stage.map)}
                  </Tag>
                ))}
              </div>
            </Item>
            <Item span={2} labelStyle={{ display: 'none' }} contentStyle={{ padding: 0, marginLeft: '-200px' }}>
              {renderMetrics()}
            </Item>
            <Item label={t('common.desc')} span={2}>
              <DescPop description={model.description} />
            </Item>
          </Descriptions>
          <TaskProgress
            state={model.state}
            result={model}
            task={model.task}
            duration={model.durationLabel}
            progress={model.progress}
            fresh={() => fetchModel(true)}
          />
          <Error code={model.task?.error_code} msg={model.task?.error_message} terminated={model?.task?.is_terminated} />
          <TaskDetail task={model.task}></TaskDetail>
          <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
            {!model.hidden ? (
              <>
                {model.url ? (
                  <Button>
                    <Link target="_blank" to={model.url}>
                      {t('model.action.download')}
                    </Link>
                  </Button>
                ) : null}
                <Button onClick={() => history.push(`/home/project/${model.projectId}/model/${model.id}/verify`)}>{t('model.action.verify')}</Button>
                <Button type="primary" onClick={() => history.push(`/home/project/${model.projectId}/mining?mid=${getModelStage()}`)}>
                  {t('dataset.action.mining')}
                </Button>
                <Button type="primary" onClick={() => history.push(`/home/project/${model.projectId}/inference?mid=${getModelStage()}`)}>
                  {t('dataset.action.inference')}
                </Button>
                <Button type="primary" onClick={() => history.push(`/home/project/${model.projectId}/train?mid=${getModelStage()}`)}>
                  {t('dataset.action.train')}
                </Button>
                <Button type="primary" onClick={() => hide(model)}>
                  {t('common.action.hide')}
                </Button>
                <Button type="primary" onClick={() => editDesc()}>
                  {t(`common.action.edit.desc`)}
                </Button>
              </>
            ) : (
              <Button type="primary" onClick={restore}>
                {t('common.action.restore')}
              </Button>
            )}
            {generateRerunBtn(model)}
          </Space>
        </div>
      </Card>
      <EditDescBox type="model" record={editing} />
      <Hide ref={hideRef} type={1} msg="model.action.hide.confirm.content" />
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

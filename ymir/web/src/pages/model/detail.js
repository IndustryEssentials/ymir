import React, { useEffect, useRef, useState } from 'react'
import { Descriptions, List, Space, Tag, Card, Button, Row, Col, Progress } from 'antd'
import { connect } from 'dva'
import { useParams, Link, useHistory, useSelector } from 'umi'

import t from '@/utils/t'
import TaskDetail from '@/components/task/detail'
import { percent } from '../../utils/number'
import useFetch from '@/hooks/useFetch'
import { ObjectType, getProjectTypeLabel } from '@/constants/project'
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
import Empty from '@/components/empty/default'

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

  useEffect(async () => (id || model?.needReload) && fetchModel(model.needReload), [id, model?.needReload])

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

  function fetchModel(force) {
    getModel({ id, force })
  }

  function getModelStage() {
    const stage = model.recommendStage
    return stage ? [id, stage].toString() : ''
  }

  function renderIntUnit(num) {
    return <span className={styles.metricsCount}>{t('model.metrics.fpfn.unit', { num: <span className={styles.metricsNum}>{num}</span> })}</span>
  }

  const renderPercentItem = (value, label, color = null) => (
    <Descriptions.Item key={label} label={label}>
      { value !== null ? <Progress type="circle" percent={value * 100} format={() => percent(value)} strokeColor={color} /> : <Empty /> }
    </Descriptions.Item>
  )

  const renderCountItem = (value, label, color = 'rgb(255, 255, 255)') => (
    <Descriptions.Item key={label} label={label}>
      { value !== null ? <Progress type="circle" percent={100} format={() => renderIntUnit(value)} strokeColor={color} /> : <Empty /> }
    </Descriptions.Item>
  )

  const metricsOptions = {
    tp: { label: 'TP', color: '#fff', isCount: true },
    fp: { label: 'FP', color: '#fff', isCount: true },
    fn: { label: 'FN', color: '#fff', isCount: true },
    ar: { label: 'Recall', color: 'rgb(44, 189, 233)' },
    acc: { label: 'MACC', color: 'rgb(44, 189, 233)' },
    boxAP: { label: 'boxAP', color: 'rgb(44, 189, 233)' },
  }

  const renderMetricsItems = (stage, type) => {
    const target = {
      [ObjectType.ObjectDetection]: 'ar',
      [ObjectType.SemanticSegmentation]: 'acc',
      [ObjectType.InstanceSegmentation]: 'boxAP',
    }[type]
    const list = [target, 'fn', 'fp']
    console.log('list:', list)
    return list.map((key) => {
      const option = metricsOptions[key]
      const metric = stage.metrics[key]
      const render = option.isCount ? renderCountItem : renderPercentItem
      return metric !== null ? render(metric, option.label, option.color) : null
    })
  }

  function renderMetrics() {
    const stage = getRecommendStage(model)
    return stage ? (
      <Descriptions
        className="infoTable vertical"
        layout="vertical"
        column={4}
        style={{ textAlign: 'center', marginTop: '-19px' }}
        labelStyle={{ display: 'block', fontWeight: 'bold', textAlign: 'center' }}
        bordered
      >
        {renderPercentItem(stage.primaryMetric, stage.primaryMetricLabel, 'rgb(54, 203, 203)')}
        {renderMetricsItems(stage, model.type)}
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
            <Item label={t('common.object.type')}>{t(getProjectTypeLabel(model.type, true))}</Item>
            {model.hidden ? <Item label={t('common.hidden.label')}>{t('common.state.hidden')}</Item> : null}
            {keywordsItem(model.keywords)}
            <Item label={t('model.detail.label.stage')} span={2}>
              <div style={{ width: '100%' }}>
                {model.stages?.map((stage) => (
                  <Tag key={stage.id} title={stage.primaryMetric}>
                    {stage.name} {stage.primaryMetricLabel}: {percent(stage.primaryMetric)}
                  </Tag>
                ))}
              </div>
            </Item>
            <Item label={t('common.desc')} span={2}>
              <DescPop description={model.description} />
            </Item>
          </Descriptions>
          {renderMetrics()}
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

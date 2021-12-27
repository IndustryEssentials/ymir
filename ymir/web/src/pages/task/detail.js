import React, { useEffect, useState } from "react"
import { connect } from 'dva'
import { useParams, Link, useHistory } from "umi"
import { Button, Card, Col, Descriptions, List, Progress, Row, Space, Tag } from "antd"

import t from "@/utils/t"
import { format } from '@/utils/date'
import Breadcrumbs from "@/components/common/breadcrumb"
import { getTaskStates, getTaskTypes } from '@/constants/query'
import { TASKSTATES, TASKTYPES } from '@/constants/task'
import StateTag from '../../components/task/stateTag'
import styles from "./detail.less"
import {
  ArrowDownIcon, ArrowUpIcon, ScreenIcon, TaggingIcon, TrainIcon, VectorIcon,
  FileYesIcon, FileHistoryIcon, SearchEyeIcon
} from "../../components/common/icons"

const { Item } = Descriptions

function TaskDetail({ getTask, getDataset, batchDatasets, getModel }) {
  const history = useHistory()
  const { id } = useParams()
  const [task, setTask] = useState({ id })
  const [dataset, setDataset] = useState({})
  const [model, setModel] = useState({})
  const [error, setError] = useState({
    code: 0,
    message: ''
  })
  const [showErrorMsg, setShowErrorMsg] = useState(false)
  const [taskModel, setTaskModel] = useState({})

  useEffect(async () => {
    const result = await getTask(id)

    if (result) {
      setTask(result)
    }
  }, [id])

  useEffect(async () => {
    if (isState(TASKSTATES.FINISH)) {
      getResult()
    } else if (isState(TASKSTATES.FAILURE)) {
      getError()
      goAnchor()
    }
  }, [task.state])

  useEffect(() => {
    if (task?.parameters?.model_id) {
      fetchModel(task.parameters.model_id)
    }
  }, [task.parameters])

  function getResult() {
    if (isType(TASKTYPES.TRAINING)) {
      // model
      fetchResultModel()
    } else {
      fetchResultDataset()
    }
  }

  async function fetchModel(id) {
    if (!id) {
      return
    }
    const result = await getModel(id)
    if (result) {
      setTaskModel(result)
    }
  }

  async function fetchResultDataset() {
    const id = task.result?.dataset_id
    if (!id) {
      return
    }
    const result = await getDataset(id)
    if (result) {
      setDataset(result)
    } else {
      setDataset({ id })
    }
    goAnchor()
  }

  async function fetchResultModel() {
    const id = task.result?.model_id
    if (!id) {
      return
    }
    const result = await getModel(id)
    if (result) {
      setModel(result)
    } else {
      setModel({ id })
    }
    goAnchor()
  }

  function goAnchor() {
    const anchor = history.location.hash
    if (anchor) {
      location.href = anchor
    }
  }

  function getError() {
    const error = task.result?.error
    if (error) {
      setError(error)
    }
  }

  function isType(type) {
    return type === task.type
  }

  function isState(state) {
    return state === task.state
  }

  const percentFormat = (value) => {
    return Number(value) * 100 + '%'
  }

  function getTypeLabel(type) {
    const types = getTaskTypes()
    const target = types.find(t => t.value === type)
    return target ? target.label : ''
  }

  function formatErrorMessage(message) {
    return <div hidden={!showErrorMsg} style={{ backgroundColor: '#f6f6f6', padding: 20 }}>
      {message.split('\n').map((item, i) => <div key={i}>{item}</div>)}
    </div>
  }

  function stateLabel(state) {
    const states = getTaskStates()
    const target = states.find(s => s.value === state)
    return state ? <Tag color={target.color}>{target.label}</Tag> : null
  }

  const labelStyle = { width: '15%', paddingRight: '20px', justifyContent: 'flex-end' }

  function renderDatasetName(dts = []) {
    return <Space>{dts.map(d => d ? <Link key={d.id} to={`/home/dataset/detail/${d.id}`}>{d.name}</Link> : ids)}</Space>
  }

  function renderConfig(config = {}) {
    return Object.keys(config).map(key => <Row key={key}>
      <Col style={{ width: 200, fontWeight: 'bold' }}>{key}:</Col>
      <Col>{config[key]}</Col>
    </Row>)
  }

  const renderTitle = (
    <Row>
      <Col flex={1}><strong>{t('task.detail.title')}</strong></Col>
      <Col><Button type='link' onClick={() => history.goBack()}>{t('common.back')}&gt;</Button></Col>
    </Row>
  )

  function renderResultTitle(type) {
    let title = ''
    if (model.id) {
      title = t('task.mining.form.model.label')
    } else if (dataset.id) {
      title = t('task.filter.form.datasets.label')
    } else if (error.code) {
      title = t('task.detail.error.title')
    }

    return <><FileYesIcon />{t('task.detail.result.title')}: {title}</>
  }

  return (
    <div className={styles.taskDetail}>
      <Breadcrumbs />
      <Card title={renderTitle}>
        {/* <h3 className={styles.title}>{t("task.detail.title")}</h3> */}
        <Descriptions column={2} bordered labelStyle={labelStyle} title={<><SearchEyeIcon /> {t("task.detail.title")} </>} className={styles.infoTable}>
          <Item label={t('task.detail.label.name')}>{task.name}</Item>
          <Item label={t('task.detail.label.id')}>{task.id}</Item>
          {isType(TASKTYPES.FILTER) ? (
            <>
              <Item label={t('task.filter.form.datasets.label')}>{renderDatasetName(task.filterSets)}</Item>
              <Item label={t('task.filter.form.include.label')} span={2}>{task.parameters.include_classes?.map(key => <Tag key={key}>{key}</Tag>)}</Item>
              {task.parameters.exclude_classes ? <Item label={t('task.filter.form.exclude.label')} span={2}>{task.parameters.exclude_classes?.map(key => <Tag key={key}>{key}</Tag>)}</Item> : null}
            </>
          ) : null}

          {isType(TASKTYPES.TRAINING) ? (
            <>
              {/* train */}
              <Item label={t('task.train.form.trainsets.label')}>{renderDatasetName(task.trainSets)} </Item>
              <Item label={t('task.train.form.testsets.label')}>{renderDatasetName(task.testSets)} </Item>
              {/* <Item label={t('task.detail.label.train_type')}>{task.parameters?.train_type}</Item> */}
              <Item label={t('task.detail.label.train_goal')}>{task.parameters.include_classes?.map(keyword => <Tag key={keyword}>{keyword}</Tag>)}</Item>
              <Item label={t('task.detail.label.framework')}>{task.parameters?.network} </Item>
              <Item label={t('task.detail.label.create_time')}>{format(task.create_datetime)} </Item>
              <Item label={t('task.detail.label.backbone')}>{task.parameters?.backbone}</Item>
              <Item label={t('task.detail.label.hyperparams')}>{renderConfig(task.config)}</Item>
            </>
          ) : null}

          {isType(TASKTYPES.MINING) ? (
            <>
              {/* mining */}
              <Item label={t('task.filter.form.datasets.label')}>{renderDatasetName(task.filterSets)}</Item>
              <Item label={t('task.mining.form.excludeset.label')}>{renderDatasetName(task.excludeSets)}</Item>
              <Item label={t('task.mining.form.model.label')}>
                <Link to={`/home/model/detail/${task.parameters.model_id}`}>{taskModel.name || task.parameters.model_id}</Link>
              </Item>
              <Item label={t('task.mining.form.algo.label')}>{task.parameters.mining_algorithm}</Item>
              <Item label={t('task.mining.form.label.label')}>{task.parameters.generate_annotations ? t('common.yes') : t('common.no')}</Item>
              <Item label={t('task.mining.form.topk.label')}>{task.parameters.top_k}</Item>
              <Item label={t('task.detail.label.hyperparams')}>{renderConfig(task.config)}</Item>
            </>
          ) : null}

          {isType(TASKTYPES.LABEL) ? (
            <>
              {/* label */}
              <Item label={t('task.filter.form.datasets.label')}>{renderDatasetName(task.filterSets)}</Item>
              <Item label={t('task.label.form.member')}>{task.parameters.labellers.map(m => <Tag key={m}>{m}</Tag>)}</Item>
              <Item label={t('task.label.form.target.label')}>{task.parameters.include_classes?.map(keyword => <Tag key={keyword}>{keyword}</Tag>)}</Item>
              <Item label={t('task.label.form.desc.label')}>
                {task.parameters.extra_url ? <a target='_blank' href={task.parameters.extra_url}>{t('task.detail.label.download.btn')}</a> : '-'}
              </Item>
            </>
          ) : null}
        </Descriptions>

        <Descriptions bordered labelStyle={labelStyle} title={<><FileHistoryIcon /> {t("task.detail.state.title")} </>} className={styles.infoTable}>
          <Item label={t('task.detail.state.current')}>
            <Row>
              <Col><StateTag mode='icon' size='large' state={task.state} /></Col>
              <Col flex={1}>{task.state === TASKSTATES.DOING ? <Progress strokeColor={'#FAD337'} percent={task.progress} /> : null}</Col>
            </Row>
          </Item>
        </Descriptions>
        <div id="result"></div>
        <Descriptions
          bordered
          column={1}
          className={styles.infoTable}
          labelStyle={labelStyle}
          title={renderResultTitle()}
        >
          {dataset.id ? (dataset.name ? <>
            <Item label={t('task.detail.dataset.name')}>
              <Row>
                <Col flex={1} style={{ lineHeight: '32px' }}><Link to={`/home/dataset/detail/${dataset.id}`}>{dataset.name}</Link></Col>
                <Col>
                  <Space>
                    <Button icon={<ScreenIcon />} type='primary' hidden={!dataset.keyword_count}
                    onClick={() => history.push(`/home/task/filter/${dataset.id}`)}>{t('dataset.detail.action.filter')}</Button>
                    <Button icon={<TrainIcon />} type='primary' onClick={() => history.push(`/home/task/train/${dataset.id}`)}>{t('dataset.detail.action.train')}</Button>
                    <Button icon={<TaggingIcon />} type='primary' onClick={() => history.push(`/home/task/label/${dataset.id}`)}>{t('dataset.detail.action.label')}</Button>
                  </Space>
                </Col>
              </Row>
            </Item>
            <Item label={t('dataset.column.asset_count')}>{dataset.asset_count}</Item>
            <Item label={t('dataset.column.keyword')}>{dataset.keywords.map(keyword => <Tag key={keyword}>{keyword}</Tag>)}</Item>
            <Item label={t('dataset.column.create_time')}>{format(dataset.create_datetime)}</Item>
          </> : <Item label={t('task.detail.state.current')}>{t('task.detail.model.deleted')}</Item>)
            : null}
          {model.id ? (model.name ? <>
            <Item label={t('model.column.name')}>
              <Row>
                <Col flex={1} style={{ lineHeight: '32px' }}><Link to={`/home/model/detail/${model.id}`}>{model.name}</Link> </Col>
                <Col>
                  <Space>
                    <Button icon={<VectorIcon />} type='primary' onClick={() => history.push(`/home/task/mining?mid=${model.id}`)}>{t('dataset.action.mining')}</Button>
                  </Space>
                </Col>
              </Row>
            </Item>
            <Item label={'ID'}>{model.id}</Item>
            <Item label={t('model.column.target')}>{model.keywords.join(', ')}</Item>
            <Item label={'mAP'}>{percentFormat(model.map)}</Item>
            <Item label={t('model.column.create_time')}>{format(task.create_datetime)}</Item>
          </> : <Item label={t('task.detail.state.current')}>{t('task.detail.model.deleted')}</Item>)
            : null}
          {error.code ? <>
            <Item label={t('task.detail.error.code')}>{getTypeLabel(task.type)}{t('task.detail.error.title')}</Item>
            <Item label={t('task.detail.error.desc')}>
              <div>
                <Button type="link" onClick={() => setShowErrorMsg(!showErrorMsg)}>
                  {showErrorMsg ? t('common.fold') : t('common.unfold')}{showErrorMsg ? <ArrowUpIcon /> : <ArrowDownIcon />}
                </Button>
                {formatErrorMessage(error.message)}
              </div>
            </Item>
          </>
            : null}
        </Descriptions>
        {task.type === TASKTYPES.LABEL ? <div style={{ textAlign: 'right' }}><Link to='/lsf/'>{t('task.detail.label.go.platform')}</Link></div> : null}
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
    getTask: (payload) => {
      return dispatch({
        type: 'task/getTask',
        payload,
      })
    },
    getDataset: (id) => {
      return dispatch({
        type: 'dataset/getDataset',
        payload: id
      })
    },
    batchDatasets: (ids) => {
      return dispatch({
        type: 'dataset/batchDatasets',
        payload: ids
      })
    },
    getModel: (id) => {
      return dispatch({
        type: 'model/getModel',
        payload: id
      })
    }
  }
}

export default connect(props, actions)(TaskDetail)

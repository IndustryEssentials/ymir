import React, { useEffect, useState } from "react"
import { Descriptions, List, Space, Tag, Card, Button, Row, Col } from "antd"
import { connect } from 'dva'
import { useParams, Link, useHistory } from "umi"

import t from "@/utils/t"
import Breadcrumbs from "../../components/common/breadcrumb"
import TripleRates from "@/components/form/tripleRates"
import styles from "./detail.less"

const { Item } = Descriptions

function ModelDetail({ getModel }) {
  const { id } = useParams()
  const history = useHistory()
  const [model, setModel] = useState({ id })

  useEffect(async () => {
    const result = await getModel(id)
    if (result) {
      // console.log('model: ', result)
      setModel(result)
    }
  }, [id])

  const percentFormat = (value) => {
    return Number(value) * 100 + '%'
  }

  function renderDataset(sets = []) {
    if (!sets.length) {
      return
    }
    return (
      <Space>
        { sets.map(item => item ? <Link key={item.id} to={`/home/dataset/detail/${item.id}`}>{item.name}</Link> : null) }
        <span>
          {t('dataset.detail.pager.total', { total: sets.reduce((prev, curr) => prev + curr.asset_count, 0) })}
        </span>
      </Space>
    )
  }

  function renderDatasetPercent() {
    const trainSets = (model?.trainSets || []).map(ds => ds.id)
    const testSets = (model?.testSets || []).map(ds => ds.id)
    const sets = [...(model?.trainSets || []), ...(model?.testSets || [])]
    return (
      <TripleRates
        data={sets}
        parts={[
          { ids: trainSets, label: t('task.train.form.trainsets.label') },
          { ids: testSets, label: t('task.train.form.testsets.label') },
        ]}
      ></TripleRates>
    )
  }

  function renderConfig(config = {}) {
    return Object.keys(config).map(key => <Row key={key}>
      <Col style={{ width: 200, fontWeight: 'bold' }}>{key}:</Col>
      <Col>{config[key]}</Col>
    </Row>)
  }

  function renderTitle () {
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
      {/* <h3 className={styles.title}>{t("dataset.detail.title")}</h3> */}
      <Descriptions bordered column={2} labelStyle={{ width: '200px' }} title={t('model.detail.title')}>
        <Item label={t('model.detail.label.name')}>{model.name}</Item>
        <Item label={t('model.detail.label.id')}>{model.id}</Item>
        <Item label={t('model.detail.label.map')}>{percentFormat(model.map)}</Item>
        <Item label={t('model.detail.label.source')}><Link to={`/home/task/detail/${model.task_id}`}>{model.task_name}</Link></Item>
        <Item label={t('model.detail.label.training_dataset')} span={2}>
          {renderDataset(model?.trainSets)}
        </Item>
        <Item label={t('model.detail.label.verify_dataset')} span={2}>
          {renderDataset(model?.testSets)}
        </Item>
        <Item label={t('model.detail.label.dataset_percent')} span={2}>{renderDatasetPercent()}</Item>
        <Item label={t('model.detail.label.train_type')} span={2}>{model.parameters?.train_type || 'Object Detection'}</Item>
        <Item label={t('model.detail.label.train_goal')} span={2}>{model.keywords?.map(keyword => (<Tag key={keyword}>{keyword}</Tag>))}</Item>
        <Item label={t('model.detail.label.framework')}>{model.parameters?.network} </Item>
        <Item label={t('model.detail.label.backbone')}>{model.parameters?.backbone}</Item>
        {/* <Item label={t('model.detail.label.hyperparams')}>
          {renderConfig(model.config)}
        </Item> */}
        <Item label={''} span={2}><Space>
          <Button><Link target="_blank" to={model.url}>{t('model.action.download')}</Link></Button>
          <Button onClick={() => history.push(`/home/model/verify/${model.id}`)}>{t('model.action.verify')}</Button>
          <Button type='primary' onClick={() => history.push(`/home/task/mining?mid=${model.id}`)}>{t('dataset.action.mining')}</Button>
        </Space></Item>
      </Descriptions>
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
    batchDatasets(ids) {
      return dispatch({
        type: 'dataset/batchDatasets',
        payload: ids,
      })
    },
  }
}

export default connect(props, actions)(ModelDetail)

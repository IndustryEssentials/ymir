import React, { useState, useEffect, memo, useMemo } from "react"
import { connect } from "dva"
import { Input, Select, Button, Form, message, ConfigProvider, Card, Space, Radio, Row, Col, InputNumber } from "antd"
import { useHistory, useParams } from "umi"

import { formLayout } from "@/config/antd"
import t from "@/utils/t"
import { randomNumber } from "@/utils/number"
import Breadcrumbs from "@/components/common/breadcrumb"
import EmptyState from '@/components/empty/dataset'
import s from "./index.less"
import commonStyles from "../common.less"
import Tip from "@/components/form/tip"
import RecommendKeywords from "@/components/common/recommendKeywords"
import Panel from "@/components/form/panel"

const { Option } = Select

function Fusion({ allDatasets, datasetCache, ...props }) {
  const pageParams = useParams()
  const id = Number(pageParams.id)
  const iterationId = Number(pageParams.iterationId)
  const currentStage = Number(pageParams.currentStage)
  const chunkSize = Number(pageParams.chunkSize)
  const strategy = Number(pageParams.strategy)
  const history = useHistory()
  const [form] = Form.useForm()
  const [dataset, setDataset] = useState({})
  const [datasets, setDatasets] = useState([])
  const [includeDatasets, setIncludeDatasets] = useState([])
  const [excludeDatasets, setExcludeDatasets] = useState([])
  const [keywords, setKeywords] = useState([])
  const [selectedKeywords, setSelectedKeywords] = useState([])
  const [selectedExcludeKeywords, setExcludeKeywords] = useState([])
  const [visibles, setVisibles] = useState({
    merge: true,
    filter: false,
    sampling: false,
  })

  const initialValues = {
    name: 'task_fusion_' + randomNumber(),
    samples: chunkSize,
    strategy: strategy || 2,
  }

  useEffect(() => {
    dataset.projectId && props.getDatasets(dataset.projectId)
  }, [dataset.projectId])

  useEffect(() => {
    id && props.getDataset(id)
  }, [id])

  useEffect(() => {
    const dst = datasetCache[id]
    dst && setDataset(dst)
  }, [datasetCache])

  useEffect(() => {
    getKeywords()
  }, [datasets, includeDatasets])

  useEffect(() => {
    setDatasets(allDatasets.filter(dataset => dataset.keywords.length))
  }, [allDatasets])

  useEffect(() => {
    const state = history.location.state

    if (state?.record) {
      const { parameters, name, } = state.record
      const { include_classes, include_datasets, exclude_classes, strategy } = parameters
      //do somethin
      form.setFieldsValue({
        name: `${name}_${randomNumber()}`,
        datasets: include_datasets,
        inc: include_classes,
        exc: exclude_classes,
        strategy,
      })
      setSelectedKeywords(include_classes)
      setExcludeKeywords(exclude_classes)
      history.replace({ state: {} })
    }
  }, [history.location.state])

  const getKeywords = () => {
    const selectedDataset = [id, ...includeDatasets]
    console.log('get keyword datasets: ', selectedDataset, id, includeDatasets, datasets)
    let ks = datasets.reduce((prev, current) => selectedDataset.includes(current.id)
      ? prev.concat(current.keywords)
      : prev, [])
    ks = [...new Set(ks)]
    ks.sort()
    setKeywords(ks)
  }

  const onFinish = async (values) => {
    const params = {
      ...values,
      project_id: dataset.projectId,
      group_id: dataset.groupId,
      dataset: id,
      include: selectedKeywords,
      exclude: selectedExcludeKeywords,
    }
    if (iterationId) {
      params.iteration = iterationId
      params.stage = currentStage
    }
    const result = await props.createFusionTask(params)
    if (result) {
      message.info(t('task.fusion.create.success.msg'))
      props.clearCache()
      history.replace(`/home/project/detail/${dataset.projectId}`)
    }
  }

  const onFinishFailed = (err) => {
    console.log("on finish failed: ", err)
  }

  function onIncludeDatasetChange(values) {
    setIncludeDatasets(values)

    getKeywords()
    // reset
    setSelectedKeywords([])
    setExcludeKeywords([])
    form.setFieldsValue({ inc: [], exc: [] })
  }
  function onExcludeDatasetChange(values) {
    setExcludeDatasets(values)
    // todo inter keywords
  }

  function selectRecommendKeywords(keyword) {
    const kws = [...new Set([...selectedKeywords, keyword])]
    setSelectedKeywords(kws)
    form.setFieldsValue({ inc: kws })
  }
  const datasetSelect = (filter = [], onChange = () => { }) => {
    return (
      <Select
        placeholder={t('task.fusion.form.datasets.placeholder')}
        mode='multiple'
        filterOption={(input, option) => option.key.toLowerCase().indexOf(input.toLowerCase()) >= 0}
        onChange={onChange}
        showArrow
      >
        {datasets.filter(ds => ![id, ...filter].includes(ds.id)).map(item => (
          <Option value={item.id} key={item.name}>
            {item.name}({item.assetCount})
          </Option>
        ))}
      </Select>
    )
  }

  return (
    <div className={commonStyles.wrapper}>
      <Breadcrumbs />
      <Card className={commonStyles.container} title={t('breadcrumbs.task.fusion')}>
        <Form
          form={form}
          name='fusionForm'
          {...formLayout}
          initialValues={initialValues}
          onFinish={onFinish}
          onFinishFailed={onFinishFailed}
          labelAlign={'left'}
          // size='middle'
          colon={false}
        >
          <Panel hasHeader={false}>
            <Tip hidden={true}>
              <Form.Item label={t('task.fusion.form.dataset')}><span>{dataset.name} {dataset.versionName} (assets: {dataset.assetCount})</span></Form.Item>
            </Tip>
          </Panel>
          <Panel label={t('task.fusion.header.merge')} visible={visibles['merge']} setVisible={(value) => setVisibles(old => ({ ...old, merge: value }))}>
            <ConfigProvider renderEmpty={() => <EmptyState add={() => history.push('/home/dataset/add')} />}>
              <Tip hidden={true}>
                <Form.Item label={t('task.fusion.form.merge.include.label')} name="include_datasets">
                  {datasetSelect(excludeDatasets, onIncludeDatasetChange)}
                </Form.Item>
              </Tip>
              <Tip hidden={true}>
                <Form.Item name='strategy'
                  hidden={includeDatasets.length < 1}
                  label={t('task.train.form.repeatdata.label')}>
                  <Radio.Group options={[
                    { value: 2, label: t('task.train.form.repeatdata.latest') },
                    { value: 3, label: t('task.train.form.repeatdata.original') },
                    { value: 1, label: t('task.train.form.repeatdata.terminate') },
                  ]} />
                </Form.Item>
              </Tip>
              <Tip hidden={true}>
                <Form.Item label={t('task.fusion.form.merge.exclude.label')} name="exclude_datasets">
                  {datasetSelect(includeDatasets, onExcludeDatasetChange)}
                </Form.Item>
              </Tip>
            </ConfigProvider>
          </Panel>
          <Panel label={t('task.fusion.header.filter')} visible={visibles['filter']} setVisible={(value) => setVisibles(old => ({ ...old, filter: value }))}>
            <Tip content={t('tip.task.fusion.includelable')}>
              <Form.Item label={t('task.fusion.form.include.label')}
                name='inc'
                help={<RecommendKeywords sets={form.getFieldValue('datasets')} onSelect={selectRecommendKeywords} />}
              >
                <Select
                  mode='multiple'
                  onChange={(value) => setSelectedKeywords(value)}
                  showArrow
                >
                  {keywords.map(keyword => selectedExcludeKeywords.indexOf(keyword) < 0
                    ? <Select.Option key={keyword} value={keyword}>{keyword}</Select.Option>
                    : null)}
                </Select>
              </Form.Item>
            </Tip>
            <Tip content={t('tip.task.fusion.excludelable')}>
              <Form.Item
                label={t('task.fusion.form.exclude.label')}
                name='exc'
              >
                <Select
                  mode='multiple'
                  onChange={(value) => setExcludeKeywords(value)}
                  showArrow
                >
                  {keywords.map(keyword => selectedKeywords.indexOf(keyword) < 0
                    ? <Select.Option key={keyword} value={keyword}>{keyword}</Select.Option>
                    : null)}
                </Select>
              </Form.Item>
            </Tip>
          </Panel>
          <Panel label={t('task.fusion.header.sampling')} visible={visibles['sampling']} setVisible={(value) => setVisibles(old => ({ ...old, sampling: value }))}>
            <Tip content={t('tip.task.fusion.sampling')}>
              <Form.Item label={t('task.fusion.form.sampling')} name='samples'>
                <InputNumber step={1} min={0} style={{ width: '100%' }} />
              </Form.Item>
            </Tip>
          </Panel>
          <Tip hidden={true}>
            <Form.Item className={s.submit} wrapperCol={{ offset: 8 }}>
              <Space size={20}>
                <Form.Item name='submitBtn' noStyle>
                  <Button type="primary" size="large" htmlType="submit">
                    {t('task.create')}
                  </Button>
                </Form.Item>
                <Form.Item name='backBtn' noStyle>
                  <Button size="large" onClick={() => history.goBack()}>
                    {t('task.btn.back')}
                  </Button>
                </Form.Item>
              </Space>
            </Form.Item>
          </Tip>
        </Form>
      </Card>
    </div>
  )
}

const props = (state) => {
  return {
    allDatasets: state.dataset.allDatasets,
    datasetCache: state.dataset.dataset,
  }
}
const mapDispatchToProps = (dispatch) => {
  return {
    getDatasets(pid, force) {
      return dispatch({
        type: "dataset/queryAllDatasets",
        payload: { pid, force },
      })
    },
    getDataset(id) {
      return dispatch({
        type: "dataset/getDataset",
        payload: id,
      })
    },
    clearCache() {
      return dispatch({ type: "dataset/clearCache", })
    },
    createFusionTask(payload) {
      return dispatch({
        type: "task/createFusionTask",
        payload,
      })
    },
  }
}

export default connect(props, mapDispatchToProps)(Fusion)

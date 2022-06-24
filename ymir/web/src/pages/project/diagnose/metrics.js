import React, { useEffect, useState } from "react"
import { Card, Button, Form, Row, Col, Radio, Slider, Select, InputNumber, Checkbox, Space, } from "antd"
import s from "./index.less"

import t from "@/utils/t"
import useFetch from "@/hooks/useFetch"
import Panel from "@/components/form/panel"
import InferResultSelect from "../../../components/form/inferResultSelect"
import MapView from "./components/mapView"
import CurvView from "./components/curvView"
import PView from "./components/pView"
import RView from "./components/rView"
import View from './components/view'

import { CompareIcon } from "@/components/common/icons"

const metricsTabs = [
  { label: 'mAP', value: 'map', component: MapView, },
  { label: 'PR curve', value: 'curv', component: CurvView, },
  { label: 'R@P', value: 'rp', component: RView, },
  { label: 'P@R', value: 'pr', component: PView, },
]

const xAxisOptions = [
  { label: 'Dataset', value: 'dataset' },
  { label: 'Class', value: 'class' },
]

const kwTypes = [{ label: '标签', value: 0 }, { label: '用户标签', value: 1 }]

function Matrics({ pid, project }) {
  console.log('pid:', pid)
  const [form] = Form.useForm()
  const [inferTasks, setInferTasks] = useState([])
  const [selectedModels, setSelectedModels] = useState([])
  const [selectedDatasets, setSelectedDatasets] = useState([])
  const [iou, setIou] = useState(0.5)
  const [everageIou, setEverageIou] = useState(false)
  const [confidence, setConfidence] = useState(0.3)
  const [selectedMetric, setSelectedMetric] = useState(metricsTabs[0].value)
  const [prRate, setPrRate] = useState(0.5)
  const [keywords, setKeywords] = useState([])
  const [selectedKeywords, setSelectedKeywords] = useState([])
  const [ck, setCK] = useState([])
  const [kwType, setKwType] = useState(0)
  const [kws, setKws] = useState([])
  const [xAxis, setXAsix] = useState(xAxisOptions[0].value)
  const [remoteData, fetchDiagnosis] = useFetch('dataset/evaluate')
  const [diagnosis, setDiagnosis] = useState(null)
  const [diagnosing, setDiagnosing] = useState(false)

  useEffect(() => {
    setDiagnosis(remoteData)
  }, [remoteData])

  useEffect(() => {
    if (diagnosing) {
      const kws = [...new Set(selectedModels.map(({ keywords }) => keywords).flat())]
      console.log('kws:', kws)
      setKeywords(kws)
    }
  }, [selectedModels, diagnosing])

  useEffect(() => {
    // calculate ck
    const cks = remoteData ? Object.values(remoteData).map(({ iou_evaluations }) => Object.keys(Object.values(iou_evaluations)[0].ck_evaluations)).flat() : []
    console.log('cks:', cks)

    setCK([...new Set(cks)])
  }, [remoteData])

  useEffect(() => {
    const kws = !kwType ? keywords : ck
    setKws(kws)
  }, [kwType, keywords, ck])

  useEffect(() => {
    setSelectedKeywords([])
  }, [kwType])

  useEffect(() => {
    setDiagnosing(!!diagnosis)
  }, [diagnosis])

  useEffect(() => {

  }, [selectedMetric, prRate, xAxis])

  const onFinish = async (values) => {
    const inferDataset = inferTasks.map(({ result }) => result)
    const params = {
      ...values,
      projectId: pid,
      everageIou,
      datasets: inferDataset,
    }
    fetchDiagnosis(params)
  }

  function onFinishFailed(errorInfo) {
    console.log("Failed:", errorInfo)
  }

  function inferResultChange({ tasks, models, datasets }) {
    setInferTasks(tasks.map(
      ({ config, parameters: { dataset_id, model_id, model_stage_id }, result_dataset: { id } }) =>
        ({ config, testing: dataset_id, model: model_id, stage: model_stage_id, result: id })))
    setSelectedDatasets(datasets)
    setSelectedModels(models)
  }

  function metricsChange({ target: { checked } }) {
    setSelectedMetric(checked)
  }

  function prRateChange({ target: { value } }) {
    console.log('pr rate chagne value:', value)
    setPrRate(value)
  }

  function xAxisChange({ target: { value } }) {
    setXAsix(value)
  }

  function kwChange(values) {
    setSelectedKeywords(values)
  }

  function isKw() {
    return kwType === kwTypes[0].value
  }

  function retry() {
    setDiagnosis(null)
    setDiagnosing(false)
  }

  function renderView() {
    const panel = metricsTabs.find(({ value }) => selectedMetric === value)
    const Viewer = View(panel.component)
    const kw = selectedKeywords.length ? selectedKeywords : kws
    console.log('keywords : selectedKeywords:', keywords, selectedKeywords)
    return <Viewer
      tasks={inferTasks}
      models={selectedModels}
      datasets={selectedDatasets}
      data={diagnosis}
      xType={xAxis}
      kwType={kwType}
      keywords={kw}
    />
  }

  const renderFilterPanel = () => <div className={s.filterPanel} size={20}>
    <Row gutter={20}>
      <Col flex={1}>
        <Radio.Group defaultValue={metricsTabs[0].value} options={metricsTabs} onChange={metricsChange} />
      </Col>
      <Col hidden={![metricsTabs[2].value, metricsTabs[3].value].includes(selectedMetric)} flex={'15%'}>
        <Slider style={{ width: 300 }} min={0} max={1}
          value={prRate}
          onChange={prRateChange}
          tooltipVisible marks={{ 0: '0', 0.5: '0.5', 1: '1' }}
          step={0.1} />
      </Col>
    </Row>
    <Row gutter={20}>
      <Col>
        <Select value={kwType} options={kwTypes} onChange={setKwType}></Select>
      </Col>
      <Col flex={1}>
        <Select style={{ width: '100%' }} mode={kwType ? 'single' : "multiple"}
          value={selectedKeywords}
          options={kws.map(kw => ({ label: kw, value: kw }))}
          placeholder={' Please select keywords'}
          showArrow onChange={kwChange}></Select>
      </Col>
      <Col>
        <Radio.Group defaultValue={xAxisOptions[0].value} options={xAxisOptions} onChange={xAxisChange} />
      </Col>
    </Row>
  </div>

  const renderViewPanel = () => <div className={s.metricsPanel}>{renderView()}</div>

  const renderIouTitle = <Space>
    <span>{t('model.diagnose.form.iou')}</span>
    <Form.Item noStyle>
      <Checkbox value={everageIou} onChange={({ target: { checked } }) => setEverageIou(checked)}>Everage IOU</Checkbox>
    </Form.Item>
  </Space>

  // todo form initial values
  const initialValues = {
    iou,
    confidence,
  }
  return (
    <div className={s.wrapper}>
      <Row className={s.view} gutter={20}>
        <Col className={s.filterPanel} span={18}>
          {renderFilterPanel()}
          {renderViewPanel()}
        </Col>
        <Col span={6} className={s.formContainer}>
          <div className={s.mask} hidden={!diagnosing}>
            <Button style={{ marginBottom: 24 }} size='large' type="primary" onClick={() => retry()}><CompareIcon /> {'restart'}</Button>
          </div>
          <Panel label={'Metrics'} style={{ marginTop: -10 }} toogleVisible={false}>
            <InferResultSelect pid={pid} onChange={inferResultChange} />
            <Form
              className={s.form}
              form={form}
              layout='vertical'
              initialValues={initialValues}
              onFinish={onFinish}
              onFinishFailed={onFinishFailed}
              labelAlign='left'
              colon={false}
            >
              <Form.Item label={t('model.diagnose.form.confidence')} name='confidence'>
                <InputNumber step={0.0005} min={0.0005} max={0.9995} />
              </Form.Item>
              <Form.Item label={renderIouTitle} name='iou'>
                <Slider style={{ display: !everageIou ? 'block' : 'none' }} min={0.25} max={0.95} step={0.05} marks={{ 0.25: '0.25', 0.5: '0.5', 0.95: '0.95' }} onChange={setIou} />
              </Form.Item>
              <Form.Item name='submitBtn'>
                <div style={{ textAlign: 'center' }}>
                  <Button type="primary" size="large" htmlType="submit">
                    <CompareIcon /> {'诊断'}
                  </Button>
                </div>
              </Form.Item>
            </Form>
          </Panel>
          <Panel label={'Set Default Stage'} toogleVisible={false}>
            {selectedModels.map(model =>
              <Form.Item label={`${model.name} ${model.versionName}`}>
                <Select>
                  {model.stages.map(stage => <Select.Option value={stage.id}>{stage.name}</Select.Option>)}
                </Select>
              </Form.Item>)}
          </Panel>
        </Col>
      </Row>
    </div >
  )
}

export default Matrics

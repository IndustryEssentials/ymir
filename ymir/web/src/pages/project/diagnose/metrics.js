import React, { useEffect, useState } from "react"
import { Card, Button, Form, Row, Col, Radio, Slider, Select, } from "antd"
import s from "./index.less"

import t from "@/utils/t"
import useFetch from "@/hooks/useFetch"
import Panel from "@/components/form/panel"
import ModelSelect from "@/components/form/modelSelect"
import DatasetSelect from "@/components/form/datasetSelect"

import { CompareIcon } from "@/components/common/icons"

const metricsTabs = [
  { label: 'mAP', value: 'map' },
  { label: 'PR curve', value: 'curv' },
  { label: 'R@P', value: 'rp' },
  { label: 'P@R', value: 'pr' },
]

const xAxisOptions = [
  { label: 'Dataset', value: 'dataset' },
  { label: 'Class', value: 'class' },
]

const kwTypes = [{ label: '标签', value: 'keyword' }, { label: '用户标签', value: 'ck' }]

function Matrics({ pid, project }) {
  console.log('pid:', pid)
  const [form] = Form.useForm()
  const [selectedModels, setSelectedModels] = useState([])
  const [selectedDatasets, setSelectedDatasets] = useState([])
  const [iou, setIou] = useState(0.5)
  const [confidence, setConfidence] = useState(0.3)
  const [selectedMetric, setSelectedMetric] = useState(metricsTabs[0].value)
  const [prRate, setPrRate] = useState(0.5)
  const [keywords, setKeywords] = useState([])
  const [ck, setCK] = useState([])
  const [kwType, setKwType] = useState(kwTypes[0].value)
  const [kwOptions, setKwOptions] = useState([])
  const [xAxis, setXAsix] = useState(null)
  const [diagnosis, fetchDiagnosis] = useFetch('model/evaluate')
  const [diagnosing, setDiagnosing] = useState(false)

  useEffect(() => {
    const kws = isKw() ? keywords : ck
    const options = kws.map(kw => ({ label: kw.name, value: kw.name }))
    setKwOptions(options)
  }, [kwType])

  useEffect(() => {
    setDiagnosing(!!diagnosis)
  }, [diagnosis])

  useEffect(() => {

  }, [selectedMetric, prRate, xAxis])

  const onFinish = async (values) => {
    fetchDiagnosis(values)
  }

  function onFinishFailed(errorInfo) {
    console.log("Failed:", errorInfo)
  }

  function modelChange(id, options = []) {
    console.log('options:', options)
    setSelectedModels(options.map(({ model }) => model) || [])
  }

  function datasetChange(id, options) {
    console.log('options:', options)
    setSelectedDatasets(options.map(({ dataset }) => dataset) || [])
  }

  function metricsChange({ target: { value }}) {
    setSelectedMetric(value)
  }

  function prRateChange({ target: { value }}) {
    setPrRate(value)
  }

  function xAxisChange({ target: { value }}) {
    setXAsix(value)
  }

  function isKw() {
    return kwType === kwTypes[0].value
  }

  function retry () {
    setDiagnosis(null)
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
    <Row>
      <Col>
        <Select value={kwType} options={kwTypes} onChange={setKwType}></Select>
      </Col>
      <Col flex={1}>
        <Select options={kwOptions}></Select>
      </Col>
      <Col>
        <Radio.Group defaultValue={xAxisOptions[0].value} options={xAxisOptions} onChange={xAxisChange} />
      </Col>
    </Row>
  </div>

  const renderViewPanel = () => <div className={s.metricsPanel}>metircs viewer</div>

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
              <Form
                className={s.form}
                form={form}
                layout='vertical'
                name='labelForm'
                initialValues={initialValues}
                onFinish={onFinish}
                onFinishFailed={onFinishFailed}
                labelAlign='left'
                colon={false}
              >
                <Form.Item label={t('model.diagnose.form.model')} rules={[{ require: true }]}>
                  <ModelSelect multiple pid={pid} onChange={modelChange} />
                </Form.Item>
                <Form.Item label={t('model.diagnose.form.testset')} rules={[{ require: true }]}>
                  <DatasetSelect mode='multiple' pid={pid} onChange={datasetChange} />
                </Form.Item>
                <Form.Item label={t('model.diagnose.form.confidence')} name='confidence'>
                  <Slider min={0} max={0.9} step={0.1} tooltipVisible marks={{ 0: '0', 0.5: '0.5', 0.9: '0.9' }} onChange={setConfidence} />
                </Form.Item>
                <Form.Item label={t('model.diagnose.form.iou')} name='iou'>
                  <Slider min={0.25} max={0.95} step={0.05} tooltipVisible marks={{ 0.25: '0.25', 0.5: '0.5', 0.95: '0.95' }} onChange={setIou} />
                </Form.Item>
                <Form.Item name='submitBtn'>
                  <div style={{ textAlign: 'center' }}>
                    <Button type="primary" size="large" htmlType="submit">
                      <CompareIcon /> {'诊断'}
                    </Button>
                    <Button type="primary" size="large">
                      <CompareIcon /> {'推理'}
                    </Button>
                  </div>
                </Form.Item>
              </Form>
            </Panel>
            {/* <Panel label={'Set Default Stage'} toogleVisible={false}>
              { selectedModels.map(model => 
                <Form.Item label={`${model.name} ${model.versionName}`}>
                  <Select>
                    {model.stages.map(stage => <Select.Option value={stage.id}>{stage.name}</Select.Option>)}
                  </Select>
                </Form.Item>)}
            </Panel> */}
          </Col>
        </Row>
    </div >
  )
}

export default Matrics

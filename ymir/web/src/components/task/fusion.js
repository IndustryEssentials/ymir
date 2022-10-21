import React, { useState, useEffect } from "react"
import { Select, Button, Form, message, Card, Space, Radio, Row, Col, InputNumber, Checkbox } from "antd"
import { useHistory, useParams, useSelector } from "umi"

import { formLayout } from "@/config/antd"
import t from "@/utils/t"
import { randomNumber } from "@/utils/number"
import useFetch from '@/hooks/useFetch'
import { MiningStrategy } from '@/constants/iteration'

import RecommendKeywords from "@/components/common/recommendKeywords"
import Panel from "@/components/form/panel"
import DatasetSelect from "@/components/form/datasetSelect"
import Desc from "@/components/form/desc"
import BottomButtons from "./BottomButtons"

function Fusion({ did, merging, iterationId, currentStage, strategy = '', chunk, ok = () => { }, skip = () => { }, bottom }) {
  console.log('did, merging, iterationId, currentStage, strategy = ', did, merging, iterationId, currentStage, strategy)
  // console.log('did, merging:', did, merging)
  const pageParams = useParams()
  const pid = Number(pageParams.id)
  const history = useHistory()
  const [form] = Form.useForm()
  const [includeDatasets, setIncludeDatasets] = useState([])
  const [excludeDatasets, setExcludeDatasets] = useState([])
  const [miningStrategy, setMiningStrategy] = useState(strategy || 0)
  const [excludeResult, setExcludeResult] = useState(strategy === '' ? false : true)
  const [keywords, setKeywords] = useState([])
  const [selectedKeywords, setSelectedKeywords] = useState([])
  const [selectedExcludeKeywords, setExcludeKeywords] = useState([])
  const [visibles, setVisibles] = useState({
    merge: true,
    filter: true,
    sampling: true,
  })
  const [fusionResult, fusion] = useFetch("task/fusion")
  const dataset = useSelector(({ dataset }) => dataset.dataset[did] || {})
  const [_d, getDataset] = useFetch('dataset/getDataset')

  const initialValues = {
    name: 'task_fusion_' + randomNumber(),
    samples: chunk,
    include_datasets: Number(merging) ? [Number(merging)] : [],
    strategy: 2,
  }

  useEffect(() => fusionResult && ok(fusionResult), [fusionResult])

  useEffect(() => did && getDataset({ id: did }), [did])

  useEffect(() => {
    dataset.id && includeDatasets.length && setKeywordOptions([dataset, ...includeDatasets])
  }, [dataset.id, includeDatasets])

  useEffect(() => {
    const state = history.location.state

    if (state?.record) {
      const { parameters, name, } = state.record
      const { include_classes, include_datasets, exclude_classes, include_strategy } = parameters
      //do somethin
      form.setFieldsValue({
        name: `${name}_${randomNumber()}`,
        datasets: include_datasets,
        inc: include_classes,
        exc: exclude_classes,
        strategy: include_strategy,
      })
      setSelectedKeywords(include_classes)
      setExcludeKeywords(exclude_classes)
      history.replace({ state: {} })
    }
  }, [history.location.state])

  const setKeywordOptions = (datasets = []) => {
    const kws = datasets.map(ds => ds.keywords).flat().filter(i => i)
    console.log('kws:', kws)
    setKeywords([...new Set(kws)].sort())
  }

  const checkInputs = (i) => {
    return i.exc || i.inc || i.samples || i?.exclude_datasets?.length || i?.include_datasets?.length
  }

  const onFinish = async (values) => {
    if (!checkInputs(values)) {
      return message.error(t('dataset.fusion.validate.inputs'))
    }
    const params = {
      ...values,
      project_id: dataset.projectId,
      group_id: dataset.groupId,
      dataset: did,
      include: selectedKeywords,
      exclude: selectedExcludeKeywords,
      mining_strategy: miningStrategy,
      exclude_result: excludeResult,
      include_strategy: Number(values.strategy) || 2,
    }
    if (iterationId) {
      params.iteration = iterationId
      params.stage = currentStage
    }
    fusion(params)
  }

  const onFinishFailed = (err) => {
    console.log("on finish failed: ", err)
  }

  function onIncludeDatasetChange(values) {
    setIncludeDatasets(values)

    // reset
    setSelectedKeywords([])
    setExcludeKeywords([])
    form.setFieldsValue({ inc: [], exc: [] })
  }
  function onExcludeDatasetChange(values) {
    setExcludeDatasets(values)
    // todo inter keywords
  }

  function miningStrategyChanged({ target: { checked } }) {
    if (Number(strategy) === MiningStrategy.free) {
      setMiningStrategy(checked ? MiningStrategy.unique : MiningStrategy.free)
      setExcludeResult(true)
    } else {
      setExcludeResult(checked)
    }
  }

  function selectRecommendKeywords(keyword) {
    const kws = [...new Set([...selectedKeywords, keyword])]
    setSelectedKeywords(kws)
    form.setFieldsValue({ inc: kws })
  }

  return (
    <Form
      form={form}
      name='fusionForm'
      {...formLayout}
      initialValues={initialValues}
      onFinish={onFinish}
      onFinishFailed={onFinishFailed}
    >
      <Panel hasHeader={false}>
        <Form.Item label={t('task.fusion.form.dataset')}><span>{dataset.name} {dataset.versionName} (assets: {dataset.assetCount})</span></Form.Item>
      </Panel>
      <Panel label={t('task.fusion.header.merge')} visible={visibles['merge']} setVisible={(value) => setVisibles(old => ({ ...old, merge: value }))}>
        <Form.Item label={t('task.fusion.form.merge.include.label')} name="include_datasets">
          <DatasetSelect
            placeholder={t('task.fusion.form.datasets.placeholder')}
            mode='multiple'
            pid={pid}
            filter={[...excludeDatasets, did]}
            allowEmpty={true}
            onChange={onIncludeDatasetChange}
            showArrow
          />
        </Form.Item>
        <Form.Item name='strategy'
          hidden={includeDatasets.length < 1}
          label={t('task.train.form.repeatdata.label')}>
          <Radio.Group options={[
            { value: 2, label: t('task.train.form.repeatdata.latest') },
            { value: 3, label: t('task.train.form.repeatdata.original') },
            { value: 1, label: t('task.train.form.repeatdata.terminate') },
          ]} />
        </Form.Item>
        {strategy.length ?
          <Form.Item noStyle>
            <Row><Col offset={8} flex={1}>
              <Checkbox defaultChecked={Number(strategy) !== MiningStrategy.free} onChange={miningStrategyChanged}>
                {t(`project.mining.strategy.${strategy}.label`)}
              </Checkbox>
            </Col></Row>
          </Form.Item>
          : null}
        <Form.Item label={t('task.fusion.form.merge.exclude.label')} name="exclude_datasets">
          <DatasetSelect
            placeholder={t('task.fusion.form.datasets.placeholder')}
            mode='multiple'
            pid={pid}
            filter={[...includeDatasets, did]}
            onChange={onExcludeDatasetChange}
            showArrow
          />
        </Form.Item>
      </Panel>
      <Panel label={t('task.fusion.header.filter')} visible={visibles['filter']} setVisible={(value) => setVisibles(old => ({ ...old, filter: value }))}>
        <Form.Item label={t('task.fusion.form.include.label')}
          tooltip={t('tip.task.fusion.includelable')}
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
        <Form.Item
          label={t('task.fusion.form.exclude.label')}
          tooltip={t('tip.task.fusion.excludelable')}
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
      </Panel>
      <Panel label={t('task.fusion.header.sampling')} visible={visibles['sampling']} setVisible={(value) => setVisibles(old => ({ ...old, sampling: value }))}>
        <Form.Item label={t('task.fusion.form.sampling')} tooltip={t('tip.task.fusion.sampling')} name='samples'>
          <InputNumber step={1} min={1} style={{ width: '100%' }} />
        </Form.Item>
      </Panel>
      <Desc form={form} />
      {bottom ? bottom : <BottomButtons />}
    </Form>
  )
}

export default Fusion

import React, { useState, useEffect } from "react"
import { connect } from "dva"
import { Input, Select, Button, Form, message, ConfigProvider, Card, Space, Row, Col, Radio } from "antd"
import { useHistory, useParams } from "umi"

import { formLayout } from "@/config/antd"
import t from "@/utils/t"
import { randomNumber } from "@/utils/number"
import Breadcrumbs from "../../../components/common/breadcrumb"
import EmptyState from '@/components/empty/dataset'
import styles from "./index.less"
import commonStyles from "../common.less"
import { TASKSTATES } from '@/constants/task'
const { Option } = Select

function Filter({
  getDatasets,
  createFilterTask,
}) {
  const { ids } = useParams()
  const datasetIds = ids ? ids.split('|').map(id => parseInt(id)) : []
  const history = useHistory()
  const [form] = Form.useForm()
  const [datasets, setDatasets] = useState([])
  const [keywords, setKeywords] = useState([])
  const [selectedKeywords, setSelectedKeywords] = useState([])
  const [selectedExcludeKeywords, setExclude] = useState([])

  const initialValues = {
    datasets: datasetIds,
    name: 'task_filter_' + randomNumber(),
  }

  useEffect(async () => {
    const result = await getDatasets({ limit: 100000 })
    if (result) {
      setDatasets(result.items.filter(dataset => TASKSTATES.FINISH === dataset.state && dataset.keyword_count))
    }
  }, [])

  useEffect(() => {
    getKeywords()
  }, [datasets])

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
      setExclude(exclude_classes)
      history.replace({ state: {} })
    }
  }, [history.location.state])

  const getKeywords = () => {
    const selectedDataset = form.getFieldValue('datasets')
    let ks = datasets.reduce((prev, current) => selectedDataset.indexOf(current.id) >= 0
      ? prev.concat(current.keywords)
      : prev, [])
    ks = [...new Set(ks)]
    ks.sort()
    setKeywords(ks)
  }

  const onFinish = async ({ name, datasets, strategy }) => {
    const params = {
      name: name.trim(),
      datasets,
      strategy,
      include: selectedKeywords,
      exclude: selectedExcludeKeywords,
    }
    const result = await createFilterTask(params)
    if (result) {
      message.info(t('task.filter.create.success.msg'))
      history.replace('/home/task')
    }
  }

  const onFinishFailed = (err) => {
    console.log("on finish failed: ", err)
  }

  function datasetChange() {
    getKeywords()
    // reset
    setSelectedKeywords([])
    setExclude([])
    form.setFieldsValue({ inc: [], exc: [] })
  }

  function requireOne(rule, value) {
    if ([...selectedKeywords, ...selectedExcludeKeywords].length) {
      return Promise.resolve()
    } else {
      return Promise.reject(t('task.filter.tip.keyword.required'))
    }
  }

  return (
    <div className={commonStyles.wrapper}>
      <Breadcrumbs />
      <Card className={commonStyles.container} title={t('breadcrumbs.task.filter')}>
        <Form
          form={form}
          name='filterForm'
          {...formLayout}
          initialValues={initialValues}
          onFinish={onFinish}
          onFinishFailed={onFinishFailed}
          labelAlign={'left'}
          size='large'
          colon={false}
        >
          <Form.Item
            label={t('task.filter.form.name.label')}
            name='name'
            rules={[
              { required: true, whitespace: true, message: t('task.filter.form.name.placeholder'), },
              { type: 'string', min: 2, max: 20 },
            ]}
          >
            <Input placeholder={t('task.filter.form.name.required')} autoComplete='off' allowClear />
          </Form.Item>
          <ConfigProvider renderEmpty={() => <EmptyState add={() => history.push('/home/dataset/add')} />}>
            <Form.Item
              label={t('task.filter.form.datasets.label')}
            >
              <Form.Item
                noStyle
                name="datasets"
                rules={[
                  { required: true, message: t('task.filter.form.datasets.required') },
                ]}
              >
                <Select
                  placeholder={t('task.filter.form.datasets.placeholder')}
                  mode='multiple'
                  filterOption={(input, option) => option.key.toLowerCase().indexOf(input.toLowerCase()) >= 0}
                  onChange={datasetChange}
                  showArrow
                >
                  {datasets.map(item => (
                    <Option value={item.id} key={item.name}>
                      {item.name}({item.asset_count})
                    </Option>
                  ))}
                </Select>
              </Form.Item>
              <div className={commonStyles.formItemLowLevel}>
                <span className={commonStyles.label}>{t('task.train.form.repeatdata.label')}</span>
                <Form.Item name='strategy' colon={true} initialValue={2} noStyle>
                  <Radio.Group options={[
                    { value: 2, label: t('task.train.form.repeatdata.latest') },
                    { value: 3, label: t('task.train.form.repeatdata.original') },
                    { value: 1, label: t('task.train.form.repeatdata.terminate') },
                  ]} />
                </Form.Item></div>
            </Form.Item>
          </ConfigProvider>
          <Form.Item label={t('dataset.column.keyword')} required>
            <Form.Item
              label={t('task.filter.form.include.label')}
              labelCol={{ span: 24, style: { fontWeight: 'normal', color: 'rgba(0, 0, 0, 0.65)' } }}
              name='inc'
              // hidden={!keywords.length}
              rules={[
                { validator: requireOne },
              ]}
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
              label={t('task.filter.form.exclude.label')}
              labelCol={{ span: 24, style: { fontWeight: 'normal', color: 'rgba(0, 0, 0, 0.65)' } }}
              name='exc'
              // hidden={!keywords.length}
              help={t('task.filter.tip.keyword.required')}
              rules={[
                { validator: requireOne },
              ]}
            >
              <Select
                mode='multiple'
                onChange={(value) => setExclude(value)}
                showArrow
              >
                {keywords.map(keyword => selectedKeywords.indexOf(keyword) < 0
                  ? <Select.Option key={keyword} value={keyword}>{keyword}</Select.Option>
                  : null)}
              </Select>
            </Form.Item>
          </Form.Item>
          <Form.Item className={styles.submit} wrapperCol={{ offset: 4 }}>
            <Space size={20}>
              <Form.Item name='submitBtn' noStyle>
                <Button type="primary" size="large" htmlType="submit">
                  {t('task.filter.create')}
                </Button>
              </Form.Item>
              <Form.Item name='backBtn' noStyle>
                <Button size="large" onClick={() => history.goBack()}>
                  {t('task.btn.back')}
                </Button>
              </Form.Item>
            </Space>
          </Form.Item>
        </Form>
      </Card>
    </div>
  )
}

const mapDispatchToProps = (dispatch) => {
  return {
    getDatasets(payload) {
      return dispatch({
        type: "dataset/getDatasets",
        payload,
      })
    },
    createFilterTask(payload) {
      return dispatch({
        type: "task/createFilterTask",
        payload,
      })
    },
  }
}

export default connect(null, mapDispatchToProps)(Filter)

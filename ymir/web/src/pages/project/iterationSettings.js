import { useCallback, useEffect, useState } from 'react'
import { Button, Card, Form, message, Modal, Select, Space, Row, Col, InputNumber } from 'antd'
import { useParams, useHistory } from "umi"

import s from './add.less'
import t from '@/utils/t'
import { MiningStrategy } from '@/constants/iteration'
import Breadcrumbs from '@/components/common/breadcrumb'
import DatasetSelect from '../../components/form/datasetSelect'
import useFetch from '../../hooks/useFetch'

const { useForm } = Form
const { confirm } = Modal

const strategyOptions = Object.values(MiningStrategy)
  .filter(key => Number.isInteger(key))
  .map(value => ({
    value,
    label: t(`project.mining.strategy.${value}`),
  }))

const Add = ({ }) => {
  const { id } = useParams()
  const history = useHistory()
  const [form] = useForm()
  const [project, getProject] = useFetch('project/getProject', {})
  const [result, updateIteration] = useFetch('project/updateProject')

  const [testSet, setTestSet] = useState(0)
  const [miningSet, setMiningSet] = useState(0)
  const [strategy, setStrategy] = useState(0)

  useEffect(() => {
    id && getProject({ id })
  }, [id])

  useEffect(() => {
    setTimeout(() => initForm(project), 1000)
  }, [project])

  useEffect(() => {
    if (result) {
      message.success(t(`project.update.success`))
      history.goBack()
    }
  }, [result])

  function initForm(project = {}) {
    const { name, trainSetVersion, testSet: testDataset, miningSet: miningDataset, miningStrategy, chunkSize } = project
    if (name) {
      form.setFieldsValue({
        trainSetVersion,
        testSet: testDataset?.id || undefined,
        miningSet: miningDataset?.id || undefined,
        strategy: miningStrategy || 0,
        chunkSize: miningStrategy === 0 && chunkSize ? chunkSize : undefined,
      })
      setStrategy(miningStrategy)
    }
  }

  const submit = async ({ name = '', description = '', ...values }) => {
    var params = {
      ...values,
      id,
      chunkSize: strategy === 0 ? values.chunkSize : undefined,
    }

    updateIteration(params)
  }

  const miningFilter = useCallback(datasets => datasets.filter(ds => ds.keywords.some(kw => project?.keywords?.includes(kw))), [project?.keywords])

  return (
    <div className={s.projectAdd}>
      <Breadcrumbs />
      <Card className={s.container} title={t('project.iteration.settings.title')}>
        <div className={s.formContainer}>
          <Form form={form} labelCol={{ span: 6, offset: 2 }} wrapperCol={{ span: 12 }}
            colon={false} labelAlign='left' onFinish={submit} scrollToFirstError>
            <Form.Item label={t('project.add.form.training.set')} tooltip={t('project.add.trainset.tip')}>
              <Row>
                <Col flex={1} className="normalColor">{project.trainSet?.name}</Col>
                <Col>
                  <Form.Item name='trainSetVersion' label={t('project.add.form.training.set.version')} className="normalFont">
                    <Select style={{ marginLeft: 20, width: 150 }} disabled={project.currentIteration}>
                      {project?.trainSet?.versions?.map(({ id, versionName, assetCount }) =>
                        <Select.Option key={id} value={id}>{versionName} (assets: {assetCount})</Select.Option>
                      )}
                    </Select>
                  </Form.Item>
                </Col>
              </Row>
            </Form.Item>
            <Form.Item label={t('project.add.form.test.set')} name="testSet" rules={[
              { required: true, message: t('task.train.form.testset.required') },
            ]} tooltip={t('project.add.testset.tip')}>
              <DatasetSelect
                pid={id}
                filter={[miningSet]}
                filterGroup={[project?.trainSet?.id, project?.miningSet?.groupId]}
                filters={miningFilter}
                onChange={(value) => setTestSet(value)}
                allowClear
              />
            </Form.Item>
            <Form.Item label={t('project.add.form.mining.set')} name="miningSet"
              rules={[
                { required: true, message: t('task.train.form.miningset.required') },
              ]} tooltip={t('project.add.miningset.tip')}>
              <DatasetSelect
                pid={id}
                filter={[testSet]}
                filterGroup={[project?.trainSet?.id, project?.testSet?.groupId]}
                onChange={(value) => setMiningSet(value)}
                allowClear
              />
            </Form.Item>
            <Form.Item label={t('project.add.form.mining.strategy')}>
              <Row wrap={false}>
                <Col flex={1}>
                  <Form.Item name='strategy' noStyle>
                    <Select options={strategyOptions} onChange={value => setStrategy(value)} />
                  </Form.Item>
                </Col>
                {strategy === MiningStrategy.block ? <Col flex={'200px'} offset={1}>
                  <Form.Item label={t('project.add.form.mining.chunksize')}
                    className="normalFont"
                    name='chunkSize'
                    rules={[
                      { required: strategy === MiningStrategy.block }
                    ]}>
                    <InputNumber step={1} min={2} precision={0} style={{ width: '100%' }} />
                  </Form.Item>
                </Col> : null}
              </Row>
            </Form.Item>
            <Form.Item wrapperCol={{ offset: 8 }}>
              <Space size={20}>
                <Form.Item name='submitBtn' noStyle>
                  <Button type="primary" size="large" htmlType="submit">
                    {t('common.confirm')}
                  </Button>
                </Form.Item>
                <Form.Item name='backBtn' noStyle>
                  <Button size="large" onClick={() => history.goBack()}>
                    {t('common.back')}
                  </Button>
                </Form.Item>
              </Space>
            </Form.Item>
          </Form>
        </div>
      </Card>
    </div>
  )
}

export default Add

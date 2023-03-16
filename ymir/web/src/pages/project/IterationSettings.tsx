import { FC, useCallback, useEffect, useState } from 'react'
import { Button, Card, Form, message, Modal, Select, Space, Row, Col, InputNumber } from 'antd'
import { useParams, useHistory } from 'umi'

import s from './add.less'
import t from '@/utils/t'
import { MiningStrategy } from '@/constants/iteration'
import useFetch from '../../hooks/useFetch'

import Breadcrumbs from '@/components/common/breadcrumb'
import DatasetSelect from '../../components/form/datasetSelect'
import AssetCount from '@/components/dataset/AssetCount'
import useRequest from '@/hooks/useRequest'

const { useForm } = Form
const { confirm } = Modal

const strategyOptions = Object.values(MiningStrategy)
  .filter((key) => Number.isInteger(key))
  .map((value) => ({
    value,
    label: t(`project.mining.strategy.${value}`),
  }))

const Add: FC = () => {
  const params = useParams<{ id: string }>()
  const id = Number(params.id)
  const history = useHistory()
  const [form] = useForm()
  const { data: project, run: getProject } = useRequest<YModels.Project, [{ id: number }]>('project/getProject')
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

  function initForm(project?: YModels.Project) {
    if (!project) {
      return
    }
    const { trainSetVersion, testSet: testDataset, miningSet: miningDataset, miningStrategy, chunkSize } = project
    form.setFieldsValue({
      trainSetVersion,
      testSet: testDataset?.id || undefined,
      miningSet: miningDataset?.id || undefined,
      strategy: miningStrategy || 0,
      chunkSize: miningStrategy === 0 && chunkSize ? chunkSize : undefined,
    })
    miningDataset && setMiningSet(miningDataset.id)
    testDataset && setTestSet(testDataset.id)
    setStrategy(miningStrategy)
  }

  const submit = async ({ name = '', description = '', ...values }) => {
    var params = {
      ...values,
      id,
      chunkSize: strategy === 0 ? values.chunkSize : undefined,
    }

    updateIteration(params)
  }

  const excludeForGroup = (ds: YModels.Dataset, excludeGroup: (number | undefined)[]) => !excludeGroup.includes(ds.groupId)
  const excludeForId = (ds: YModels.Dataset, excludeIds: (number | undefined)[]) => !excludeIds.includes(ds.id)
  const datasetsFilter = useCallback(
    (isTestDataset?: boolean) => (datasets: YModels.Dataset[]) => {
      if (!project) {
        return datasets
      }
      const excludeDataset = isTestDataset ? miningSet : testSet

      return project
        ? datasets.filter(
            (ds) =>
              excludeForGroup(ds, [project.trainSet?.id]) &&
              excludeForId(ds, [project.candidateTrainSet, excludeDataset]) &&
              (!isTestDataset || ds.keywords.some((kw) => project?.keywords?.includes(kw))),
          )
        : datasets
    },
    [project, testSet, miningSet],
  )

  return (
    <div className={s.projectAdd}>
      <Breadcrumbs />
      <Card className={s.container} title={t('project.iteration.settings.title')}>
        <div className={s.formContainer}>
          <Form form={form} labelCol={{ span: 6, offset: 2 }} wrapperCol={{ span: 12 }} colon={false} labelAlign="left" onFinish={submit} scrollToFirstError>
            <Form.Item label={t('project.add.form.training.set')} tooltip={t('project.add.trainset.tip')}>
              <Row>
                <Col flex={1} className="normalColor">
                  {project?.trainSet?.name}
                </Col>
                <Col>
                  <Form.Item name="trainSetVersion" label={t('project.add.form.training.set.version')} className="normalFont" style={{ marginBottom: 0 }}>
                    <Select style={{ marginLeft: 20, width: 150 }} disabled={!!project?.currentIteration}>
                      {project?.trainSet?.versions?.map((dataset) => (
                        <Select.Option key={dataset.id} value={dataset.id}>
                          {dataset.versionName} (assets: <AssetCount dataset={dataset} />)
                        </Select.Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
              </Row>
            </Form.Item>
            <Form.Item
              label={t('project.add.form.test.set')}
              name="testSet"
              rules={[{ required: true, message: t('task.train.form.testset.required') }]}
              tooltip={t('project.add.testset.tip')}
            >
              <DatasetSelect pid={id} filters={datasetsFilter(true)} onChange={setTestSet} allowClear />
            </Form.Item>
            <Form.Item
              label={t('project.add.form.mining.set')}
              name="miningSet"
              rules={[{ required: true, message: t('task.train.form.miningset.required') }]}
              tooltip={t('project.add.miningset.tip')}
            >
              <DatasetSelect pid={id} filters={datasetsFilter()} onChange={setMiningSet} allowClear />
            </Form.Item>
            <Form.Item label={t('project.add.form.mining.strategy')}>
              <Row wrap={false}>
                <Col flex={1}>
                  <Form.Item name="strategy" noStyle>
                    <Select options={strategyOptions} onChange={setStrategy} />
                  </Form.Item>
                </Col>
                {strategy === MiningStrategy.block ? (
                  <Col flex={'200px'} offset={1}>
                    <Form.Item
                      label={t('project.add.form.mining.chunksize')}
                      className="normalFont"
                      name="chunkSize"
                      rules={[{ required: strategy === MiningStrategy.block }]}
                    >
                      <InputNumber step={1} min={2} precision={0} style={{ width: '100%' }} />
                    </Form.Item>
                  </Col>
                ) : null}
              </Row>
            </Form.Item>
            <Form.Item wrapperCol={{ offset: 8 }}>
              <Space size={20}>
                <Form.Item name="submitBtn" noStyle>
                  <Button type="primary" size="large" htmlType="submit">
                    {t('common.confirm')}
                  </Button>
                </Form.Item>
                <Form.Item name="backBtn" noStyle>
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

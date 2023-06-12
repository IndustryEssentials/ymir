import { FC, useState, useEffect, useCallback } from 'react'
import { useHistory, useParams, useSelector } from 'umi'
import t from '@/utils/t'
import { Dataset, Project, Task } from '@/constants'
import { Button, Card, Col, Form, Row, Space } from 'antd'
import DatasetSelect from '@/components/form/datasetSelect'
import DockerConfigForm from '@/components/form/items/DockerConfig'
import { formLayout } from '@/config/antd'
import useRequest from '@/hooks/useRequest'
import { transHyperParams } from './_utils'
import { randomNumber } from '@/utils/number'
import { InferenceParams } from '@/services/task.d'
import DatasetOption from '@/components/form/option/Dataset'
import { getConfig, TYPES } from '@/constants/image'
import { ObjectType } from '@/constants/objectType'
import PromptInput from './PromptInput'

type Props = {}
const DatasetInfer: FC<Props> = ({}) => {
  const pageParams = useParams<{ id: string }>()
  const pid = Number(pageParams.id)
  const history = useHistory()
  const [form] = Form.useForm()
  const [seniorConfig, setSeniorConfig] = useState({})
  const { data: project, run: getProject } = useRequest<Project, [{ id: number }]>('project/getProject', {
    cacheKey: 'getProject',
    loading: false,
  })
  const { data: result, run: infer } = useRequest<Task, [InferenceParams]>('task/infer')
  const { groundedSAM: image } = useSelector(({ image }) => image)

  useEffect(() => {
    pid && getProject({ id: pid })
  }, [pid])

  useEffect(() => {
    if (!image) {
      return
    }
    const config = getConfig(image, TYPES.INFERENCE, ObjectType.MultiModal)
    config && setSeniorConfig(config.config)
  }, [image])

  useEffect(() => {
    result && history.replace(`/home/project/${pid}/prediction`)
  }, [result])

  const onFinish = async ({ hyperparam, dataset, prompt, gpu_count = 1 }: any) => {
    if (!image) {
      return
    }
    const config = transHyperParams(hyperparam, prompt, gpu_count)

    const params = {
      dataset,
      name: 'task_inference_' + randomNumber(),
      projectId: pid,
      image: image.id,
      config,
    }
    infer(params)
  }

  function onFinishFailed(errorInfo: any) {
    console.log('Failed:', errorInfo)
  }

  const testSetFilters = useCallback(
    (datasets: Dataset[]) => {
      const testings = datasets.filter((ds) => project?.testingSets?.includes(ds.id)).map((ds) => ({ ...ds, isProjectTesting: true }))
      const others = datasets.filter((ds) => !project?.testingSets?.includes(ds.id))
      return [...testings, ...others]
    },
    [project?.testingSets],
  )

  const renderLabel = (item: Dataset & { isProjectTesting?: boolean }) => (
    <Row>
      <Col flex={1}>
        <DatasetOption dataset={item} />
      </Col>
      <Col>{item.isProjectTesting ? t('project.testing.dataset.label') : null}</Col>
    </Row>
  )

  return (
    <Form {...formLayout} form={form} name="inferenceForm" onFinish={onFinish} onFinishFailed={onFinishFailed}>
      <Form.Item
        label={t('task.inference.form.dataset.label')}
        required
        name="dataset"
        rules={[{ required: true, message: t('task.inference.form.dataset.required') }]}
      >
        <DatasetSelect pid={pid} filters={testSetFilters} renderLabel={renderLabel} placeholder={t('task.inference.form.dataset.placeholder')} />
      </Form.Item>
      <PromptInput />
      <DockerConfigForm form={form} show={true} seniorConfig={seniorConfig} />

      <Form.Item wrapperCol={{ offset: 8 }}>
        <Space size={20}>
          <Form.Item name="submitBtn" noStyle>
            <Button type="primary" size="large" htmlType="submit">
              {t('common.action.inference')}
            </Button>
          </Form.Item>
          <Form.Item name="backBtn" noStyle>
            <Button size="large" onClick={() => history.goBack()}>
              {t('task.btn.back')}
            </Button>
          </Form.Item>
        </Space>
      </Form.Item>
    </Form>
  )
}
export default DatasetInfer

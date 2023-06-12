import { FC, useState, useEffect, ReactNode } from 'react'
import { useSelector } from 'umi'
import t from '@/utils/t'
import { Form, FormInstance, InputNumber } from 'antd'
import useRequest from '@/hooks/useRequest'
type Props = {
  form: FormInstance
  min?: number
  tip?: ReactNode
  name?: string
}
const GPUCount: FC<Props> = ({ form, min = 0, name = 'gpu_count', tip }) => {
  const [gpuCount, setGpuCount] = useState<number>(0)
  const { data: sysInfo } = useRequest<{ gpu_count: number }>('common/getSysInfo', {
    cacheKey: 'getSysInfo',
    loading: false,
    manual: false,
  })

  useEffect(() => {
    sysInfo && setGpuCount(sysInfo.gpu_count)
  }, [sysInfo])

  const validator = () => {
    const input = Number(form.getFieldValue(name))
    return input >= min && input <= gpuCount ? Promise.resolve() : Promise.reject()
  }

  return (
    <Form.Item tooltip={tip} label={t('task.gpu.count')}>
      <Form.Item
        noStyle
        name={name}
        initialValue={min}
        rules={[
          {
            validator,
            message: t('task.gpu.invalid', { min, max: gpuCount }),
          },
        ]}
      >
        <InputNumber min={min} max={gpuCount} precision={0} />
      </Form.Item>
      <span style={{ marginLeft: 20 }}>{t('task.gpu.tip', { count: gpuCount })}</span>
    </Form.Item>
  )
}
export default GPUCount

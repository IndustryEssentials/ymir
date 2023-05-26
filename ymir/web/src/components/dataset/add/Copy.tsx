import ProjectDatasetSelect, { DataNodeType } from '@/components/form/ProjectDatasetSelect'
import { FC, useState, useEffect } from 'react'
import t from '@/utils/t'
import { ImportSelectorProps } from '.'
import { useParams } from 'umi'
import { Types } from './AddTypes'
import { Button, Form } from 'antd'
import { ImportingItem } from '@/constants'
import useRequest from '@/hooks/useRequest'
import { formLayout } from '@/config/antd'

const Copy: FC = () => {
  const [form] = Form.useForm()
  const [items, setItems] = useState<ImportingItem[]>([])
  const { run: addImportingList } = useRequest('dataset/addImportingList', { loading: false })

  useEffect(() => {}, [])
  return (
    <Form
      form={form}
      {...formLayout}
      onFinish={() => {
        addImportingList(items)
        form.resetFields()
      }}
      onFinishFailed={(err) => {
        console.log('finish failed: ', err)
      }}
    >
      <Form.Item required label={t('dataset.add.form.copy.label')}>
        <ProjectDatasetSelect
          multiple
          onChange={(_, options) => {
            if (Array.isArray(options)) {
              const items: ImportingItem[] = (options as DataNodeType[][])?.map(([{ label }, { dataset }]) => ({
                type: Types.COPY,
                name: dataset?.name,
                source: dataset?.id,
                sourceName: `${label} ${dataset?.name}`,
              }))

              setItems(items)
            }
          }}
          placeholder={t('dataset.add.form.copy.placeholder')}
        />
      </Form.Item>

      <Form.Item>
        <Button type="primary" htmlType="submit">
          Add to List
        </Button>
      </Form.Item>
    </Form>
  )
}
export default Copy

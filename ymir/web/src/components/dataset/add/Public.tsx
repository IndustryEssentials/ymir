import { Dataset, ImportingItem } from '@/constants'
import { Button, Form, Select } from 'antd'
import { FC, useState, useEffect } from 'react'
import t from '@/utils/t'
import useRequest from '@/hooks/useRequest'
import DatasetOption from '@/components/form/option/Dataset'
import { Types } from './AddTypes'
import { List } from '@/models/typings/common'
import { formLayout } from '@/config/antd'
type Props = {
  selected?: number
}
const Public: FC<Props> = ({ selected }) => {
  const [form] = Form.useForm()
  const [items, setItems] = useState<ImportingItem[]>([])
  const { data: { items: publicDatasets } = { items: [] }, run: getPublicDatasets } = useRequest<List<Dataset>>('dataset/getInternalDataset', {
    loading: false,
  })
  const { run: addImportingList } = useRequest<null, [ImportingItem[]]>('dataset/addImportingList', { loading: false })

  useEffect(() => {
    getPublicDatasets()
  }, [])
  return (
    <Form
      form={form}
      {...formLayout}
      onFinish={() => {
        addImportingList(items)
        form.resetFields()
      }}
    >
      <Form.Item
        label={t('dataset.add.form.internal.label')}
        tooltip={t('tip.task.filter.datasets')}
        name="did"
        initialValue={selected}
        rules={[
          {
            required: true,
            message: t('dataset.add.form.internal.required'),
          },
        ]}
      >
        <Select
          placeholder={t('dataset.add.form.internal.placeholder')}
          mode="multiple"
          onChange={(value, options) => {
            if (Array.isArray(options)) {
              console.log('value, option:', value, options)
              const items: ImportingItem[] = options?.map(({ dataset }) => ({
                type: Types.INTERNAL,
                name: dataset.name,
                source: dataset.id,
                sourceName: dataset.name,
              }))

              setItems(items)
            }
          }}
          options={publicDatasets?.map((dataset) => ({
            value: dataset.id,
            dataset,
            label: <DatasetOption dataset={dataset} />,
          }))}
        ></Select>
      </Form.Item>

      <Form.Item>
        <Button type="primary" htmlType="submit">
          Add to List
        </Button>
      </Form.Item>
    </Form>
  )
}
export default Public

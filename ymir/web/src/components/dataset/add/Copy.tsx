import ProjectDatasetSelect from '@/components/form/ProjectDatasetSelect'
import { FC, useState, useEffect } from 'react'
import t from '@/utils/t'
import { ImportSelectorProps } from '.'
import { useParams } from 'umi'
import { Types } from './AddTypes'
import { Button, Form } from 'antd'
import { ImportingItem } from '@/constants'
import useRequest from '@/hooks/useRequest'

const Copy: FC = () => {
  const [items, setItems] = useState<ImportingItem[]>([])
  const { run: addImportingList } = useRequest('dataset/addImportingList', { loading: false })

  useEffect(() => {}, [])
  return (
    <Form
      onFinish={() => {
        addImportingList(items)
      }}
    >
      <Form.Item label={t('dataset.add.form.copy.label')}>
        <ProjectDatasetSelect
          multiple
          onChange={(_, options) => {
            const datasets = options.map((opt) => opt[1]?.dataset)
            const items = datasets.map((ds) => ({
              type: Types.COPY,
              name: ds.name,
              source: ds.id,
              sourceName: ds.name,
            }))
            setItems(items)
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

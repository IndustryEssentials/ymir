import { Dataset, ImportingItem } from '@/constants'
import { Button, Form, Select } from 'antd'
import { FC, useState, useEffect } from 'react'
import t from '@/utils/t'
import useRequest from '@/hooks/useRequest'
import DatasetOption from '@/components/form/option/Dataset'
import { Types } from './AddTypes'
import { List } from '@/models/typings/common'
import { formLayout } from '@/config/antd'
import SubmitBtn from './SubmitBtn'
import { useSelector } from 'umi'
import { ImportingMaxCount } from '@/constants/common'
type Props = {
  selected?: number
}
const Public: FC<Props> = ({ selected }) => {
  const [form] = Form.useForm()
  const [items, setItems] = useState<ImportingItem[]>([])
  const { max } = useSelector(({ dataset }) => dataset.importing)
  const { data: publicDatasets = [], run: getPublicDatasets } = useRequest<Dataset[]>('dataset/getInternalDataset', {
    loading: false,
  })
  const { run: addImportingList } = useRequest<null, [ImportingItem[]]>('dataset/addImportingList', { loading: false })
  const { run: setEditing } = useRequest<null, [boolean]>('dataset/updateImportingEditState', { loading: false })

  useEffect(() => {
    getPublicDatasets()
  }, [])

  useEffect(() => setEditing(!!items.length), [items])

  return (
    <Form
      form={form}
      {...formLayout}
      onFinish={() => {
        addImportingList(items)
        form.resetFields()
        setItems([])
      }}
      onFinishFailed={(err) => {
        console.log('finish failed: ', err)
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
          {
            validator(rule, value) {
              return value.length <= max ? Promise.resolve() : Promise.reject()
            },
            message: t('dataset.add.form.internal.max', { max: ImportingMaxCount }),
          },
        ]}
      >
        <Select
          placeholder={t('dataset.add.form.internal.placeholder')}
          mode="multiple"
          onChange={(value, options) => {
            if (Array.isArray(options)) {
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

      <SubmitBtn disabled={!items.length} />
    </Form>
  )
}
export default Public

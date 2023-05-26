import ProjectDatasetSelect, { DataNodeType } from '@/components/form/ProjectDatasetSelect'
import { FC, useState, useEffect } from 'react'
import t from '@/utils/t'
import { ImportSelectorProps } from '.'
import { useParams } from 'umi'
import { Types } from './AddTypes'
import { Button, Cascader, Form } from 'antd'
import { ImportingItem } from '@/constants'
import useRequest from '@/hooks/useRequest'
import { formLayout } from '@/config/antd'
import SubmitBtn from './SubmitBtn'

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
      <Form.Item required label={t('dataset.add.form.copy.label')} name="dataset">
        <ProjectDatasetSelect
          onChange={(_, option) => {
            if (Array.isArray(option)) {
              const label = option[0].label
              const dataset = option[1].dataset
              const item: ImportingItem = {
                type: Types.COPY,
                name: dataset?.name,
                source: dataset?.id,
                sourceName: `${label} ${dataset?.name}`,
              }

              setItems([item])
            } else {
              return false
            }
          }}
          placeholder={t('dataset.add.form.copy.placeholder')}
          showCheckedStrategy={Cascader.SHOW_CHILD}
        />
      </Form.Item>
      <SubmitBtn />
    </Form>
  )
}
export default Copy

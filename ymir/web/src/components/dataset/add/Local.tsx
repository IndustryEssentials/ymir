import { FC, useEffect, useState } from 'react'
import { useSelector } from 'umi'
import { Types } from './AddTypes'
import { Button, Form } from 'antd'
import useRequest from '@/hooks/useRequest'
import { ImportingItem } from '@/constants'
import t from '@/utils/t'
import Uploader from '@/components/form/uploader'
import Tip from './Tip'
import { formLayout } from '@/config/antd'
import SubmitBtn from './SubmitBtn'

const Local: FC = () => {
  const [form] = Form.useForm()
  const [key, setKey] = useState(0)
  const [items, setItems] = useState<ImportingItem[]>([])
  const max = useSelector(({ dataset }) => dataset.importing.max)
  const { run: addImportingList } = useRequest('dataset/addImportingList', { loading: false })

  return (
    <Form
      form={form}
      key={key}
      {...formLayout}
      onFinish={() => {
        addImportingList(items)
        setItems([])
        setKey(Math.random())
      }}
      onFinishFailed={(err) => {
        console.log('finish failed: ', err)
      }}
    >
      <Form.Item required label={t('dataset.add.form.upload.btn')}>
        <Uploader
          max={1024}
          maxCount={max}
          onChange={({ fileList }) => {
            const items = fileList
              .map((file) => {
                return file.url
                  ? {
                      type: Types.LOCAL,
                      name: file.name.replace(/\.zip$/i, ''),
                      source: file.url,
                      sourceName: file.name,
                    }
                  : undefined
              })
              .filter<ImportingItem>((item): item is ImportingItem => !!item)
            setItems(items)
          }}
          info={<Tip type={Types.LOCAL} />}
        ></Uploader>
      </Form.Item>
      <SubmitBtn />
    </Form>
  )
}

export default Local

import { FC, useEffect, useState } from 'react'
import { useSelector } from 'umi'
import { Types } from './AddTypes'
import { Button, Form } from 'antd'
import useRequest from '@/hooks/useRequest'
import { formLayout } from '@/config/antd'
import SubmitBtn from './SubmitBtn'
import { ImportingItem } from '@/constants'
import t from '@/utils/t'
import Uploader, { UploadFile } from '@/components/form/uploader'
import Tip from './Tip'

const Local: FC = () => {
  const [form] = Form.useForm()
  const [key, setKey] = useState(0)
  const [items, setItems] = useState<ImportingItem[]>([])
  const max = useSelector(({ dataset }) => dataset.importing.max)
  const { run: addImportingList } = useRequest('dataset/addImportingList', { loading: false })
  const { run: setEditing } = useRequest<null, [boolean]>('dataset/updateImportingEditState', { loading: false })

  useEffect(() => setEditing(!!items.length), [items])

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
            setEditing(true)
            if (fileList.every(({ status }) => status !== 'uploading')) {
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
                .filter((item) => !!item) as ImportingItem[]
              setItems(items)
            }
          }}
          info={<Tip type={Types.LOCAL} />}
        ></Uploader>
      </Form.Item>
      <SubmitBtn disabled={!items.length} />
    </Form>
  )
}

export default Local

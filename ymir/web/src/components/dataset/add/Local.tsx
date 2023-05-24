import { FC, useEffect, useState } from 'react'
import { useSelector } from 'umi'
import { Types } from './AddTypes'
import { Button, Form } from 'antd'
import useRequest from '@/hooks/useRequest'
import { ImportingItem } from '@/constants'
import t from '@/utils/t'
import Uploader from '@/components/form/uploader'
import Tip from './Tip'

const Local: FC = () => {
  const [key, setKey] = useState<number>()
  const [items, setItems] = useState<ImportingItem[]>([])
  const max = useSelector(({ dataset }) => dataset.importing.max)
  const { run: addImportingList } = useRequest('dataset/addImportingList', { loading: false })

  return (
    <Form.Item label={t('dataset.add.form.upload.btn')}>
      <Uploader
        key={key}
        max={1024}
        maxCount={max}
        onChange={({ fileList }) => {
          console.log('fileList:', fileList)
          const items = fileList
            .map((file) => {
              return file.url
                ? {
                    type: Types.LOCAL,
                    name: file.name,
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
      <Button
        type="primary"
        onClick={() => {
          addImportingList(items)
          setKey(Math.random())
        }}
      >
        Add to List
      </Button>
    </Form.Item>
  )
}

export default Local

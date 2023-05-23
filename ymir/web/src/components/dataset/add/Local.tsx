import { FC, useState } from 'react'
import Uploader from '@/components/form/uploader'
import { Types } from './AddTypes'
import { Button } from 'antd'
import useRequest from '@/hooks/useRequest'
import { ImportingItem } from '@/constants'
import { useSelector } from 'umi'

const Local: FC = () => {
  const [key, setKey] = useState<number>()
  const [items, setItems] = useState<ImportingItem[]>([])
  const max = useSelector(({ dataset }) => dataset.importing.max)
  const { run: addImportingList } = useRequest('dataset/addImportingList', { loading: false })
  return (
    <>
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
    </>
  )
}

export default Local

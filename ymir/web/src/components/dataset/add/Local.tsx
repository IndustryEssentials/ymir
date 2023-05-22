import { FC, useState } from 'react'
import Uploader from '@/components/form/uploader'
import { ImportItem, ImportSelectorProps } from '.'
import { Types } from './AddTypes'
import { Button } from 'antd'

const Local: FC<ImportSelectorProps> = ({ confirm }) => {
  const [items, setItems] = useState<ImportItem[]>([])
  return (
    <>
      <Uploader
        max={1024}
        maxCount={6}
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
            .filter<ImportItem>((item): item is ImportItem => !!item)
          setItems(items)
        }}
      ></Uploader>
      <Button type="primary" onClick={() => confirm(items)}>
        Add to List
      </Button>
    </>
  )
}

export default Local

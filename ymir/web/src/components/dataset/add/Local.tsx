import { FC } from 'react'
import Uploader from '@/components/form/uploader'
import { ImportItem, ImportSelectorProps } from '.'
import { Types } from './AddTypes'

const Local: FC<ImportSelectorProps> = ({ onChange }) => {
  return (
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
        onChange(items)
      }}
    ></Uploader>
  )
}

export default Local

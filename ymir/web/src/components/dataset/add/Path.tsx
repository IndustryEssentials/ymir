import { FC } from 'react'
import t from '@/utils/t'
import { ImportSelectorProps } from '.'
import { Types } from './AddTypes'
import Inputs from './Inputs'

const Path: FC<ImportSelectorProps> = ({ onChange }) => {
  return (
    <Inputs
      name="path"
      onChange={(paths) => {
        const items = paths
          .filter((item) => !!item)
          .map((path) => ({
            type: Types.NET,
            name: path,
            source: path,
            sourceName: path,
          }))
        onChange(items)
      }}
      rules={[
        {
          required: true,
          message: t('dataset.add.form.path.placeholder'),
        },
      ]}
      tip={
        <p>
          {
            //renderTip('path')
          }
        </p>
      }
    />
  )
}
export default Path

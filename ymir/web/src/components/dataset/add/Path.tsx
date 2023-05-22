import { FC } from 'react'
import t from '@/utils/t'
import { ImportSelectorProps } from '.'
import { Types } from './AddTypes'
import Inputs from './Inputs'

const Path: FC<ImportSelectorProps> = ({ confirm }) => {
  return (
    <Inputs
      name="path"
      confirm={(paths) => {
        const items = paths
          .filter((item) => !!item)
          .map((path) => ({
            type: Types.PATH,
            name: path,
            source: path,
            sourceName: path,
          }))
        confirm(items)
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

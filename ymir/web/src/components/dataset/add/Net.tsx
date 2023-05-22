import { urlValidator } from '@/components/form/validators'
import { FC } from 'react'
import t from '@/utils/t'
import { ImportSelectorProps } from '.'
import { Types } from './AddTypes'
import Inputs from './Inputs'

const Net: FC<ImportSelectorProps> = ({ confirm }) => {
  return (
    <Inputs
      name="net"
      confirm={(urls) => {
        const items = urls
          .filter((item) => !!item)
          .map((url) => ({
            type: Types.NET,
            name: url,
            source: url,
            sourceName: url,
          }))
        confirm(items)
      }}
      rules={[
        {
          required: true,
          message: t('dataset.add.form.net.placeholder'),
        },
        { validator: urlValidator },
      ]}
      tip={<p>hello</p>}
    />
  )
}

export default Net

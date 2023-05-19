import { urlValidator } from '@/components/form/validators'
import { FC } from 'react'
import t from '@/utils/t'
import { ImportSelectorProps } from '.'
import { Types } from './AddTypes'
import Inputs from './Inputs'

const Net: FC<ImportSelectorProps> = ({ onChange }) => {
  return (
    <Inputs
      name="net"
      onChange={(urls) => {
        const items = urls
          .filter((item) => !!item)
          .map((url) => ({
            type: Types.NET,
            name: url,
            source: url,
            sourceName: url,
          }))
        onChange(items)
      }}
      rules={[
        {
          required: true,
          message: t('dataset.add.form.net.placeholder'),
        },
        { validator: urlValidator },
      ]}
      tip={
        <p>
          {
            //renderTip('net')
          }
        </p>
      }
    />
  )
}
export default Net

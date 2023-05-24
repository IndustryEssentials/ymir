import { urlValidator } from '@/components/form/validators'
import { FC, useState } from 'react'
import t from '@/utils/t'
import { Types } from './AddTypes'
import Inputs from './Inputs'
import { useSelector } from 'umi'
import useRequest from '@/hooks/useRequest'
import Tip from './Tip'

const Net: FC = () => {
  const max = useSelector(({ dataset }) => dataset.importing.max)
  const { run: addImportingList } = useRequest('dataset/addImportingList', { loading: false })
  return (
    <Inputs
      name="net"
      max={max}
      confirm={(urls) => {
        const items = urls
          .filter((item) => !!item)
          .map((url) => ({
            type: Types.NET,
            name: url,
            source: url,
            sourceName: url,
          }))
        addImportingList(items)
      }}
      rules={[
        {
          required: true,
          message: t('dataset.add.form.net.placeholder'),
        },
        { validator: urlValidator },
      ]}
      tip={<Tip type={Types.NET} />}
    />
  )
}

export default Net

import { FC } from 'react'
import t from '@/utils/t'
import { Types } from './AddTypes'
import Inputs from './Inputs'
import { useSelector } from 'umi'
import useRequest from '@/hooks/useRequest'

const Path: FC = () => {
  const max = useSelector(({ dataset }) => dataset.importing.max)
  const { run: addImportingList } = useRequest('dataset/addImportingList', { loading: false })
  return (
    <Inputs
      name="path"
      max={max}
      confirm={(paths) => {
        const items = paths
          .filter((item) => !!item)
          .map((path) => ({
            type: Types.PATH,
            name: path,
            source: path,
            sourceName: path,
          }))
        addImportingList(items)
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

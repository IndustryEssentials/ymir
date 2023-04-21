import { ColumnType } from 'antd/lib/table'

import StrongTitle from './StrongTitle'
import ImageName from '@/components/image/ImageName'
import { Prediction } from '@/constants'

const Image = <T extends Prediction>(): ColumnType<T> => ({
  title: <StrongTitle label="pred.column.image" />,
  dataIndex: 'image',
  render: (_, { task, projectId }) => {
    const id = task.parameters.docker_image_id
    return <ImageName id={id} />
  },
})

export default Image

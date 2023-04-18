import { ColumnType } from 'antd/lib/table'
import { Link } from 'umi'

import StrongTitle from './StrongTitle'
import ImageName from '@/components/image/ImageName'

const Image = <T extends YModels.Prediction>(): ColumnType<T> => ({
  title: <StrongTitle label="pred.column.image" />,
  dataIndex: 'image',
  render: (_, { task, projectId }) => {
    const id = task.parameters.docker_image_id
    return <ImageName id={id} />
  },
})

export default Image

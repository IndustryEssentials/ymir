import { FC } from 'react'
import { Image } from '@/constants'
import { Space } from 'antd'
import { Link } from 'umi'

const ImagesLink: FC<{ images?: Image[] }> = ({ images = [] }) => {
  return images.length ? (
    <Space>
      {images.map((image) => (
        <Link key={image.id} to={`/home/image/detail/${image.id}`}>
          {image.name}
        </Link>
      ))}
    </Space>
  ) : null
}

export default ImagesLink

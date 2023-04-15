import useFetch from '@/hooks/useFetch'
import React, { useEffect } from 'react'
import { Link, useSelector } from 'umi'

type Props = {
  id?: number
  url?: string
}
const ImageName: React.FC<Props> = ({ id, url = '' }) => {
  if (url) {
    return <>${url}</>
  }
  const image = useSelector(({ image }) => {
    return id ? image.image[id] : undefined
  })
  const [_, getImage] = useFetch('image/getImage')

  useEffect(() => id && getImage({ id }), [id])

  const label = image?.name ? `${image?.name}` : `${id}`
  return (
    <Link to={`/home/image/${id}`} className={'imageName'} title={image?.url}>
      {label}
    </Link>
  )
}

export default ImageName

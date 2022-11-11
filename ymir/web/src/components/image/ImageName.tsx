import useFetch from '@/hooks/useFetch'
import React, { useEffect } from 'react'
import { useSelector } from 'umi'

type Props = {
  id: number
}
const ImageName: React.FC<Props> = ({ id }) => {
  const image: YModels.Image = useSelector(({ image }: YStates.Root) => {
    return id && image.image[id]
  })
  const [_, getImage] = useFetch('image/getImage')

  useEffect(() => id && getImage({ id }), [id])

  const label = image?.name ? `${image?.name}` : `${id}`
  return (
    <span className={'imageName'} title={image?.url}>
      {label}
    </span>
  )
}

export default ImageName

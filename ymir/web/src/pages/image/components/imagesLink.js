import { Space } from "antd"
import { Link } from "umi"

const ImagesLink = ({ images = [] }) => {
  return images.length ?
    <Space>{images.map(image => <Link key={image.id} to={`/home/image/detail/${image.id}`}>{image.name}</Link>)}</Space> :
    null
}

export default ImagesLink

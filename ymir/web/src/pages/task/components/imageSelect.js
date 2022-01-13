import { Select } from 'antd'
import { connect } from 'dva'
import { useEffect, useState } from 'react'

import { TYPES } from '@/constants/image'

const ImageSelect = ({ value, type = TYPES.TRAINING, onChange = () => {}, getImages, ...resProps }) => {
  const [options, setOptions] = useState([])

  useEffect(() => {
    fetchImages()
  }, [])

  useEffect(() => {
    if (options.length === 1) {
      value = options[0].value
    }
  }, [options])

  async function fetchImages() {
    const params = {
      type,
      offset: 0,
      limit: 100000,
    }
    const result = await getImages(params)
    if (result) {
      const images = result.items
      const opts = images.map(image => {
        return {
          label: image.name,
          image,
          value: image.id,
        }
      })
      setOptions(opts)
      if (value) {
        const opt = opts.find(opt => opt.value === value)
        onChange(opt.value, opt.image)
      }
    }
  }

  return (
    <Select value={value} {...resProps} onChange={(value, opt) => onChange(value, opt?.image)} options={options} allowClear></Select>
  )
}

const actions = (dispatch) => {
  return {
    getImages(payload) {
      return dispatch({
        type: 'image/getImages',
        payload,
      })
    }
  }
}
export default connect(null, actions)(ImageSelect)

import { Col, Row, Select } from 'antd'
import { connect } from 'dva'
import { useEffect, useState } from 'react'

import { TYPES } from '@/constants/image'
import { HIDDENMODULES } from '@/constants/common'
import t from '@/utils/t'

const ImageSelect = ({ value, relatedId, type = TYPES.TRAINING, onChange = () => {}, getImages, getImage, ...resProps }) => {
  const [options, setOptions] = useState([])

  useEffect(() => {
    fetchImages()
  }, [])

  useEffect(() => {
    if (options.length === 1) {
      if (value) {
        const opt = options.find(({ image }) => image.id === value)
        opt && onChange(value, opt.image)
      } else {
        value = options[0].value
      }
    }
  }, [options])

  useEffect(() => {
    if (value) {
      const opt = options.find(({ image }) => image.id === value)
      opt && onChange(value, opt.image)
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
      generateOptions(images)
    }
  }

  const generateOption = (image) => ({
    label: (
      <Row>
        <Col flex={1}>{image.name}</Col>
        {!HIDDENMODULES.LIVECODE ? (
          <Col style={{ color: 'rgba(0, 0, 0, 0.45)' }}>{t(`image.livecode.label.${image.liveCode ? 'remote' : 'local'}`)}</Col>
        ) : null}
      </Row>
    ),
    image,
    value: image.id,
  })

  async function generateOptions(images) {
    let relatedOptions = relatedId ? await getRelatedOptions() : []
    const opts = images.filter((image) => relatedOptions.every((img) => img.value !== image.id)).map(generateOption)
    let result = opts
    if (relatedOptions.length) {
      result = [
        {
          label: t('image.select.opt.related'),
          options: relatedOptions,
        },
        {
          label: t('image.select.opt.normal'),
          options: opts,
        },
      ]
    }
    setOptions(result)
  }

  async function getRelatedOptions() {
    const trainImage = await getImage({ id: relatedId })
    let relatedOptions = []
    if (trainImage?.related) {
      relatedOptions = trainImage.related.map(generateOption)
    }
    return relatedOptions
  }

  return (
    <Select value={value} optionFilterProp="label" allowClear {...resProps} onChange={(value, opt) => onChange(value, opt?.image)} options={options}></Select>
  )
}

const actions = (dispatch) => {
  return {
    getImages(payload) {
      return dispatch({
        type: 'image/getImages',
        payload,
      })
    },
    getImage(payload) {
      return dispatch({
        type: 'image/getImage',
        payload,
      })
    },
  }
}
export default connect(null, actions)(ImageSelect)

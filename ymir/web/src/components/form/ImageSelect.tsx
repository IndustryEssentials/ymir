import { Col, Row, Select, SelectProps } from 'antd'
import { FC, UIEvent, UIEventHandler, useCallback, useEffect, useState } from 'react'

import { TYPES } from '@/constants/image'
import { HIDDENMODULES } from '@/constants/common'
import t from '@/utils/t'
import useRequest from '@/hooks/useRequest'
import { QueryParams } from '@/services/image'
import { DefaultOptionType } from 'antd/lib/select'

interface Props extends SelectProps {
  pid: number
  relatedId?: number
  type?: TYPES
}

type OptionType = DefaultOptionType & {
  image?: YModels.Image
}

const ImageSelect: FC<Props> = ({ value, pid, relatedId, type = TYPES.TRAINING, onChange = () => {}, ...resProps }) => {
  const [options, setOptions] = useState<OptionType[]>([])
  const { data: list, run: getImages } = useRequest<YModels.ImageList, [QueryParams]>('image/getImages', {
    loading: false,
  })
  const { data: trainImage, run: getRelatedImage } = useRequest<YModels.Image, [{ id: number }]>('image/getImage', {
    loading: false,
  })
  const { data: project, run: getProject } = useRequest<YModels.Project, [{ id: number }]>('project/getProject', {
    cacheKey: 'getProject',
    loading: false,
  })

  useEffect(() => {
    pid && getProject({ id: pid })
  }, [pid])

  useEffect(() => {
    if (list?.items?.length) {
      const options = generateOptions(list.items)
      setOptions((opts) => [...opts, ...options, ...[
        1, 2,3,4,5,6,7,8, 10, 11, 'helldssfjldfk'
      ].map(i => ({ value: i, label: i }))])
    }
  }, [list])

  useEffect(() => {
    relatedId && getRelatedImage({ id: relatedId })
  }, [relatedId])

  useEffect(() => {
    project?.type && fetchImages()
  }, [project])

  useEffect(() => {
    if (options.length === 1) {
      if (!value) {
        value = options[0].value
      }
    }
  }, [options])

  useEffect(() => {
    if (value) {
      const opt = options.find(({ image }) => image?.id === value)
      opt && onChange(value, opt)
    }
  }, [options])

  const fetchImages = useCallback(
    (page = 1) => {
      if (!project) {
        return
      }
      const limit = 10
      const offset = (page - 1) * limit
      const params = {
        type,
        objectType: project.type,
        offset,
        limit,
      }
      getImages(params)
    },
    [project?.type],
  )

  const generateOption = (image: YModels.Image) => ({
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

  const generateOptions = useCallback(
    (images: YModels.Image[]) => {
      const related = trainImage?.related || []
      const opts = images.map(generateOption)
      if (related.length) {
        const defOpts = opts.filter((opt) => related.every(({ id }) => id !== opt.value))
        const relatedOpts = related.map(generateOption)
        return [
          {
            label: t('image.select.opt.related'),
            options: relatedOpts,
          },
          {
            label: t('image.select.opt.normal'),
            options: defOpts,
          },
        ]
      } else {
        return opts
      }
    },
    [trainImage],
  )

  const scrollChange = (e: UIEvent<HTMLDivElement>) => {
    e.persist()
    const target = e.currentTarget
    console.log('target:', e, target.scrollTop)
    // const top = target.scrollTop || 0

    if (target.scrollTop + target.offsetHeight === target.scrollHeight) {
    }
  }

  return (
    <Select
      value={value}
      optionFilterProp="label"
      allowClear
      {...resProps}
      onChange={(value, opt) => onChange(value, opt)}
      onPopupScroll={scrollChange}
      options={options}
    ></Select>
  )
}

export default ImageSelect

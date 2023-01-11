import { Col, Row, Select, SelectProps } from 'antd'
import { FC, UIEvent, UIEventHandler, useCallback, useEffect, useState } from 'react'

import { TYPES } from '@/constants/image'
import { HIDDENMODULES } from '@/constants/common'
import t from '@/utils/t'
import useRequest from '@/hooks/useRequest'
import { QueryParams } from '@/services/image'
import { DefaultOptionType } from 'antd/lib/select'
import { useDebounce } from 'ahooks'

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
  const [groupOptions, setGroupOptions] = useState<{ label: string; options?: OptionType[] }[]>([])
  const [query, setQuery] = useState<QueryParams>({
    type,
    limit: 10,
    offset: 0,
  })
  const [name, setSearchName] = useState<string>()
  const searchName = useDebounce(name, { wait: 400 })
  const [total, setTotal] = useState(0)
  const {
    data: list,
    run: getImages,
    loading,
  } = useRequest<YModels.ImageList, [QueryParams]>('image/getImages', {
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
      const items = list.items.filter((item) => options.every((opt) => opt.value !== item.id))
      const opts = generateOptions(items)
      setOptions((options) => [...options, ...opts])
    }
    list && setTotal(list?.total)
  }, [list])

  useEffect(() => {
    relatedId && getRelatedImage({ id: relatedId })
  }, [relatedId])

  useEffect(() => {
    if (trainImage?.related) {
      const related = trainImage?.related || []
      if (related.length) {
        const defOpts = options.filter((opt) => related.every(({ id }) => id !== opt.value))
        const relatedOpts = related.map(generateOption)
        const groupOptions = [
          {
            label: t('image.select.opt.related'),
            options: relatedOpts,
          },
          {
            label: t('image.select.opt.normal'),
            options: defOpts,
          },
        ]
        setGroupOptions(groupOptions)
      }
    }
  }, [options, trainImage])

  useEffect(() => {
    project && setQuery((query) => ({ ...query, objectType: project.type }))
  }, [project])

  useEffect(() => {
    setOptions([])
    setQuery((query) => ({ ...query, offset: 0, name: searchName }))
  }, [searchName])

  useEffect(() => {
    fetchImages()
  }, [query])

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

  const fetchImages = () => {
    if (!project) {
      return
    }
    getImages(query)
  }

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

  const generateOptions = (images: YModels.Image[]) => images.map(generateOption)

  const scrollChange = (e: UIEvent<HTMLDivElement>) => {
    e.persist()
    const target = e.currentTarget

    if (target.scrollTop + target.offsetHeight === target.scrollHeight) {
      const offset = (query.offset || 0) + (query.limit || 10)
      if (offset <= total) {
        setQuery((query) => ({ ...query, offset }))
      }
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
      options={groupOptions.length ? groupOptions : options}
      loading={loading}
      onSearch={setSearchName}
      showSearch
      filterOption={false}
    ></Select>
  )
}

export default ImageSelect

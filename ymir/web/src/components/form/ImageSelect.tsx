import { Col, Row, Select, SelectProps } from 'antd'
import { FC, UIEvent, UIEventHandler, useCallback, useEffect, useState } from 'react'

import { TYPES } from '@/constants/image'
import { HIDDENMODULES, validState } from '@/constants/common'
import t from '@/utils/t'
import useRequest from '@/hooks/useRequest'
import { QueryParams } from '@/services/typings/image.d'
import { DefaultOptionType } from 'antd/lib/select'
import { useDebounce } from 'ahooks'
import { Image } from '@/constants'
import { List } from '@/models/typings/common'
import { useSelector } from 'umi'
import { ObjectType } from '@/constants/objectType'

interface Props extends SelectProps {
  pid: number
  relatedId?: number
  type?: TYPES
  fixedSelected?: number
}

type OptionType = DefaultOptionType & {
  value?: number
  image?: Image
  objectType?: ObjectType
}

type GO = OptionType

const ImageSelect: FC<Props> = ({ value, pid, relatedId, type = TYPES.TRAINING, onChange = () => {}, fixedSelected, ...resProps }) => {
  const [options, setOptions] = useState<OptionType[]>([])
  const [groupOptions, setGroupOptions] = useState<OptionType[]>([])
  const [selected, setSelected] = useState<number>()
  const [query, setQuery] = useState<QueryParams>({
    type,
    limit: 10,
    offset: 0,
  })
  const [name, setSearchName] = useState<string>()
  const searchName = useDebounce(name, { wait: 400 })
  const [total, setTotal] = useState(0)
  const { official } = useSelector(({ image }) => image)
  const {
    data: list,
    run: getImages,
    loading,
  } = useRequest<List<Image>, [QueryParams]>('image/getImages', {
    loading: false,
  })
  const { data: trainImage, run: getRelatedImage } = useRequest<Image, [{ id: number }]>('image/getImage', {
    loading: false,
  })
  useRequest<Image, [{ id: number }]>('image/getOfficialImage', {
    loading: false,
    manual: false,
    loadingDelay: 500,
  })
  const { data: project, run: getProject } = useRequest<YModels.Project, [{ id: number }]>('project/getProject', {
    cacheKey: 'getProject',
    loading: false,
  })

  useEffect(() => {
    if (project?.recommendImage) {
      setSelected(project?.recommendImage)
    } else if (value) {
      setSelected(value)
    } else if (official && validState(official.state)) {
      setSelected(official.id)
    } else {
      setSelected(undefined)
    }
  }, [value, official, project?.recommendImage])

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
      if (!selected) {
        setSelected(options[0].value)
      }
    }
  }, [options])

  useEffect(() => {
    if (options.length && selected) {
      const opt = options.find(({ image }) => image?.id === selected)
      if (opt) {
        onChange(selected, opt)
      } else {
        setSelected(undefined)
      }
    }
  }, [options, selected])

  const fetchImages = () => {
    if (!project) {
      return
    }
    getImages(query)
  }

  const generateOption = useCallback((image: Image) => ({
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
    objectType: project?.type,
  }), [project])

  const generateOptions = (images: Image[]) => images.map(generateOption)

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
    <Select<number, OptionType>
      optionFilterProp="label"
      allowClear
      {...resProps}
      value={selected}
      onChange={onChange}
      onPopupScroll={scrollChange}
      options={groupOptions.length ? groupOptions : options}
      loading={loading}
      onSearch={setSearchName}
      showSearch
      filterOption={false}
      disabled={!!project?.recommendImage}
    ></Select>
  )
}

export default ImageSelect

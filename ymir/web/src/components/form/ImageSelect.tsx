import { Col, Row, Select, SelectProps } from 'antd'
import { FC, UIEvent, UIEventHandler, useCallback, useEffect, useState } from 'react'

import { TYPES } from '@/constants/image'
import { HIDDENMODULES, validState } from '@/constants/common'
import t from '@/utils/t'
import useRequest from '@/hooks/useRequest'
import { DefaultOptionType } from 'antd/lib/select'
import { useDebounce } from 'ahooks'
import { Image, Project } from '@/constants'
import { List } from '@/models/typings/common.d'
import { useSelector } from 'umi'
import { isMultiModal, ObjectType } from '@/constants/objectType'
import { QueryParams } from '@/services/typings/image.d'
import LLMM from '@/constants/llmm'

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
  const { official, trainImage, sampleImage } = useSelector(({ image }) => ({
    ...image,
    trainImage: relatedId ? image.image[relatedId] : undefined,
    sampleImage: project?.recommendImage ? image.image[project?.recommendImage] : undefined,
  }))
  const {
    data: list,
    run: getImages,
    loading,
  } = useRequest<List<Image>, [QueryParams]>('image/getImages', {
    loading: false,
  })
  const { run: getImage } = useRequest<Image, [{ id: number }]>('image/getImage', {
    loading: false,
  })
  const { run: getOfficialImage } = useRequest<Image>('image/getOfficialImage', {
    loading: false,
    loadingDelay: 500,
  })
  const { data: project, run: getProject } = useRequest<Project, [{ id: number }]>('project/getProject', {
    cacheKey: 'getProject',
    loading: false,
  })

  useEffect(() => {
    if (project?.recommendImage) {
      setSelected(project?.recommendImage)
    } else if (value) {
      setSelected(value)
    } else if (!isMultiModal(project?.type) && official && validState(official.state)) {
      setSelected(official.id)
    } else {
      setSelected(undefined)
    }
  }, [value, official, project?.recommendImage, project?.type])

  useEffect(() => {
    pid && getProject({ id: pid })
  }, [pid])

  useEffect(() => {
    project?.type && !isMultiModal(project.type) && getOfficialImage()
  }, [project?.type])

  useEffect(() => {
    project?.recommendImage && getImage({ id: project.recommendImage })
  }, [project?.recommendImage])

  useEffect(() => {
    if (list?.items?.length) {
      let items = list.items
      if (sampleImage) {
        items = withPriorityImage(list.items, sampleImage)
      }
      if (project?.type && !isMultiModal(project?.type) && official) {
        items = withPriorityImage(items, official)
      }
      if (isMultiModal(project?.type) && type === TYPES.INFERENCE) {
        items = items.filter((item) => item.url !== LLMM.GroundedSAMImageUrl)
      }
      items = items.filter((item) => options.every((opt) => opt.value !== item.id))
      const opts = generateOptions(items)
      setOptions((options) => [...options, ...opts])
    }
    list && setTotal(list?.total)
  }, [list, official, sampleImage, project?.type])

  useEffect(() => {
    relatedId && getImage({ id: relatedId })
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

  const withPriorityImage = (list: Image[], image?: Image) => (image ? [image, ...list.filter(({ id }) => id !== image.id)] : list)

  const generateOption = useCallback(
    (image: Image) => ({
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
    }),
    [project],
  )

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

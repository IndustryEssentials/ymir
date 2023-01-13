import { Cascader, CascaderProps, Col, Row, Select } from 'antd'
import { useParams } from 'umi'
import t from '@/utils/t'
import { FC, useEffect, useState } from 'react'

enum Type {
  keywords = 'keywords',
  cks = 'cks',
  tags = 'tags',
}
type Props = {
  value: string[] | string[][]
  onChange?: (value: { type: Type; selected?: (string | string[])[] }) => void
  dataset: YModels.Dataset
}
type KeywordOptionsType = {
  [key in Type]: KeywordOption[]
}

type KeywordOption = {
  value: string
  label: string
  children?: KeywordOption[]
  hidden?: boolean
}
type TypeOption = KeywordOption & {
  value: Type
}

const labels = { [Type.keywords]: 'keywords', [Type.cks]: 'cks', [Type.tags]: 'tags' }

const types = [Type.keywords, Type.cks, Type.tags]

const visibleTypes = (types: TypeOption[]) => types.filter(({ hidden }) => !hidden)

const KeywordSelector: FC<Props> = ({ value, onChange, dataset }) => {
  const [typeOptions, setTypeOptions] = useState<TypeOption[]>(
    types.map((value) => ({ value, label: t(`dataset.assets.keyword.selector.types.${labels[value]}`) })),
  )
  const [kwOptions, setKwOptions] = useState<KeywordOptionsType>({
    [Type.keywords]: [],
    [Type.cks]: [],
    [Type.tags]: [],
  })
  const [currentType, setCurrentType] = useState<Type>(Type.keywords)
  const [selected, setSelected] = useState<string[]>([])
  const [ckSelected, setCkSelected] = useState<string[][]>([])

  useEffect(() => {
    if (value) {
      if (value?.length) {
        const isCk = Array.isArray(value[0])
        if (isCk) {
          setCkSelected(value as string[][])
        } else {
          setSelected(value as string[])
        }
      } else {
        setCkSelected([])
        setSelected([])
      }
    }
  }, [value])

  useEffect(() => {
    const validTypes = visibleTypes(typeOptions).map(({ value }) => value)
    if (!validTypes?.includes(currentType)) {
      setCurrentType(validTypes[0])
    }
  }, [typeOptions])

  useEffect(() => {
    setTypeOptions((types) => types.map((opt) => ({ ...opt, hidden: !kwOptions[opt.value].length })))
  }, [kwOptions])

  useEffect(() => {
    if (!dataset.id) {
      return
    }
    const ck2opts = (kws: YModels.CKItem[] = []): KeywordOption[] =>
      kws.map(({ keyword, children }) => ({ value: keyword, label: keyword, children: ck2opts(children) }))
    setKwOptions({
      [Type.keywords]: dataset.keywords.map((keyword) => ({ value: keyword, label: keyword })),
      [Type.cks]: ck2opts(dataset?.cks?.keywords),
      [Type.tags]: ck2opts(dataset?.tags?.keywords),
    })
  }, [dataset])

  useEffect(() => {
    onChange && onChange({ type: currentType, selected })
  }, [selected])

  useEffect(() => {
    onChange && onChange({ type: currentType, selected: ckSelected })
  }, [ckSelected])

  useEffect(() => {
    setSelected([])
    setCkSelected([])
  }, [currentType])

  const renderKeywords = (type: Type) => {
    const targetOptions = kwOptions[type]
    return type !== Type.keywords ? renderCk(targetOptions) : renderKw(targetOptions)
  }

  const renderKw = (list: KeywordOption[] = []) => (
    <Select
      showSearch
      value={selected}
      mode="multiple"
      allowClear
      style={{ width: 160 }}
      onChange={setSelected}
      placeholder={t('dataset.assets.keyword.selector.types.placeholder')}
      options={list}
    />
  )

  const renderCk = (list: KeywordOption[] = []) => (
    <Cascader
      value={ckSelected}
      multiple
      allowClear
      expandTrigger="hover"
      onChange={(value: unknown) => setCkSelected(value as string[][])}
      options={list}
      placeholder={t('dataset.assets.keyword.selector.types.placeholder')}
    />
  )

  return visibleTypes(typeOptions).length ? (
    <Row gutter={10}>
      <Col style={{ width: 150 }}>
        <Select style={{ width: '100%' }} value={currentType} onChange={setCurrentType} options={visibleTypes(typeOptions)} />
      </Col>
      <Col flex={1}>{renderKeywords(currentType)}</Col>
    </Row>
  ) : null
}

export default KeywordSelector

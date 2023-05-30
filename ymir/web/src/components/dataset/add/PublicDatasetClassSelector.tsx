import { Form, Select } from 'antd'
import { FC, useState, useEffect } from 'react'
import t from '@/utils/t'
import { useSelector } from 'umi'
import useRequest from '@/hooks/useRequest'

type Props = { id: number; onChange: (classes: string[]) => void }

const PublicDatasetClassSelector: FC<Props> = ({ id, onChange }) => {
  const dataset = useSelector(({ dataset }) => {
    return dataset.publicDatasets.items?.find((ds) => ds.id === id)
  })
  const [classes, setClasses] = useState<string[]>([])
  const { data: { newer } = {}, run: checkKeywords } = useRequest<{ newer: string[] }>('keyword/checkDuplication')

  useEffect(() => {
    dataset?.keywords.length && checkKeywords(dataset.keywords)
  }, [dataset])

  useEffect(() => {
    newer && setClasses(newer)
  }, [newer])

  useEffect(() => {
    onChange(classes)
  }, [classes])

  return newer?.length ? (
    <Form.Item label={t('dataset.import.public.include')}>
      <Select mode="multiple" defaultValue={newer} options={newer.map((kw) => ({ value: kw, label: kw }))} onChange={setClasses}></Select>
    </Form.Item>
  ) : null
}
export default PublicDatasetClassSelector

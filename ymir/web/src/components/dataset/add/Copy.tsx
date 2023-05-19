import ProjectDatasetSelect from '@/components/form/ProjectDatasetSelect'
import { FC, useState, useEffect } from 'react'
import t from '@/utils/t'
import { ImportSelectorProps } from '.'
import { useParams } from 'umi'
import { Types } from './AddTypes'
const Copy: FC<ImportSelectorProps> = ({ onChange }) => {
  const params = useParams<{ id: string }>()

  useEffect(() => {}, [])
  return (
    <ProjectDatasetSelect
      multiple
      onChange={(_, options) => {
        const datasets = options.map((opt) => opt[1]?.dataset)
        const items = datasets.map((ds) => ({
          type: Types.COPY,
          name: ds.name,
          source: ds.id,
          sourceName: ds.name,
        }))
        onChange(items)
      }}
      placeholder={t('dataset.add.form.copy.placeholder')}
    />
  )
}
export default Copy

import { Form, Select } from 'antd'
import { FC, useState, useEffect } from 'react'
import t from '@/utils/t'
import { useSelector } from 'umi'
import useRequest from '@/hooks/useRequest'
import Dataset from '@/components/form/option/Dataset'
type Props = {
  selected?: number
}
const Public: FC<Props> = ({ selected }) => {
  const { data: publicDatasets, run: getPublicDatasets } = useRequest('dataset/getPublicDatasets', {
    loading: false,
  })

  useEffect(() => {}, [])
  return (
    <>
      <Form.Item
        label={t('dataset.add.form.internal.label')}
        tooltip={t('tip.task.filter.datasets')}
        name="did"
        initialValue={selected}
        rules={[
          {
            required: true,
            message: t('dataset.add.form.internal.required'),
          },
        ]}
      >
        <Select
          placeholder={t('dataset.add.form.internal.placeholder')}
          onChange={onInternalDatasetChange}
          options={publicDatasets.map((dataset) => ({
            value: dataset.id,
            dataset,
            label: <Dataset dataset={dataset} />,
          }))}
        ></Select>
      </Form.Item>

      {selected && newKeywords.length ? (
        <Form.Item label={t('dataset.import.public.include')}>
          <>
            <h4>
              {t('dataset.add.internal.newkeywords.label')}
              <Button type="link" onClick={(e) => updateIgnoredKeywords(e, newKeywords, false)}>
                {t('dataset.add.internal.ignore.all')}
              </Button>
            </h4>
            <div>{renderKeywords(newKeywords)}</div>
          </>
          {ignoredKeywords.length ? (
            <>
              <h4>
                {t('dataset.add.internal.ignorekeywords.label')}
                <Button type="link" onClick={(e) => updateIgnoredKeywords(e, ignoredKeywords, true)}>
                  {t('dataset.add.internal.add.all')}
                </Button>
              </h4>
              <div>{renderKeywords(ignoredKeywords, true)}</div>
            </>
          ) : null}
        </Form.Item>
      ) : null}
    </>
  )
}
export default Public

import { FC, useEffect } from 'react'
import { Space, Tag } from 'antd'
import t from '@/utils/t'
import useRequest from '@/hooks/useRequest'
import s from './common.less'

type Props = {
  global?: boolean
  sets?: number[] | number
  limit?: number
  onSelect?: (keyword: string) => void
}

const RecommendKeywords: FC<Props> = ({ global = false, sets, limit = 5, onSelect = () => {} }) => {
  const { data: keywords = [], run: getKeywords } = useRequest<string[], [{ global?: boolean; dataset_ids: number[]; limit?: number }]>(
    'keyword/getRecommendKeywords',
  )

  useEffect(() => {
    if (global || sets) {
      fetchKeywords(sets)
    }
  }, [sets])

  function fetchKeywords(sets: number | number[] = []) {
    const ids = Array.isArray(sets) ? sets : [sets]
    getKeywords({ global, dataset_ids: ids, limit })
  }

  return (
    <Space className={s.recommendKeywords}>
      <span className={s.label}>{t('common.recommend.keyword.label')}</span>
      {keywords.map((keyword) => (
        <Tag className={s.tag} key={keyword} onClick={() => onSelect(keyword)}>
          {keyword}
        </Tag>
      ))}
    </Space>
  )
}

export default RecommendKeywords

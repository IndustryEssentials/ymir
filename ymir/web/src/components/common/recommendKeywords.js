import { Space, Tag } from 'antd'
import { connect } from 'dva'
import { useEffect, useState } from 'react'

import t from "@/utils/t"
import useFetch from '@/hooks/useFetch'
import s from './common.less'

const RecommendKeywords = ({ global = false, sets, limit = 5, onSelect = () => { } }) => {
  const [keywords, getKeywords] = useFetch('keyword/getRecommendKeywords', [])

  useEffect(() => {
    if (global || sets) {
      fetchKeywords()
    }
  }, [sets])

  function fetchKeywords() {
    const ids = Array.isArray(sets) ? sets : [sets]
    getKeywords({ global, dataset_ids: ids, limit })
  }

  return (
    <Space className={s.recommendKeywords}>
      <span className={s.label}>{t('common.recommend.keyword.label')}</span>
      {keywords.map(keyword => <Tag className={s.tag} key={keyword} onClick={() => onSelect(keyword)}>{keyword}</Tag>)}
    </Space>
  )
}

export default RecommendKeywords

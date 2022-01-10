import { Space, Tag } from 'antd'
import { connect } from 'dva'
import { useEffect, useState } from 'react'

import t from "@/utils/t"
import s from './common.less'

const RecommandKeywords = ({sets = [], onSelect = () => {}, getRecommandKeywords}) => {
  const [keywords, setKeywords] = useState([])

  useEffect(() => {
    fetchKeywords()
  }, [sets])

  async function fetchKeywords() {
    const result = await getRecommandKeywords({ sets })
    if (result) {
      setKeywords(result)
    }
  }

  return (
    <Space className={s.recommandKeywords}>
      <span className={s.label}>{t('common.recommand.keyword.label')}</span>
      {keywords.map(keyword => <Tag className={s.tag} key={keyword} onClick={() => onSelect(keyword)}>{keyword}</Tag>)}
    </Space>
  )
}

const props = (state) => {
  return {

  }
}

const actions = (dispatch) => {
  return {
    getRecommandKeywords(payload) {
      return dispatch({
        type: 'keyword/getRecommandKeywords',
        payload,
      })
    }
  }
}


export default connect(props, actions)(RecommandKeywords)
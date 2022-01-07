import { Space, Tag } from 'antd'
import { connect } from 'dva'
import { useEffect, useState } from 'react'

import s from './common.less'

const RecommandKeywords = ({type = '', onSelected = () => {}, getRecommandKeywords}) => {
  const [keywords, setKeywords] = useState([])

  useEffect(() => {
    fetchKeywords()
  }, [])

  async function fetchKeywords() {
    const result = await getRecommandKeywords({ type })
    if (result) {
      setKeywords(result)
    }
  }

  return (
    <Space>
      <span className={s.recommandKwTitle}>{t('common.recommand.keyword.label')}</span>
      {keywords.map(keyword => <Tag key={keyword}>{keyword}</Tag>)}
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
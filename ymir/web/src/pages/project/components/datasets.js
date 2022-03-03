import { connect } from 'dva'

import List from '@/components/dataset/list'

function Datasets ({}) {
  return <List />
}

const props = state => {
  return {

  }
}

const actions = dispacth => {
  return {

  }
}

export default connect(props, actions)(Datasets)
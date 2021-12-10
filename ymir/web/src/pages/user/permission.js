import { Tabs, Card } from "antd"
import { connect } from "dva"

const { TabPane } = Tabs

const Permission = () => {

  const renderTitle = (<></>)
  return (
    <Card>
      
      <Tabs>
        <TabPane tab='权限管理' key='1'></TabPane>
        <TabPane tab='注册申请' key='2'></TabPane>
      </Tabs>
    </Card>
  )
}

const props = (state) => {
  return {

  }
}
const actions = (dispatch) => {
  return {}
}
export default connect(props, actions)(Permission)
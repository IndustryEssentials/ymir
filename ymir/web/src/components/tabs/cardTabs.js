import { Card } from "antd"
import { useEffect, useState } from "react"
import { useLocation, useHistory } from "umi"

export const CardTabs = ({ data = [], initialTab, ...props }) => {
  const location = useLocation()
  const history = useHistory()
  const [tabs, setTabs] = useState([])
  const [contents, setContents] = useState({})
  const [active, setActive] = useState(null)

  useEffect(() => (tabs.length && !active) && setActive(initialTab || tabs[0].key), [tabs])
  useEffect(() => {
    const type = location?.state?.type
    if (typeof type !== 'undefined') {
      setActive(type)
    }
  }, [location.state])

  useEffect(() => {
    setTabs(data.map(({ tab, key }) => ({ tab: tab || key, key })))
    setContents(data.reduce((prev, { content, key }) => ({ ...prev, [key]: content }), {}))
  }, [data])

  return <Card
    className="fullTab"
    {...props}
    tabList={tabs}
    activeTabKey={active}
    onTabChange={(key) => history.replace({ state: { type: key } })}
    tabProps={{
      moreIcon: null,
    }}
  >
    {contents[active]}
  </Card>
}

import { Card } from "antd"
import { useEffect, useState } from "react"

export const CardTabs = ({ data = [], initialTab, ...props }) => {
  const [tabs, setTabs] = useState([])
  const [contents, setContents] = useState({})
  const [active, setActive] = useState(null)

  useEffect(() => (tabs.length && !active) && setActive(initialTab || tabs[0].key), [tabs])

  useEffect(() => {
    setTabs(data.map(({ tab, key }) => ({ tab: tab || key, key })))
    setContents(data.reduce((prev, { content, key }) => ({ ...prev, [key]: content }), {}))
  }, [data])

  return <Card {...props} tabList={tabs} activeTabKey={active} onTabChange={setActive}>
    {contents[active]}
  </Card>
}

import { Card, Modal } from "antd"
import { useState } from "react"
import XMLViewer from 'react-xml-viewer'

const annotationsFormat = `<annotation>
<folder>VOC_ROOT</folder>                           
<filename>aaaa.jpg</filename>  # filename(required)
<size>                         # image szie（width, height and channel count）                      
  <width>500</width>
  <height>332</height>
  <depth>3</depth>
</size>
<image_quality>1.234</image_quality>       # image quality (optional)
<segmented>1</segmented>       # for segmentation（optional）
<object>                       # object
  <name>horse</name>         # object class
  <pose>Unspecified</pose>   #  shooting angle(optional)
  <truncated>0</truncated>   # truncated
  <difficult>0</difficult>   # recognition degree, 0(easy), 1(difficult) (optional)
  <box_quality>1.234</box_quality>       # box quality 
  <bndbox>                   # bounding-box
    <xmin>100</xmin>
    <ymin>96</ymin>
    <xmax>355</xmax>
    <ymax>324</ymax>
    <rotate_angle>2.889813</rotate_angle>
  </bndbox>
</object>
<object>                       # multiple objects
  <name>person</name>
  <pose>Unspecified</pose>
  <truncated>0</truncated>
  <difficult>0</difficult>
  <box_quality>1.234</box_quality>
  <confidence>0.95</confidence>  # box confidence (for prediction, not VOC standard attribute) (optional)
  <bndbox>
    <xmin>100</xmin>
    <ymin>96</ymin>
    <xmax>355</xmax>
    <ymax>324</ymax>
    <rotate_angle>2.889813</rotate_angle>
  </bndbox>
</object>
</annotation>`

const tabs = [
  { tab: '*.xml', key: 'xml', },
  { tab: 'meta.yaml', key: 'yaml', },
]

const contents = {
  'xml': <XMLViewer xml={annotationsFormat} />,
  'yaml': <div>
    <pre><code>{
      `
eval_class_names:
      - person
      - cat
      `
    }
    </code></pre>
  </div>,
}

export const FormatDetailModal = props => {
  const [active, setActive] = useState('xml')
  return (
    <Modal
      width={'80%'}
      style={{ top: 40 }}
      {...props}
      footer={null}
    >
      <Card tabList={tabs} activeTabKey={active} onTabChange={setActive}>
        {contents[active]}
      </Card>
    </Modal>
  )
}

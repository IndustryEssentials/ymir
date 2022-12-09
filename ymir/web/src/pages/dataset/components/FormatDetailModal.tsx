import { Card, Modal, ModalProps } from 'antd'
import { FC, useState } from 'react'
import XMLViewer from 'react-xml-viewer'
import JsonViewer from 'react-json-view'
import { PROJECTTYPES } from '@/constants/project'

interface Props extends ModalProps {
  objectType: number
}

enum ObjectTypes {
  voc = 'xml',
  coco = 'json',
  yaml = 'yaml',
}

const vocXml = `<annotation>
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

const cocoJson = {}

const contents = {
  [ObjectTypes.voc]: <XMLViewer xml={vocXml} />,
  [ObjectTypes.coco]: <JsonViewer src={cocoJson} name={false} />,
  [ObjectTypes.yaml]: (
    <div>
      <pre>
        <code>
          {`eval_class_names:
      - person
      - cat
      `}
        </code>
      </pre>
    </div>
  ),
}

export const FormatDetailModal: FC<Props> = ({ objectType, ...props }) => {
  const [active, setActive] = useState<ObjectTypes>(objectType ? ObjectTypes.voc : ObjectTypes.coco)
  const vocTab = { tab: '*.xml', key: ObjectTypes.voc }
  const cocoTab = { tab: '*.json', key: ObjectTypes.coco }
const tabs = [
  objectType === PROJECTTYPES.SemanticSegmentation ? cocoTab: vocTab,
  { tab: 'meta.yaml', key: ObjectTypes.yaml },
]
  return (
    <Modal width={'80%'} style={{ top: 40 }} {...props} footer={null}>
      <Card tabList={tabs} activeTabKey={active} onTabChange={(value) => setActive(value as ObjectTypes)}>
        {contents[active]}
      </Card>
    </Modal>
  )
}

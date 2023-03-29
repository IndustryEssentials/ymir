import { Card, Modal, ModalProps } from 'antd'
import { FC, useState } from 'react'
import XMLViewer from 'react-xml-viewer'
import JsonViewer from 'react-json-view'
import { ObjectType } from '@/constants/project'

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

const cocoJson = {
  info: {
    contributor: 'LabelFree',
    date_created: '2022-12-07 07:49:11',
    description: '',
    url: '',
    version: '1.0',
    year: 2022,
  },
  licenses: [
    {
      url: 'http://creativecommons.org/licenses/by-nc-sa/2.0/',
      id: 1,
      name: 'Attribution-NonCommercial-ShareAlike License',
    },
  ],
  images: [
    {
      id: 33,
      width: 2048,
      height: 1024,
      file_name: '2baefd19-strasbourg_000000_010372_leftImg8bit.png',
    },
  ],
  annotations: [
    {
      id: 30,
      image_id: 33,
      segmentation: [
        [
          1191.0962343096237, 314.9121338912134, 1111.8326359832636, 443.44769874476987, 1096.836820083682, 531.2803347280335, 1071.129707112971,
          559.1297071129707, 1073.2719665271966, 625.5397489539749, 1079.6987447698746, 721.9414225941423, 1546.7112970711298, 751.9330543933054,
          1565.991631799163, 529.1380753138076, 1553.1380753138076, 494.8619246861925, 1585.2719665271966, 456.30125523012555, 1570.2761506276152,
          441.30543933054395, 1540.2845188284518, 434.87866108786613, 1529.5732217573222, 439.163179916318, 1491.0125523012553, 340.6192468619247,
        ],
      ],
      area: 181829.0,
      bbox: [1071.0, 314.0, 515.0, 438.0],
      iscrowd: 0,
      category_id: 1,
    },
    {
      id: 31,
      image_id: 33,
      segmentation: [
        [
          578.4100418410042, 327.765690376569, 494.8619246861925, 426.30962343096235, 507.7154811715481, 475.581589958159, 589.1213389121339, 469.1548117154812,
          672.6694560669456, 456.30125523012555, 685.5230125523012, 464.8702928870293, 709.0878661087866, 462.72803347280336, 719.7991631799163,
          449.8744769874477, 739.0794979079498, 439.163179916318, 749.7907949790795, 449.8744769874477, 786.2092050209205, 449.8744769874477, 790.4937238493724,
          439.163179916318, 826.9121338912134, 434.87866108786613, 820.4853556485356, 310.6276150627615,
        ],
      ],
      area: 41284.0,
      bbox: [494.0, 310.0, 333.0, 166.0],
      iscrowd: 0,
      category_id: 1,
    },
  ],
  categories: [{ name: 'car', supercategory: 'car', id: 1 }],
}

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

const FormatDetailModal: FC<Props> = ({ objectType, ...props }) => {
  const isDetection = objectType === ObjectType.ObjectDetection
  const [active, setActive] = useState<ObjectTypes>(isDetection ? ObjectTypes.voc : ObjectTypes.coco)
  const vocTab = { tab: '*.xml', key: ObjectTypes.voc }
  const cocoTab = { tab: '*.json', key: ObjectTypes.coco }
  const tabs = [!isDetection ? cocoTab : vocTab, { tab: 'meta.yaml', key: ObjectTypes.yaml }]
  return (
    <Modal width={'80%'} style={{ top: 40 }} {...props} footer={null}>
      <Card tabList={tabs} activeTabKey={active} onTabChange={(value) => setActive(value as ObjectTypes)}>
        {contents[active]}
      </Card>
    </Modal>
  )
}

export default FormatDetailModal

import React, { useEffect, useRef } from 'react'
import { IconProps } from './IconProps'
import styles from './style.css'
import s from '../common.less'

// icon hoc
export default function Icon(SvgContent: React.FC) {
  function generateIcon(props: IconProps) {
    const root = useRef<SVGSVGElement>(null)
    const { size = '1em', width, height, spin, rtl, color, fill, stroke, className, ...rest } = props;
    const _width = width || size;
    const _height = height || size;
    const _stroke = stroke || color;
    const _fill = fill || color;
    useEffect(() => {
      if (!_fill) {
        (root.current as SVGSVGElement)?.querySelectorAll('[data-follow-fill]').forEach(item => {
          item.setAttribute('fill', item.getAttribute('data-follow-fill') || '')
        })
      }
      if (!_stroke) {
        (root.current as SVGSVGElement)?.querySelectorAll('[data-follow-stroke]').forEach(item => {
          item.setAttribute('stroke', item.getAttribute('data-follow-stroke') || '')
        })
      }
    }, [stroke, color, fill])

    return <span className={`anticon ant-menu-item-icon ${s.cicon} ${className || ''}`}>
      <svg
        ref={root}
        width={_width}
        height={_height}
        fill='currentColor'
        xmlns="http://www.w3.org/2000/svg"
        className={`${spin ? styles.spin : ''} ${rtl ? styles.rtl : ''}`.trim()}
        {...rest}
      ><SvgContent /></svg>
    </span>
  }
  return generateIcon
}

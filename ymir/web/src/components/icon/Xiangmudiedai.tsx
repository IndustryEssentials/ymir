import React, { useEffect, useRef } from 'react';
import styles from './style.css';
interface IconProps extends React.SVGProps<SVGSVGElement> {
    size?: string | number;
    width?: string | number;
    height?: string | number;
    spin?: boolean;
    rtl?: boolean;
    color?: string;
    fill?: string;
    stroke?: string;
}

export default function Xiangmudiedai(props: IconProps) {
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
    return (
        <svg
          ref={root}
          width={_width} 
          height={_height}
          viewBox="0 0 20 20"
          preserveAspectRatio="xMidYMid meet"
          fill={_fill}
          role="presentation"
          xmlns="http://www.w3.org/2000/svg"
          className={`${className || ''} ${spin ? styles.spin : ''} ${rtl ? styles.rtl : ''}`.trim()}
          {...rest}
        >
          <g><path d="M13.596 4.5 11.97 2.873l1.06-1.06 3.359 3.359L13.03 8.53l-1.06-1.06L13.44 6H3v7H1.5V4.5h12.096ZM7.06 14l1.47-1.47-1.06-1.06-3.359 3.358 3.359 3.36 1.06-1.061L6.904 15.5H18.5V7H17v7H7.06Z" data-follow-fill="#000" fill='currentColor' /></g>
        </svg>
    )
}

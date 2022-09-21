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

export default function Shangjia(props: IconProps) {
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
          fill="none"
          role="presentation"
          xmlns="http://www.w3.org/2000/svg"
          className={`${className || ''} ${spin ? styles.spin : ''} ${rtl ? styles.rtl : ''}`.trim()}
          {...rest}
        >
          <g><path d="M1 1.25h2a.75.75 0 0 1 .724.553L6.573 12.25H17v1.5H6a.75.75 0 0 1-.724-.553L2.427 2.75H1v-1.5Zm16.04 4.5H16v-1.5h2a.75.75 0 0 1 .728.932l-1 4a.75.75 0 0 1-.64.563l-8.5 1-.176-1.49 7.986-.94.641-2.565Zm-1.842 10.903a.5.5 0 1 1-.75-.66.5.5 0 0 1 .75.66Zm1.126.99a2 2 0 1 1-3.003-2.641 2 2 0 0 1 3.003 2.641Zm-8.832-.945a.5.5 0 1 0 .66-.75.5.5 0 0 0-.66.75Zm-.99 1.127a2 2 0 1 0 2.641-3.004 2 2 0 0 0-2.641 3.004ZM8 4.332h2.167v3.5h1.666v-3.5H14L11 2 8 4.333Z" clipRule="evenodd" fillRule="evenodd" data-follow-fill="#000" fill={_fill}/></g>
        </svg>
    )
}

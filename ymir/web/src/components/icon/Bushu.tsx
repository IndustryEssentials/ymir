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

export default function Bushu(props: IconProps) {
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
          <g><path fillOpacity=".45" d="M12.5 2.5c.46 0 .833.373.833.833v3.334c0 .46-.373.833-.833.833h-1.667v1.667h3.334c.46 0 .833.373.833.833v2.5h1.667c.46 0 .833.373.833.833v3.334c0 .46-.373.833-.833.833h-5a.834.834 0 0 1-.834-.833v-3.334c0-.46.374-.833.834-.833h1.666v-1.667H6.667V12.5h1.666c.46 0 .834.373.834.833v3.334c0 .46-.374.833-.834.833h-5a.834.834 0 0 1-.833-.833v-3.334c0-.46.373-.833.833-.833H5V10c0-.46.373-.833.833-.833h3.334V7.5H7.5a.834.834 0 0 1-.833-.833V3.333c0-.46.373-.833.833-.833h5Zm-5 11.667H4.167v1.666H7.5v-1.666Zm8.333 0H12.5v1.666h3.333v-1.666Zm-4.166-10H8.333v1.666h3.334V4.167Z" data-follow-fill="#000" fill={_fill}/></g>
        </svg>
    )
}

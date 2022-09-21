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

export default function New(props: IconProps) {
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
          viewBox="0 0 48 24"
          preserveAspectRatio="xMidYMid meet"
          fill="none"
          role="presentation"
          xmlns="http://www.w3.org/2000/svg"
          className={`${className || ''} ${spin ? styles.spin : ''} ${rtl ? styles.rtl : ''}`.trim()}
          {...rest}
        >
          <g><path fill="#2CBDE9" d="M0 0h48v16a8 8 0 0 1-8 8H8a8 8 0 0 1-8-8V0Z"/><path fill="#fff" d="M9.008 7.004V17h1.148V8.782h.042L15.882 17h1.176V7.004H15.91v8.134h-.042l-5.656-8.134H9.008Zm10.062 0V17h7.322v-.994h-6.174v-3.668h5.6v-.994h-5.6V7.998h5.936v-.994H19.07Zm7.977 0L29.917 17h1.274l2.282-8.33h.042L35.783 17h1.274l2.87-9.996h-1.288L36.44 15.39h-.056l-2.268-8.386H32.87l-2.282 8.386h-.056l-2.198-8.386h-1.288Z"/></g>
        </svg>
    )
}

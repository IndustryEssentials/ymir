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

export default function Redu(props: IconProps) {
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
          <g><path d="M6.92 18c-1.059-2.23-.501-3.512.335-4.683.892-1.338 1.115-2.62 1.115-2.62s.725.892.446 2.341c1.226-1.393 1.45-3.623 1.282-4.46 2.788 1.952 4.014 6.244 2.397 9.366 8.586-4.906 2.119-12.209 1.004-12.99.39.837.446 2.23-.335 2.9C11.882 2.948 8.704 2 8.704 2c.39 2.509-1.337 5.24-3.01 7.303-.056-1.003-.111-1.672-.669-2.676-.111 1.84-1.505 3.29-1.895 5.13-.502 2.508.39 4.292 3.79 6.243Z" data-follow-fill="#F2637B" fill={_fill}/></g>
        </svg>
    )
}

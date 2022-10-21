import { useEffect, useState } from "react"

const useWindowResize = () => {
    const [width, setWidth] = useState(window.innerWidth)
    const resizeHandle = () => setWidth(window.innerWidth)
    useEffect(() => {
        window.addEventListener('resize', resizeHandle)
        return () => {
            window.removeEventListener('resize', resizeHandle)
        }
    }, [])

    return width
}

export default useWindowResize

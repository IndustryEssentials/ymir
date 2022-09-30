export function encode(obj: { [name: string]: string | number }) {
    return Object.keys(obj).map(key => encodeURIComponent(key) + '=' + encodeURIComponent(obj[key]))
}

export function decode(paramsString: string) {
    const params = new URLSearchParams(paramsString)
    return [...params].reduce((prev, [key, value]) => ({ ...prev, [key]: value }), {})
}
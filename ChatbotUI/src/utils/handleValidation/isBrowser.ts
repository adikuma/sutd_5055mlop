const isBrowser = (): boolean => {
  return typeof window !== 'undefined'
}

export default isBrowser

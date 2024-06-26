enum Keys {
  token = "TOKEN",
  username = "USERNAME"
}

export default new Proxy({} as {
  -readonly [P in keyof typeof Keys]?: string
}, {
  get(_, key: keyof typeof Keys) {
    return localStorage[Keys[key]]
  },
  set(_, key: keyof typeof Keys, value: string | undefined) {
    if (typeof value == "undefined") {
      localStorage.removeItem(Keys[key])
    } else {
      localStorage.setItem(Keys[key], value)
    }
    return true
  },
  deleteProperty(_, key: keyof typeof Keys) {
    localStorage.removeItem(Keys[key])
    return true
  },
})

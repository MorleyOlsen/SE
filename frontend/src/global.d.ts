interface ObjectConstructor {
  keys<T>(o: T): (keyof T)[]
  values<T>(o: T): T[keyof T][]
  entries<T>(o: T): [keyof T, T[keyof T]][]
  fromEntries<K extends PropertyKey, V>(entries: Iterable<readonly [K, V]>): { [Key in K]: V }
}

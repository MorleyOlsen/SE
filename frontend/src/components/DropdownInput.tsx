import { For, Suspense, createResource, createSignal, type JSX } from "solid-js"
import { type MaybePromise } from "~/utils"
import styles from "./DropdownInput.module.css"

export function DropdownInput(props: {
  name?: string,
  id?: string,
  value?: string,
  displayValue?: string,
  required?: boolean,
  options(search: string): MaybePromise<{ value: string, displayValue: string }[]>,
  class?: string,
}): JSX.Element {
  const [selection, setSelection] = createSignal({
    value: props.value ?? "",
    displayValue: props.displayValue ?? ""
  }, { equals: false })
  const [search, setSearch] = createSignal<string>()
  const [options] = createResource(search, s => {
    if (typeof s == "string") {
      return props.options(s)
    } else {
      return []
    }
  }, { initialValue: [] })
  return <span class={styles.dropdownInput + " " + (props.class ?? "")}>
    <input type="hidden" name={props.name} value={selection().value} />
    <input type="text" id={props.id} value={selection().displayValue} required={props.required}
      onfocus={e => setSearch(e.currentTarget.value)}
      oninput={e => setSearch(e.currentTarget.value)}
      onblur={e => {
        const selected = options().find(option => option.displayValue == e.currentTarget.value)
        if (typeof selected != "undefined") {
          setSelection(selected)
        } else {
          setSelection(selection())
        }
      }}
    />
    <div>
      <Suspense fallback={<div>加载中……</div>}>
        <For each={options()}>{option =>
          <div class={styles.option}
            tabindex="0"
            onclick={e => {
              setSelection(option)
              e.currentTarget.blur()
            }}
            onkeypress={e => {
              if (e.key == "Enter") {
                setSelection(option)
                e.currentTarget.blur()
              }
            }}
          >{option.displayValue}</div>
        }</For>
      </Suspense>
    </div>
  </span>
}

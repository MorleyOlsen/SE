import { createContext, createUniqueId, useContext, type Component, type JSX } from "solid-js"

import styles from "./SegmentedButton.module.css"

const SegmentedButtonCtx = createContext<{
  name: string,
  type: "radio" | "checkbox",
  required?: boolean
}>()

export const SegmentedButton: Component<{
  name: string,
  type: "radio" | "checkbox",
  required?: boolean,
  id?: string,
  class?: string,
  children: JSX.Element
}> = props => {
  return <SegmentedButtonCtx.Provider value={props}>
    <fieldset id={props.id}
      class={styles.segmentedBtn + " " + (props.class ?? "")}
    >
      {props.children}
    </fieldset>
  </SegmentedButtonCtx.Provider>
}

export const SegmentedButtonSegment: Component<{
  value: string | number,
  checked?: boolean,
  disabled?: boolean,
  class?: string,
  children: JSX.Element
}> = props => {
  const ctx = useContext(SegmentedButtonCtx)!
  const id = createUniqueId()
  return <>
    <input id={id}
      type={ctx.type}
      name={ctx.name}
      required={ctx.required}
      value={props.value}
      checked={props.checked}
      disabled={props.disabled}
    />
    <label for={id} class={props.class}>{props.children}</label>
  </>
}

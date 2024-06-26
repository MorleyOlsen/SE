import { For, Show, Suspense, createSignal, createUniqueId, type JSX } from "solid-js"
import styles from "./DataTable.module.css"

export function DataTable<T, Key extends keyof T>(props: {
  data: T[],
  head: {
    [K in Key]: JSX.Element
  },
  cell: {
    [K in Key]: (value: T[K], row: T) => JSX.Element
  },
  edit?: {
    [K in Key]?: (id: string, value: T[K]) => JSX.Element
  },
  save?(input: { [K in Key]: string }, row?: T): Promise<void> | void,
  remove?(row: T): Promise<void> | void,
  default?: { [K in Key]: T[K] },
  class?: string
}): JSX.Element {
  const hasControls = Boolean(props.save || props.remove)
  const [showEditor, setShowEditor] = createSignal(false)
  return <table class={styles.dataTable + " " + (props.class ?? "")}>
    <thead>
      <tr>
        <For each={Object.values(props.head)}>{head =>
          <th>{head}</th>
        }</For>
        <Show when={hasControls}>
          <th>操作</th>
        </Show>
      </tr>
    </thead>
    <tbody>
      <Suspense fallback={<tr>
        <td colspan={Object.keys(props.head).length + Number(hasControls)}>
          加载中……
        </td>
      </tr>}>
        <For each={props.data}>{row =>
          <DataTableRow row={row}
            head={props.head}
            cell={props.cell}
            edit={props.edit}
            save={props.save ? (input, row) => props.save!(input, row) : undefined}
            remove={props.remove}
          />
        }</For>
      </Suspense>
      <Show when={props.save}>{save =>
        <Show when={props.default}>{def =>
          <tr>
            <td class={showEditor() ? styles.editor : ""}
              colspan={Object.keys(props.head).length + Number(hasControls)}
            >
              <Show when={showEditor()}
                children={<DataTableEditor value={def()}
                  head={props.head}
                  edit={props.edit}
                  save={async input => {
                    await save()(input)
                    setShowEditor(false)
                  }}
                  cancel={() => setShowEditor(false)}
                />}
                fallback={<a onclick={() => setShowEditor(true)}>添加……</a>}
              />
            </td>
          </tr>
        }</Show>
      }</Show>
    </tbody>
  </table>
}

function DataTableRow<T, Key extends keyof T>(props: {
  row: T,
  head: {
    [K in Key]: JSX.Element
  },
  cell: {
    [K in Key]: (value: T[K], row: T) => JSX.Element
  },
  edit?: {
    [K in Key]?: (id: string, value: T[K]) => JSX.Element
  },
  save?(input: { [K in Key]: string }, row: T): Promise<void> | void,
  remove?(row: T): Promise<void> | void
}): JSX.Element {
  const hasControls = Boolean(props.save || props.remove)
  const [showEditor, setShowEditor] = createSignal(false)
  return <>
    <tr>
      <For each={Object.keys(props.head)}>{key =>
        <td>{props.cell[key](props.row[key], props.row)}</td>
      }</For>
      <Show when={hasControls}>
        <td class={styles.controls}>
          <Show when={props.save}>
            <a onclick={() => setShowEditor(true)}>编辑</a>
          </Show>
          <Show when={props.remove}>{remove =>
            <a onclick={() => remove()(props.row)}>删除</a>
          }</Show>
        </td>
      </Show>
    </tr>
    <Show when={showEditor() && props.save}>{save =>
      <tr>
        <td class={styles.editor}
          colspan={Object.keys(props.head).length + Number(hasControls)}
        >
          <DataTableEditor value={props.row}
            head={props.head}
            edit={props.edit}
            save={async input => {
              await save()(input, props.row)
              setShowEditor(false)
            }}
            cancel={() => setShowEditor(false)}
          />
        </td>
      </tr>
    }</Show>
  </>
}

function DataTableEditor<T, Key extends keyof T>(props: {
  value: { [K in Key]: T[K] },
  head: {
    [K in Key]: JSX.Element
  },
  edit?: {
    [K in Key]?: (id: string, value: T[K]) => JSX.Element
  },
  save(input: { [K in Key]: string }): Promise<void> | void,
  cancel: () => void,
}): JSX.Element {
  const ids = Object.fromEntries(
    Object.keys(props.head).map(key => [key, createUniqueId()])
  )
  return <form onsubmit={event => {
    event.preventDefault()
    const data = new FormData(event.currentTarget)
    props.save(Object.fromEntries(
      Object.entries(ids).map(([key, id]) => [key, data.get(id)!.toString()])
    ))
  }}>
    <For each={Object.entries(props.head)}>{([key, name]) => <>
      <label for={ids[key]}>{name}</label>
      <Show when={props.edit?.[key]}
        children={edit => edit()(ids[key], props.value[key])}
        fallback={
          <input type="text" name={ids[key]} id={ids[key]}
            value={String(props.value[key])} required
          />
        }
      />
    </>}</For>
    <div>
      <button onclick={props.cancel}>取消</button>
      <button type="submit">保存</button>
    </div>
  </form>
}

import { createResource, useContext, type Component } from "solid-js"
import { DataTable } from "~/components/DataTable"
import { handleError, request } from "~/utils"
import { ProfileCtx } from "./profile"

interface Warehouse {
  id: number
  name: string
  env: string
  size: number
}

export async function getWarehouses(token: string) {
  const resp = await request("/query_all_repo", {
    body: JSON.stringify({
      "log_token": token
    })
  })
  await handleError(resp)
  const data = await resp.json()
  return (data["repos"] as any[]).map(warehouse => ({
    id: warehouse["repo_id"],
    name: warehouse["repo_name"],
    env: warehouse["repo_info"],
    size: warehouse["repo_maxsize"],
  } as Warehouse))
}

async function updateWarehouse(token: string, warehouse: Omit<Warehouse, "id">, id?: number) {
  const resp = await request(
    typeof id == "number" ? "/update_repo" : "/add_repo",
    {
      body: JSON.stringify({
        "log_token": token,
        "repo_id": id ?? null,
        "repo_name": warehouse.name,
        "repo_info": warehouse.env,
        "repo_maxsize": warehouse.size
      })
    }
  )
  await handleError(resp)
}

async function deleteWarehouse(token: string, id: number) {
  const resp = await request("/delete_repo", {
    body: JSON.stringify({
      "log_token": token,
      "repo_id": id,
    })
  })
  await handleError(resp)
}

const Warehouse: Component = () => {
  const [profile] = useContext(ProfileCtx)
  const [warehouses, { refetch }] = createResource(
    profile,
    profile => getWarehouses(profile.token),
    { initialValue: [] }
  )
  return <div>
    <h1 style={{ "margin-bottom": "1rem" }}>仓库管理</h1>
    <DataTable data={warehouses()}
      head={{
        name: "名称",
        env: "环境",
        size: "容量"
      }}
      cell={{
        name: x => x,
        env: x => x,
        size: x => `${x} m³`
      }}
      edit={{
        size: (id, value) => <span attr:with-unit="true">
          <input type="number" name={id} id={id} value={value} min={0} step={1} required />
           m³
        </span>,
      }}
      save={async (input, row) => {
        await updateWarehouse(profile().token, {
          name: input.name,
          env: input.env,
          size: Number(input.size)
        }, row?.id)
        refetch()
      }}
      remove={async row => {
        await deleteWarehouse(profile().token, row.id)
        refetch()
      }}
      default={{
        name: "",
        env: "",
        size: 0
      }} />
  </div>
}

export default Warehouse

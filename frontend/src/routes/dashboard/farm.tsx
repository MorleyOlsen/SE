import { createResource, useContext, type Component } from "solid-js"
import { DataTable } from "~/components/DataTable"
import { handleError, request } from "~/utils"
import { ProfileCtx } from "./profile"

export interface Farm {
  id: number
  name: string
  type: string
  size: number
}

export async function getFarms(token: string) {
  const resp = await request("/query_all_farms", {
    body: JSON.stringify({
      "log_token": token
    })
  })
  await handleError(resp)
  const data = await resp.json()
  return (data["farms"] as any[]).map(farm => ({
    id: farm["farm_id"],
    name: farm["farm_name"],
    type: farm["farm_type"],
    size: farm["farm_size"],
  } as Farm))
}

async function updateFarm(token: string, farm: Omit<Farm, "id">, id?: number) {
  const resp = await request(
    typeof id == "number" ? "/update_farm" : "/add_farm",
    {
      body: JSON.stringify({
        "log_token": token,
        "farm_id": id ?? null,
        "farm_name": farm.name,
        "farm_type": farm.type,
        "farm_size": farm.size
      })
    }
  )
  await handleError(resp)
}

async function deleteFarm(token: string, id: number) {
  const resp = await request("/delete_farm", {
    body: JSON.stringify({
      "log_token": token,
      "farm_id": id,
    })
  })
  await handleError(resp)
}

const Farm: Component = () => {
  const [profile] = useContext(ProfileCtx)
  const [farms, { refetch }] = createResource(
    profile,
    profile => getFarms(profile.token),
    { initialValue: [] }
  )
  return <div>
    <h1 style={{ "margin-bottom": "1rem" }}>农场管理</h1>
    <DataTable data={farms()}
      head={{
        name: "名称",
        type: "类型",
        size: "面积"
      }}
      cell={{
        name: x => x,
        type: x => x,
        size: x => `${x} 公顷`
      }}
      edit={{
        size: (id, value) => <span attr:with-unit="true">
          <input type="number" name={id} id={id} value={value} min={0} required />
          公顷
        </span>
      }}
      save={async (input, row) => {
        await updateFarm(profile().token, {
          name: input.name,
          type: input.type,
          size: Number(input.size)
        }, row?.id)
        refetch()
      }}
      remove={async row => {
        await deleteFarm(profile().token, row.id)
        refetch()
      }}
      default={{
        name: "",
        type: "",
        size: 0
      }}
    />
  </div>
}

export default Farm

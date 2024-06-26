import { createResource, useContext, type Component } from "solid-js"
import { DataTable } from "~/components/DataTable"
import { SegmentedButton, SegmentedButtonSegment } from "~/components/SegmentedButton"
import { handleError, request } from "~/utils"
import { ProfileCtx } from "./profile"

export enum Kind {
  ANIMAL, PLANT
}

export interface Breed {
  id: number
  name: string
  period: number
  info: string
  kind: Kind
}

export async function getBreeds(token: string) {
  const resp = await request("/query_all_type", {
    body: JSON.stringify({
      "log_token": token
    })
  })
  await handleError(resp)
  const data = await resp.json()
  return (data["all_types"] as any[]).map(breed => ({
    id: breed["type_id"],
    name: breed["type_name"],
    period: breed["type_period"],
    info: breed["type_info"],
    kind: breed["type_judge"],
  } as Breed))
}

async function updateBreed(token: string, breed: Omit<Breed, "id">, id?: number) {
  const resp = await request(
    typeof id == "number" ? "/update_type" : "/add_type",
    {
      body: JSON.stringify({
        "log_token": token,
        "type_id": id ?? null,
        "type_name": breed.name,
        "type_period": breed.period,
        "type_info": breed.info,
        "type_judge": breed.kind
      })
    }
  )
  await handleError(resp)
}

const Breed: Component = () => {
  const [profile] = useContext(ProfileCtx)
  const [breeds, { refetch }] = createResource(
    profile,
    profile => getBreeds(profile.token),
    { initialValue: [] }
  )
  return <div>
    <h1 style={{ "margin-bottom": "1rem" }}>品种管理</h1>
    <DataTable data={breeds()}
      head={{
        name: "名称",
        period: "生长周期",
        info: "备注",
        kind: "类别"
      }}
      cell={{
        name: x => x,
        period: x => `${x} 天`,
        info: x => x,
        kind: x => ["动物", "植物"][x]
      }}
      edit={{
        period: (id, value) => <span attr:with-unit="true">
          <input type="number" name={id} id={id} value={value} min={1} step={1} required />
          天
        </span>,
        kind: (id, value) => <SegmentedButton type="radio" id={id} name={id} required>
          <SegmentedButtonSegment value={Kind.ANIMAL} checked={value == Kind.ANIMAL}>动物</SegmentedButtonSegment>
          <SegmentedButtonSegment value={Kind.PLANT} checked={value == Kind.PLANT}>植物</SegmentedButtonSegment>
        </SegmentedButton>
      }}
      save={async (input, row) => {
        await updateBreed(profile().token, {
          name: input.name,
          period: Number(input.period),
          info: input.info,
          kind: Number(input.kind)
        }, row?.id)
        refetch()
      }}
      default={{
        name: "",
        period: 1,
        info: "",
        kind: 0
      }}
    />
  </div>
}

export default Breed

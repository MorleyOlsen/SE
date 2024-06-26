import { createResource, useContext, type Component } from "solid-js"
import { DataTable } from "~/components/DataTable"
import { DropdownInput } from "~/components/DropdownInput"
import { SegmentedButton, SegmentedButtonSegment } from "~/components/SegmentedButton"
import { handleError, request } from "~/utils"
import { getBreeds } from "./breed"
import { getFarms } from "./farm"
import { ProfileCtx } from "./profile"

enum State {
  GROWING, RIPE, HARVESTED
}

interface Production {
  id: number
  farm: number
  breed: number
  amount: number
  begin: Date
  state: State
}

export async function getProductions(token: string) {
  const resp = await request("/query_all_produce_batch", {
    body: JSON.stringify({
      "log_token": token
    })
  })
  await handleError(resp)
  const data = await resp.json()
  return (data["produce_batches"] as any[]).map(production => ({
    id: production["batch_id"],
    farm: production["farm_id"],
    breed: production["type_id"],
    amount: production["batch_num"],
    begin: new Date(production["batch_start"]),
    state: production["batch_judge"]
  } as Production))
}

async function updateProduction(token: string, production: Omit<Production, "id">, id?: number) {
  const resp = await request(
    typeof id == "number" ? "/update_produce_batch" : "/add_produce_batch",
    {
      body: JSON.stringify({
        "log_token": token,
        "batch_id": id ?? null,
        "farm_id": production.farm,
        "type_id": production.breed,
        "batch_num": production.amount,
        "batch_start": production.begin.toISOString(),
        "batch_judge": production.state
      })
    }
  )
  await handleError(resp)
}

async function deleteProduction(token: string, id: number) {
  const resp = await request("/delete_produce_batch", {
    body: JSON.stringify({
      "log_token": token,
      "batch_id": id,
    })
  })
  await handleError(resp)
}

const Production: Component = () => {
  const [profile] = useContext(ProfileCtx)
  const [productions, { refetch }] = createResource(
    profile,
    profile => getProductions(profile.token),
    { initialValue: [] }
  )
  const [farms] = createResource(
    profile,
    async profile => (await getFarms(profile.token)).map(farm => ({
      value: farm.id.toString(),
      displayValue: farm.name
    })),
    { initialValue: [] }
  )
  const [breeds] = createResource(
    profile,
    async profile => (await getBreeds(profile.token)).map(breed => ({
      value: breed.id.toString(),
      displayValue: breed.name
    })),
    { initialValue: [] }
  )
  return <div>
    <h1 style={{ "margin-bottom": "1rem" }}>生产管理</h1>
    <DataTable data={productions()}
      head={{
        farm: "农场",
        breed: "品种",
        amount: "数量",
        begin: "开始时间",
        state: "状态"
      }}
      cell={{
        farm: x => farms().find(farm => farm.value == x.toString())?.displayValue,
        breed: x => breeds().find(breed => breed.value == x.toString())?.displayValue,
        amount: x => x,
        begin: x => x.toLocaleString("zh-CN", {
          "dateStyle": "short",
          "timeStyle": "short"
        }),
        state: x => ["未成熟", "待收获", "已收获"][x]
      }}
      edit={{
        farm: (id, value) =>
          <DropdownInput name={id} id={id} required
            value={value < 0 ? undefined : value.toString()}
            displayValue={value < 0 ? undefined :
              farms().find(farm => farm.value == value.toString())?.displayValue
            }
            options={search => farms().filter(farm => farm.displayValue.includes(search))}
          />,
        breed: (id, value) =>
          <DropdownInput name={id} id={id} required
            value={value < 0 ? undefined : value.toString()}
            displayValue={value < 0 ? undefined :
              breeds().find(breed => breed.value == value.toString())?.displayValue
            }
            options={search => breeds().filter(breed => breed.displayValue.includes(search))}
          />,
        amount: (id, value) =>
          <input type="number" name={id} id={id} value={value} min={0} step={1} required />,
        begin: (id, value) =>
          <input type="datetime-local" name={id} id={id} step="any" required
            value={new Date(
              value.getTime() - value.getTimezoneOffset() * 60000
            ).toISOString().slice(0, -5)}
          />,
        state: (id, value) => <SegmentedButton type="radio" id={id} name={id} required>
          <SegmentedButtonSegment value={State.GROWING} checked={value == State.GROWING}>生长中</SegmentedButtonSegment>
          <SegmentedButtonSegment value={State.RIPE} checked={value == State.RIPE}>待收获</SegmentedButtonSegment>
          <SegmentedButtonSegment value={State.HARVESTED} checked={value == State.HARVESTED}>已收获</SegmentedButtonSegment>
        </SegmentedButton>
      }}
      save={async (input, row) => {
        await updateProduction(profile().token, {
          farm: Number(input.farm),
          breed: Number(input.breed),
          amount: Number(input.amount),
          begin: new Date(input.begin),
          state: Number(input.state)
        }, row?.id)
        refetch()
      }}
      remove={async row => {
        await deleteProduction(profile().token, row.id)
        refetch()
      }}
      default={{
        farm: -1,
        breed: -1,
        amount: 0,
        begin: new Date(),
        state: 0
      }} />
  </div>
}

export default Production

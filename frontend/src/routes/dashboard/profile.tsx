import { createContext, createUniqueId, useContext, type Component } from "solid-js"
import { SegmentedButton, SegmentedButtonSegment } from "~/components/SegmentedButton"
import { handleError, request } from "~/utils"
import styles from "./profile.module.css"

export enum Role {
  FARMER,
  CUSTOMER
}

export interface Profile {
  username: string
  token: string
  role: Role
  name: string | null
  gender: string | null
  age: number | null
  phone: string | null
  address: string | null
}

export const defaultProfile: Profile = {
  username: "",
  token: "",
  role: 0,
  name: null,
  gender: null,
  age: null,
  phone: null,
  address: null
}

export const ProfileCtx = createContext<[() => Profile, () => void]>(
  [() => defaultProfile, () => {}]
)

export async function getProfile(username: string, token: string) {
  const resp = await request("/user_info", {
    body: JSON.stringify({
      "log_token": token
    })
  })
  await handleError(resp)
  const { role_id: role, ...profile } = await resp.json()
  const prefix = role == Role.FARMER ? "seller" : "buyer"
  const details = profile[prefix]
  return {
    username: username,
    token: token,
    role: role,
    name: details[prefix + "_name"],
    gender: details[prefix + "_sex"],
    age: details[prefix + "_age"],
    phone: details[prefix + "_phone"],
    address: details[prefix + "_address"]
  } as Profile
}

async function updateProfile(token: string, profile: Omit<Profile, "username" | "token" | "role">) {
  const resp = await request("/update_user_info", {
    body: JSON.stringify({
      "log_token": token,
      ...profile,
      "sex": profile.gender
    })
  })
  await handleError(resp)
}

const Profile: Component = () => {
  const [profile, refetch] = useContext(ProfileCtx)
  const ids = Array.from({ length: 5 }, () => createUniqueId())
  return <div class={styles.root}>
    <h1>个人资料</h1>
    <form onsubmit={async event => {
      event.preventDefault()
      const data = new FormData(event.currentTarget)
      await updateProfile(profile().token, {
        name: data.get(ids[0]) as string | null,
        gender: data.get(ids[1]) as string | null,
        age: data.get(ids[2]) as number | null,
        phone: data.get(ids[3]) as string | null,
        address: data.get(ids[4]) as string | null,
      })
      refetch()
    }}>
      <label for={ids[0]}>姓名</label>
      <input type="text" id={ids[0]} name={ids[0]} value={profile().name ?? ""} />
      <label for={ids[1]}>性别</label>
      <SegmentedButton type="radio" name={ids[1]} id={ids[1]}>
        <SegmentedButtonSegment value="男" checked={profile().gender == "男"}>男</SegmentedButtonSegment>
        <SegmentedButtonSegment value="女" checked={profile().gender == "女"}>女</SegmentedButtonSegment>
      </SegmentedButton>
      <label for={ids[2]}>年龄</label>
      <input type="number" id={ids[2]} name={ids[2]} min="0" step="0" value={profile().age ?? ""} />
      <label for={ids[3]}>电话</label>
      <input type="text" id={ids[3]} name={ids[3]} value={profile().phone ?? ""} />
      <label for={ids[4]}>地址</label>
      <input type="text" id={ids[4]} name={ids[4]} value={profile().address ?? ""} />
      <button type="submit">保存</button>
    </form>
  </div>
}

export default Profile

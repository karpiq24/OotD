// Links between NPC folders and the faction/location pages of the same name (OotD:
// 02-People/NPCs/Kult Węża/ <-> 02-People/Factions/Kult Węża.md, NPCs/Mytros/ <-> 03-Locations/.../Mytros).
// A page whose name differs from its NPC folder sets `people: <folder name>`.
// The folder names come from site.json.
import path from "path"
import { alsoIn, folderName, pageTitle } from "./data"
import { QuartzPluginData } from "../../plugins/vfile"
import { byTitle, Listing } from "./listing"
import { layout, t } from "../../util/site"

export const PEOPLE_ROOT = layout.people_dir + "/"
export const NPC_ROOT = PEOPLE_ROOT + layout.npcs_subdir + "/"
const FACTIONS_ROOT = PEOPLE_ROOT + layout.factions_subdir + "/"
const BRIDGED = [FACTIONS_ROOT, layout.locations_dir + "/"]

// The NPC folder name a faction/location page or folder pairs with.
export function peopleKey(file: QuartzPluginData): string | undefined {
  const explicit = file.frontmatter?.people
  if (typeof explicit === "string" && explicit.trim()) return explicit.trim()
  if (!file.relativePath) return undefined
  const base = path.posix.basename(file.relativePath, ".md")
  return base === "index" ? folderName(file) : base
}

function isIndex(file: QuartzPluginData): boolean {
  return path.posix.basename(file.relativePath ?? "") === "index.md"
}

// The index.md of the NPC folder called `name`, at any depth under NPCs/.
export function npcFolder(l: Listing, name: string): QuartzPluginData | undefined {
  return l.allFiles.find(
    (f) => f.relativePath?.startsWith(NPC_ROOT) && isIndex(f) && folderName(f) === name,
  )
}

// Everyone in that NPC folder (and its subfolders), then those who list it in `also_in`.
export function membersOf(
  l: Listing,
  name: string,
): { members: QuartzPluginData[]; guests: QuartzPluginData[] } {
  const folder = npcFolder(l, name)
  const dir = folder ? path.posix.dirname(folder.relativePath!) + "/" : undefined
  const sort = (a: QuartzPluginData, b: QuartzPluginData) => byTitle(l)(pageTitle(a), pageTitle(b))
  const members = dir
    ? l.allFiles.filter((f) => f.relativePath?.startsWith(dir) && !isIndex(f)).sort(sort)
    : []
  const guests = l.allFiles
    .filter(
      (f) =>
        f.relativePath?.startsWith(PEOPLE_ROOT) && !members.includes(f) && alsoIn(f).includes(name),
    )
    .sort(sort)
  return { members, guests }
}

// Faction and location pages paired with the NPC folder `name`.
export function pagesAbout(l: Listing, name: string): QuartzPluginData[] {
  return l.allFiles.filter(
    (f) =>
      BRIDGED.some((p) => f.relativePath?.startsWith(p)) &&
      peopleKey(f) === name &&
      !hasOwnPage(l.allFiles, f),
  )
}

// a folder (…/Mytros/index.md) holding a page of its own name (…/Mytros/Mytros.md) defers to it
export function hasOwnPage(allFiles: QuartzPluginData[], file: QuartzPluginData): boolean {
  if (!isIndex(file)) return false
  const dir = path.posix.dirname(file.relativePath!)
  return allFiles.some((f) => f.relativePath === `${dir}/${folderName(file)}.md`)
}

export function isBridged(file: QuartzPluginData): boolean {
  return BRIDGED.some((p) => file.relativePath?.startsWith(p))
}

export function bridgeKind(file: QuartzPluginData): string {
  return file.relativePath?.startsWith(FACTIONS_ROOT) ? t("kind_faction") : t("kind_place")
}

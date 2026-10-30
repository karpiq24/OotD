import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import style from "./styles/ootd.scss"
// @ts-ignore
import script from "./scripts/ootdFilter.inline"
import { alsoIn, folderName, groupOf, pageTitle, stringList } from "./ootd/data"
import { byTitle, FilterBox, Listing, PageCard } from "./ootd/listing"
import { QuartzPluginData } from "../plugins/vfile"
import { FullSlug } from "../util/path"

// A page with `catalog: true` lists every person under 02-People in one grid. Folders act
// as filter chips instead of places: a card matches its home folder and its `also_in`
// folders, and each chip group (the NPC folders' `group:`) filters the whole group.
const ROOT = "02-People/"
const TOP_GROUP = "Bohaterowie i frakcje"

const PeopleCatalog: QuartzComponent = ({ fileData, allFiles, ctx, cfg }: QuartzComponentProps) => {
  if (fileData.frontmatter?.catalog !== true) return null
  const l: Listing = { slug: fileData.slug as FullSlug, ctx, locale: cfg.locale, allFiles }
  const sort = byTitle(l)

  const isIndex = (f: QuartzPluginData) => f.relativePath?.endsWith("/index.md")
  const inPeople = (f: QuartzPluginData) => f.relativePath?.startsWith(ROOT)
  const folders = new Map(
    allFiles
      .filter((f) => inPeople(f) && isIndex(f) && f.relativePath !== ROOT + "index.md")
      .map((f) => [folderName(f)!, f]),
  )
  const label = (name: string) => {
    const index = folders.get(name)
    return index ? pageTitle(index) : name
  }
  const groupFor = (name: string) =>
    groupOf(folders.get(name)) ??
    (folders.get(name)?.relativePath?.split("/").length === 3 ? TOP_GROUP : undefined)

  const people = allFiles
    .filter((f) => inPeople(f) && !isIndex(f) && f.frontmatter?.catalog !== true)
    .sort((a, b) => sort(pageTitle(a), pageTitle(b)))

  // every folder on the way down (Tytani for Dzieci Tytanów) plus `also_in`
  const foldersOf = (f: QuartzPluginData) =>
    f
      .relativePath!.split("/")
      .slice(1, -1)
      .filter((d) => d !== "NPCs")
  const tagsOf = (f: QuartzPluginData) => {
    const names = [...foldersOf(f), ...alsoIn(f)]
    const groups = names.map(groupFor).filter((g): g is string => !!g)
    return [...names, ...groups.map((g) => `grupa:${g}`)]
  }

  // chips: every folder someone is tagged with, under its group, groups in NPC order
  const used = new Set(people.flatMap((f) => [...foldersOf(f), ...alsoIn(f)]))
  const npcOrder = stringList(folders.get("NPCs")?.frontmatter?.groups)
  const chipGroups = new Map<string, string[]>()
  for (const name of [...used].filter((n) => folders.has(n) && n !== "NPCs")) {
    const group = groupFor(name) ?? "Pozostałe"
    chipGroups.set(group, [...(chipGroups.get(group) ?? []), name])
  }
  const groupOrder = [TOP_GROUP, ...npcOrder]
  const orderedGroups = [...chipGroups.keys()].sort((a, b) => {
    const ia = groupOrder.indexOf(a)
    const ib = groupOrder.indexOf(b)
    return (ia < 0 ? 999 : ia) - (ib < 0 ? 999 : ib)
  })

  return (
    <div class="ootd-catalog" data-ootd-filter>
      <FilterBox total={people.length} label="Szukaj: imię, przydomek, opis…" />
      <div class="ootd-facets">
        {orderedGroups.map((group) => (
          <div class="ootd-facet-group">
            <button type="button" class="ootd-chip ootd-chip-group" data-tag={`grupa:${group}`}>
              {group}
            </button>
            {chipGroups
              .get(group)!
              .sort((a, b) => sort(label(a), label(b)))
              .map((name) => (
                <button type="button" class="ootd-chip" data-tag={name}>
                  {label(name)}
                </button>
              ))}
          </div>
        ))}
      </div>
      <div class="ootd-grid ootd-grid-pages">
        {people.map((page) => (
          <PageCard l={l} page={page} kicker={label(folderName(page)!)} tags={tagsOf(page)} />
        ))}
      </div>
    </div>
  )
}

PeopleCatalog.css = style
PeopleCatalog.afterDOMLoaded = script

export default (() => PeopleCatalog) satisfies QuartzComponentConstructor

import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import style from "./styles/theme.scss"
// @ts-ignore
import script from "./scripts/cardFilter.inline"
import { alsoIn, folderName, groupOf, pageTitle, stringList } from "./rpg/data"
import { byTitle, FilterBox, Listing, PageCard } from "./rpg/listing"
import { QuartzPluginData } from "../plugins/vfile"
import { FullSlug } from "../util/path"
import { layout, t } from "../util/site"

// A page with `catalog: true` lists every person under the people folder in one grid. Folders
// act as filter chips instead of places: a card matches its home folder and its `also_in`
// folders, and each chip group (the NPC folders' `group:`) filters the whole group.
const ROOT = layout.people_dir + "/"
const NPCS = layout.npcs_subdir
// a folder directly under the people folder (the party, the factions) is in the top group
const TOP_DEPTH = ROOT.split("/").length + 1
const TOP_GROUP = t("catalog_top_group")
const GROUP_TAG = t("group_tag_prefix")

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
    (folders.get(name)?.relativePath?.split("/").length === TOP_DEPTH ? TOP_GROUP : undefined)

  const people = allFiles
    .filter((f) => inPeople(f) && !isIndex(f) && f.frontmatter?.catalog !== true)
    .sort((a, b) => sort(pageTitle(a), pageTitle(b)))

  // every folder on the way down (Tytani for Dzieci Tytanów) plus `also_in`
  const foldersOf = (f: QuartzPluginData) =>
    f
      .relativePath!.split("/")
      .slice(TOP_DEPTH - 2, -1)
      .filter((d) => d !== NPCS)
  const tagsOf = (f: QuartzPluginData) => {
    const names = [...foldersOf(f), ...alsoIn(f)]
    const groups = names.map(groupFor).filter((g): g is string => !!g)
    return [...names, ...groups.map((g) => GROUP_TAG + g)]
  }

  // chips: every folder someone is tagged with, under its group, groups in NPC order
  const used = new Set(people.flatMap((f) => [...foldersOf(f), ...alsoIn(f)]))
  const npcOrder = stringList(folders.get(NPCS)?.frontmatter?.groups)
  const chipGroups = new Map<string, string[]>()
  for (const name of [...used].filter((n) => folders.has(n) && n !== NPCS)) {
    const group = groupFor(name) ?? t("other_group")
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
      <FilterBox total={people.length} label={t("search_people")} />
      <div class="ootd-facets">
        {orderedGroups.map((group) => (
          <div class="ootd-facet-group">
            <button type="button" class="ootd-chip ootd-chip-group" data-tag={GROUP_TAG + group}>
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

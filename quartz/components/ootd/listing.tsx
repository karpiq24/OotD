// Shared building blocks for card listings: folder pages, the people overview and the
// people catalog. Cards carry `data-search` / `data-tags` for ootdFilter.inline.ts.
import { JSX } from "preact"
import { Card } from "./Card"
import {
  alsoIn,
  coverImage,
  fold,
  folderName,
  groupOf,
  imageHref,
  pageTitle,
  plural,
  sectionId,
  stringList,
  summaryLine,
} from "./data"
import { QuartzPluginData } from "../../plugins/vfile"
import { BuildCtx, BuildTimeTrieData } from "../../util/ctx"
import { FileTrieNode } from "../../util/fileTrie"
import { FullSlug, resolveRelative } from "../../util/path"

export type TrieNode = FileTrieNode<BuildTimeTrieData>

export interface Listing {
  slug: FullSlug
  ctx: BuildCtx
  locale: string
  allFiles: QuartzPluginData[]
}

export function href(l: Listing, target: string): string {
  return resolveRelative(l.slug, target as FullSlug)
}

export function img(l: Listing, file: QuartzPluginData | null | undefined): string | undefined {
  const cover = coverImage(file)
  return cover ? imageHref(l.slug, cover) : undefined
}

export function byTitle(l: Listing) {
  return (a: string, b: string) =>
    a.localeCompare(b, l.locale, { numeric: true, sensitivity: "base" })
}

export function descendants(node: TrieNode): BuildTimeTrieData[] {
  return node.children.flatMap((child) =>
    child.isFolder ? descendants(child) : child.data ? [child.data] : [],
  )
}

export function nodeTitle(node: TrieNode): string {
  return node.data ? pageTitle(node.data) : node.displayName
}

export function PageCard({
  l,
  page,
  kicker,
  tags,
}: {
  l: Listing
  page: QuartzPluginData
  kicker?: string
  tags?: string[]
}) {
  const title = pageTitle(page)
  const meta = summaryLine(l.ctx, page)
  return (
    <Card
      href={href(l, page.slug!)}
      title={title}
      image={img(l, page)}
      kicker={kicker}
      meta={meta}
      search={fold([title, meta, kicker, ...stringList(page.frontmatter?.aliases)].join(" "))}
      tags={tags}
    />
  )
}

export function FolderCard({ l, node }: { l: Listing; node: TrieNode }) {
  const inside = descendants(node)
  const cover = img(l, node.data) ?? inside.map((f) => img(l, f)).find(Boolean)
  const title = nodeTitle(node)
  const meta = node.data?.frontmatter?.description as string | undefined
  return (
    <Card
      href={href(l, node.slug)}
      title={title}
      image={cover}
      kicker={`${inside.length} ${plural(inside.length, "wpis", "wpisy", "wpisów")}`}
      meta={meta}
      class="ootd-card-folder"
      search={fold([title, meta, ...inside.map((f) => pageTitle(f))].join(" "))}
    />
  )
}

// Pages elsewhere in the same top-level section that list `name` in `also_in`.
export function guestsOf(l: Listing, name: string, section: string): QuartzPluginData[] {
  return l.allFiles
    .filter(
      (f) =>
        f.relativePath?.startsWith(section + "/") &&
        folderName(f) !== name &&
        alsoIn(f).includes(name),
    )
    .sort((a, b) => byTitle(l)(pageTitle(a), pageTitle(b)))
}

export function FilterBox({ total, label }: { total: number; label: string }) {
  return (
    <div class="ootd-filter">
      <input
        class="ootd-filter-input"
        type="search"
        placeholder={label}
        aria-label={label}
        autocomplete="off"
      />
      <span class="ootd-filter-count" aria-live="polite" data-total={total}></span>
    </div>
  )
}

interface Group {
  name: string
  nodes: TrieNode[]
}

// A folder's children in sections by their `group:` frontmatter, ordered by the
// folder's own `groups:` list; ungrouped children come last.
export function groupChildren(l: Listing, folder: TrieNode): Group[] | undefined {
  const children = [...folder.children].sort((a, b) => {
    if (a.isFolder !== b.isFolder) return a.isFolder ? -1 : 1
    return byTitle(l)(nodeTitle(a), nodeTitle(b))
  })
  if (!children.some((c) => groupOf(c.data))) return undefined

  const order = stringList(folder.data?.frontmatter?.groups)
  const names = [...new Set(children.map((c) => groupOf(c.data) ?? "Pozostałe"))].sort((a, b) => {
    const ia = order.indexOf(a)
    const ib = order.indexOf(b)
    if (a === "Pozostałe" || b === "Pozostałe") return a === "Pozostałe" ? 1 : -1
    return (ia < 0 ? 999 : ia) - (ib < 0 ? 999 : ib) || byTitle(l)(a, b)
  })
  return names.map((name) => ({
    name,
    nodes: children.filter((c) => (groupOf(c.data) ?? "Pozostałe") === name),
  }))
}

export function ChildCards({ l, nodes }: { l: Listing; nodes: TrieNode[] }) {
  return (
    <div class="ootd-grid ootd-grid-pages">
      {nodes.map((node) =>
        node.isFolder ? (
          <FolderCard l={l} node={node} />
        ) : node.data ? (
          <PageCard l={l} page={node.data} />
        ) : null,
      )}
    </div>
  )
}

export function SectionNav({ names }: { names: string[] }) {
  return (
    <nav class="ootd-arc-nav" aria-label="Sekcje">
      {names.map((name) => (
        <a href={`#${sectionId(name)}`}>{name}</a>
      ))}
    </nav>
  )
}

export function GroupSections({
  l,
  groups,
  level = 2,
}: {
  l: Listing
  groups: Group[]
  level?: 2 | 3
}): JSX.Element {
  const Heading = level === 2 ? "h2" : "h3"
  return (
    <>
      {groups.map((group) => (
        <section class="ootd-arc" id={sectionId(group.name)} data-ootd-section>
          <header class="ootd-arc-head">
            <Heading>{group.name}</Heading>
          </header>
          <ChildCards l={l} nodes={group.nodes} />
        </section>
      ))}
    </>
  )
}

// subfolders first, then pages, each alphabetically
export function sortedChildren(l: Listing, folder: TrieNode): TrieNode[] {
  return [...folder.children].sort((a, b) => {
    if (a.isFolder !== b.isFolder) return a.isFolder ? -1 : 1
    return byTitle(l)(nodeTitle(a), nodeTitle(b))
  })
}

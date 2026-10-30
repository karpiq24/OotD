import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "../types"
import style from "../styles/ootd.scss"
import { Card } from "../ootd/Card"
import {
  Arc,
  coverImage,
  folderName,
  imageHref,
  isSessionPage,
  pageTitle,
  readArcs,
  sectionId,
  sessionInfo,
  SessionInfo,
  stringList,
  summaryLine,
} from "../ootd/data"
import {
  ChildCards,
  descendants,
  FilterBox,
  GroupSections,
  groupChildren,
  guestsOf,
  href as hrefFor,
  Listing,
  nodeTitle,
  PageCard,
  SectionNav,
  sortedChildren,
  TrieNode,
} from "../ootd/listing"
import { bridgeKind, NPC_ROOT, pagesAbout } from "../ootd/people"
// @ts-ignore
import script from "../scripts/ootdFilter.inline"
import { Element, ElementContent, Root } from "hast"
import { htmlToJsx } from "../../util/jsx"
import { QuartzPluginData } from "../../plugins/vfile"
import { ComponentChildren } from "preact"
import { trieFromAllFiles } from "../../util/ctx"
import { FullSlug, resolveRelative } from "../../util/path"

// A folder page: the index.md prose (minus the bullet list of links that the cards
// replace — update_indexes.py keeps that list for Obsidian), then an image card per page.
// The sessions folder groups its cards by the story arcs in Campaign_Context.md.

function textOutsideLinks(node: ElementContent): string {
  if (node.type === "text") return node.value
  if (node.type !== "element" || node.tagName === "a") return ""
  return node.children.map(textOutsideLinks).join("")
}

function hasLink(node: ElementContent): boolean {
  if (node.type !== "element") return false
  return node.tagName === "a" || node.children.some(hasLink)
}

function isLinkList(node: Root["children"][number]): boolean {
  if (node.type !== "element" || (node.tagName !== "ul" && node.tagName !== "ol")) return false
  const items = node.children.filter((c): c is Element => c.type === "element")
  return items.length > 0 && items.every((li) => hasLink(li) && !textOutsideLinks(li).trim())
}

interface SessionEntry {
  file: QuartzPluginData
  info: SessionInfo
}

function groupByArc(sessions: SessionEntry[], arcs: Arc[]) {
  const groups = arcs
    .map((arc) => ({
      arc,
      sessions: sessions.filter((s) => s.info.number >= arc.from && s.info.number <= arc.to),
    }))
    .filter((g) => g.sessions.length > 0)
  const grouped = new Set(groups.flatMap((g) => g.sessions))
  const rest = sessions.filter((s) => !grouped.has(s))
  if (rest.length > 0) {
    const numbers = rest.map((s) => s.info.number)
    groups.push({
      arc: { name: "Pozostałe sesje", from: Math.min(...numbers), to: Math.max(...numbers) },
      sessions: rest,
    })
  }
  // newest first, both the arcs and the sessions inside them
  return groups.sort((a, b) => b.arc.to - a.arc.to)
}

export default (() => {
  const CardFolderContent: QuartzComponent = (props: QuartzComponentProps) => {
    const { tree, fileData, allFiles, cfg, ctx } = props
    const slug = fileData.slug as FullSlug
    const href = (target: string) => resolveRelative(slug, target as FullSlug)
    const img = (file: QuartzPluginData | null | undefined) => {
      const cover = coverImage(file)
      return cover ? imageHref(slug, cover) : undefined
    }

    const trie = (ctx.trie ??= trieFromAllFiles(allFiles))
    const folder = trie.findNode(slug.split("/"))
    if (!folder) return null

    const root = tree as Root
    const prose = { ...root, children: root.children.filter((node) => !isLinkList(node)) }
    const hasProse = prose.children.some((n) => n.type !== "text" || n.value.trim())
    const content = (
      hasProse ? htmlToJsx(fileData.filePath!, prose) : undefined
    ) as ComponentChildren
    const classes = ((fileData.frontmatter?.cssclasses as string[] | undefined) ?? []).join(" ")

    const pages = folder.children.filter((c) => !c.isFolder && c.data).map((c) => c.data!)
    const sessions = pages
      .filter(isSessionPage)
      .flatMap((file) => {
        const info = sessionInfo(file)
        return info ? [{ file, info }] : []
      })
      .sort((a, b) => b.info.number - a.info.number)

    if (sessions.length > 0 && sessions.length === pages.length) {
      const groups = groupByArc(sessions, readArcs(ctx))
      const arcId = (arc: Arc) => `luk-${arc.from}`
      return (
        <div class="popover-hint ootd-folder">
          {content && <article class={classes}>{content}</article>}
          <nav class="ootd-arc-nav" aria-label="Łuki fabularne">
            {groups.map(({ arc }) => (
              <a href={`#${arcId(arc)}`}>{arc.name}</a>
            ))}
          </nav>
          {groups.map(({ arc, sessions }) => (
            <section class="ootd-arc" id={arcId(arc)}>
              <header class="ootd-arc-head">
                <div>
                  <h2>{arc.name}</h2>
                  {arc.subtitle && <p>{arc.subtitle}</p>}
                </div>
                <span class="ootd-kicker">
                  {arc.from === arc.to ? `Sesja ${arc.from}` : `Sesje ${arc.from}–${arc.to}`}
                </span>
              </header>
              <div class="ootd-grid ootd-grid-sessions">
                {sessions.map(({ file, info }) => (
                  <Card
                    href={href(file.slug!)}
                    title={info.title}
                    image={img(file)}
                    kicker={`Sesja ${info.number}`}
                    meta={info.date}
                    class="ootd-card-wide"
                  />
                ))}
              </div>
            </section>
          ))}
        </div>
      )
    }

    const l: Listing = { slug, ctx, locale: cfg.locale, allFiles }
    const name = folderName(fileData)
    const section = fileData.relativePath?.split("/")[0] ?? ""
    const guests = name ? guestsOf(l, name, section) : []
    const guestLabel = (fileData.frontmatter?.also_label as string | undefined) ?? "Również tutaj"
    const about = name && fileData.relativePath?.startsWith(NPC_ROOT) ? pagesAbout(l, name) : []
    const cardCount = descendants(folder).length + guests.length

    const seeAlso = about.length > 0 && (
      <p class="ootd-see-also">
        Zobacz też:{" "}
        {about.map((page, i) => (
          <>
            {i > 0 && ", "}
            <a href={hrefFor(l, page.slug!)}>{pageTitle(page)}</a> ({bridgeKind(page)})
          </>
        ))}
      </p>
    )
    const guestSection = guests.length > 0 && (
      <section class="ootd-arc" data-ootd-section>
        <header class="ootd-arc-head">
          <h2>{guestLabel}</h2>
        </header>
        <div class="ootd-grid ootd-grid-pages">
          {guests.map((page) => (
            <PageCard l={l} page={page} kicker={folderName(page)} />
          ))}
        </div>
      </section>
    )

    // `expand: [Bohaterowie, Factions, NPCs]`: show those subfolders' contents right here,
    // one section each, so the overview page is a directory rather than three doors
    const expand = stringList(fileData.frontmatter?.expand)
    if (expand.length > 0) {
      const subs = expand
        .map((sub) => folder.children.find((c) => c.isFolder && folderName(c.data ?? {}) === sub))
        .filter((c): c is TrieNode => !!c)
      const featured = pages.filter((p) => !subs.some((s) => s.data === p))
      return (
        <div class="popover-hint ootd-folder" data-ootd-filter>
          {content && <article class={classes}>{content}</article>}
          {featured.map((page) => (
            <a class="ootd-feature" href={hrefFor(l, page.slug!)}>
              <span class="ootd-feature-title">{pageTitle(page)} →</span>
              <span>{summaryLine(ctx, page)}</span>
            </a>
          ))}
          <SectionNav names={subs.map(nodeTitle)} />
          <FilterBox total={cardCount} label="Szukaj w tym dziale…" />
          {subs.map((sub) => {
            const groups = groupChildren(l, sub)
            return (
              <section class="ootd-expanded" id={sectionId(nodeTitle(sub))} data-ootd-section>
                <header class="ootd-arc-head">
                  <h2>{nodeTitle(sub)}</h2>
                  <a class="ootd-kicker" href={hrefFor(l, sub.slug)}>
                    Otwórz →
                  </a>
                </header>
                {groups ? (
                  <GroupSections l={l} groups={groups} level={3} />
                ) : (
                  <ChildCards l={l} nodes={sortedChildren(l, sub)} />
                )}
              </section>
            )
          })}
        </div>
      )
    }

    const groups = groupChildren(l, folder)
    return (
      <div class="popover-hint ootd-folder" data-ootd-filter>
        {content && <article class={classes}>{content}</article>}
        {seeAlso}
        {groups && <SectionNav names={groups.map((g) => g.name)} />}
        {cardCount > 8 && <FilterBox total={cardCount} label="Szukaj w tym folderze…" />}
        {groups ? (
          <GroupSections l={l} groups={groups} />
        ) : (
          <section data-ootd-section>
            <ChildCards l={l} nodes={sortedChildren(l, folder)} />
          </section>
        )}
        {guestSection}
      </div>
    )
  }

  CardFolderContent.css = style
  CardFolderContent.afterDOMLoaded = script
  return CardFolderContent
}) satisfies QuartzComponentConstructor

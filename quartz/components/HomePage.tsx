import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import style from "./styles/theme.scss"
import { Card } from "./rpg/Card"
import {
  coverImage,
  excerpt,
  heroTagline,
  imageHref,
  isSessionPage,
  pageTitle,
  sessionInfo,
} from "./rpg/data"
import { FullSlug, resolveRelative } from "../util/path"
import { layout, plural, t } from "../util/site"
import { QuartzPluginData } from "../plugins/vfile"

// The home page: banner hero with live counts, the latest session with an excerpt, the
// party's portraits and the section tiles. The structure is shared. The tiles are the layout's
// `home_sections` (site.json, from the manifest): a folder's tile takes its title, description
// and cover from its index.md, a single note's (Timeline) from home_sections and `covers`. The
// headings and the closing paragraph are the wiki's own, passed in from quartz.layout.ts.

export interface HomePageOptions {
  /** section tiles in display order (default: the layout's home_sections) */
  sections: string[]
  /** tile images, relative to the content root, for notes that have no cover of their own */
  covers: Record<string, string>
  /** heading over the party's portraits */
  partyTitle: string
  /** heading over the section tiles */
  sectionsTitle: string
  /** closing paragraph under the tiles, as HTML (none when empty) */
  footerHtml: string
}

function isPage(file: QuartzPluginData, prefix: string): boolean {
  return !!file.slug?.startsWith(prefix) && !file.slug.endsWith("index")
}

// How each section counts its pages; anything else counts entries
const NOUNS: Record<string, string> = {
  [layout.sessions_dir]: "session",
  [layout.people_dir]: "person",
  [layout.locations_dir]: "place",
  [layout.items_dir]: "item",
}

export default ((opts?: Partial<HomePageOptions>) => {
  const options: HomePageOptions = {
    sections: Object.keys(layout.home_sections ?? {}).length
      ? Object.keys(layout.home_sections)
      : [layout.sessions_dir, layout.people_dir, layout.locations_dir, layout.items_dir],
    covers: {},
    partyTitle: t("home_party"),
    sectionsTitle: t("home_sections"),
    footerHtml: "",
    ...opts,
  }
  const partyFolder = `${layout.people_dir}/${layout.party_subdir}/`

  const HomePage: QuartzComponent = ({ fileData, allFiles, ctx, cfg }: QuartzComponentProps) => {
    const slug = fileData.slug as FullSlug
    const href = (target: string) => resolveRelative(slug, target as FullSlug)
    const img = (file: QuartzPluginData | undefined) => {
      const cover = coverImage(file)
      return cover ? imageHref(slug, cover) : undefined
    }
    const count = (folder: string) => allFiles.filter((f) => isPage(f, folder + "/")).length

    const sessions = allFiles
      .filter(isSessionPage)
      .flatMap((file) => {
        const info = sessionInfo(file)
        return info ? [{ file, info }] : []
      })
      .sort((a, b) => b.info.number - a.info.number)
    const latest = sessions[0]
    const firstDate = sessions.at(-1)?.info.date
    const people = count(layout.people_dir)
    const places = count(layout.locations_dir)

    const party = allFiles
      .filter((f) => isPage(f, partyFolder))
      .sort((a, b) => pageTitle(a).localeCompare(pageTitle(b), cfg.locale))

    const banner = img(fileData)

    return (
      <div class="ootd-home">
        <header class="ootd-hero">
          {banner && <img class="ootd-hero-art" src={banner} alt="" />}
          <div class="ootd-hero-text">
            <h1 class="ootd-metal">{cfg.pageTitle}</h1>
            <p class="ootd-hero-stats">
              <span>
                <b>{sessions.length}</b> {plural(sessions.length, "session")}
              </span>
              <span>
                <b>{people}</b> {plural(people, "person")}
              </span>
              <span>
                <b>{places}</b> {plural(places, "place")}
              </span>
              {firstDate && latest?.info.date && (
                <span>
                  {firstDate} – {latest.info.date}
                </span>
              )}
            </p>
          </div>
        </header>

        {latest && (
          <section class="ootd-section">
            <h2 class="ootd-label">{t("latest_session")}</h2>
            <a class="ootd-latest" href={href(latest.file.slug!)}>
              <div class="ootd-latest-media">
                {img(latest.file) && <img src={img(latest.file)} alt="" />}
              </div>
              <div class="ootd-latest-text">
                <span class="ootd-kicker">
                  {t("session_label", { n: latest.info.number })}
                  {latest.info.date && ` · ${latest.info.date}`}
                </span>
                <h3>{latest.info.title}</h3>
                <p>{excerpt(ctx, latest.file)}</p>
                <span class="ootd-more">{t("read_recap")}</span>
              </div>
            </a>
          </section>
        )}

        {party.length > 0 && (
          <section class="ootd-section">
            <h2 class="ootd-label">{options.partyTitle}</h2>
            <div class="ootd-grid ootd-grid-heroes">
              {party.map((hero) => (
                <Card
                  href={href(hero.slug!)}
                  title={pageTitle(hero).split(" ")[0]}
                  image={img(hero)}
                  meta={heroTagline(ctx, hero)}
                  class="ootd-card-portrait"
                />
              ))}
            </div>
          </section>
        )}

        <section class="ootd-section">
          <h2 class="ootd-label">{options.sectionsTitle}</h2>
          <div class="ootd-grid ootd-grid-sections">
            {options.sections.flatMap((section) => {
              const file = allFiles.find((f) => f.slug === `${section}/index` || f.slug === section)
              if (!file) return []
              const isFolder = file.slug!.endsWith("/index")
              const text = isFolder ? undefined : layout.home_sections?.[section]
              const cover = options.covers[section]
              const n = isFolder ? count(section) : 0
              return [
                <Card
                  href={href(file.slug!)}
                  title={text?.title || pageTitle(file)}
                  image={cover ? imageHref(slug, cover) : img(file)}
                  kicker={n > 0 ? `${n} ${plural(n, NOUNS[section] ?? "entry")}` : undefined}
                  meta={text?.description || (file.frontmatter?.description as string | undefined)}
                  class="ootd-card-square"
                />,
              ]
            })}
          </div>
        </section>

        {options.footerHtml && (
          <p class="ootd-repo" dangerouslySetInnerHTML={{ __html: options.footerHtml }} />
        )}
      </div>
    )
  }

  HomePage.css = style
  return HomePage
}) satisfies QuartzComponentConstructor

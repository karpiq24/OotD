import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import style from "./styles/ootd.scss"
import { Card } from "./ootd/Card"
import {
  coverImage,
  excerpt,
  heroTagline,
  imageHref,
  isSessionPage,
  pageTitle,
  plural,
  sessionInfo,
} from "./ootd/data"
import { FullSlug, resolveRelative } from "../util/path"
import { QuartzPluginData } from "../plugins/vfile"

// Section tiles in display order; each folder's title, `description` and `cover` come
// from its index.md frontmatter. Timeline.md stays frontmatter-free (export_context.py
// hands its preamble to rpgnotes), so its tile is described here.
const SECTIONS = [
  "01-Sessions",
  "02-People",
  "03-Locations",
  "04-Items-and-Loot",
  "05-Lore",
  "06-Rules",
  "07-Handouts",
  "Timeline",
]

const SECTION_OVERRIDES: Record<string, { title: string; description: string; cover: string }> = {
  Timeline: {
    title: "Oś Czasu",
    description: "Chronologiczny zapis wydarzeń.",
    cover: "assets/sessions/080/tapniecie_mount_volkan_1.webp",
  },
}

// How each section counts its pages; anything else counts "wpisy"
const NOUNS: Record<string, [string, string, string]> = {
  "01-Sessions": ["sesja", "sesje", "sesji"],
  "02-People": ["postać", "postacie", "postaci"],
  "03-Locations": ["miejsce", "miejsca", "miejsc"],
  "04-Items-and-Loot": ["przedmiot", "przedmioty", "przedmiotów"],
}

const HERO_FOLDER = "02-People/Bohaterowie/"

export const REPO_URL = "https://github.com/karpiq24/OotD"

function isPage(file: QuartzPluginData, prefix: string): boolean {
  return !!file.slug?.startsWith(prefix) && !file.slug.endsWith("index")
}

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
  const people = count("02-People")
  const places = count("03-Locations")

  const heroes = allFiles
    .filter((f) => isPage(f, HERO_FOLDER))
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
              <b>{sessions.length}</b> {plural(sessions.length, "sesja", "sesje", "sesji")}
            </span>
            <span>
              <b>{people}</b> {plural(people, "postać", "postacie", "postaci")}
            </span>
            <span>
              <b>{places}</b> {plural(places, "miejsce", "miejsca", "miejsc")}
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
          <h2 class="ootd-label">Ostatnia sesja</h2>
          <a class="ootd-latest" href={href(latest.file.slug!)}>
            <div class="ootd-latest-media">
              {img(latest.file) && <img src={img(latest.file)} alt="" />}
            </div>
            <div class="ootd-latest-text">
              <span class="ootd-kicker">
                Sesja {latest.info.number}
                {latest.info.date && ` · ${latest.info.date}`}
              </span>
              <h3>{latest.info.title}</h3>
              <p>{excerpt(ctx, latest.file)}</p>
              <span class="ootd-more">Czytaj kronikę →</span>
            </div>
          </a>
        </section>
      )}

      {heroes.length > 0 && (
        <section class="ootd-section">
          <h2 class="ootd-label">Bohaterowie Przepowiedni</h2>
          <div class="ootd-grid ootd-grid-heroes">
            {heroes.map((hero) => (
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
        <h2 class="ootd-label">Kronika Thylei</h2>
        <div class="ootd-grid ootd-grid-sections">
          {SECTIONS.flatMap((section) => {
            const file = allFiles.find((f) => f.slug === `${section}/index` || f.slug === section)
            if (!file) return []
            const override = SECTION_OVERRIDES[section]
            const n = file.slug!.endsWith("/index") ? count(section) : 0
            return [
              <Card
                href={href(file.slug!)}
                title={override?.title ?? pageTitle(file)}
                image={override ? imageHref(slug, override.cover) : img(file)}
                kicker={
                  n > 0
                    ? `${n} ${plural(n, ...(NOUNS[section] ?? ["wpis", "wpisy", "wpisów"]))}`
                    : undefined
                }
                meta={
                  override?.description ?? (file.frontmatter?.description as string | undefined)
                }
                class="ootd-card-square"
              />,
            ]
          })}
        </div>
      </section>

      <p class="ootd-repo">
        Cała wiki to pliki Markdown w publicznym repozytorium{" "}
        <a href={REPO_URL}>karpiq24/OotD na GitHubie</a>. Możesz je sklonować albo wpuścić tam
        swojego agenta: sesje, postacie i miejsca leżą w katalogu <code>content/</code>.
      </p>
    </div>
  )
}

HomePage.css = style

export default (() => HomePage) satisfies QuartzComponentConstructor

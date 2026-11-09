// The campaign's site settings: `site.json` at the wiki root, written by `rpg-tools site sync`
// from the campaign manifest (the wiki layout's folder names, the language, the interface
// strings). The shared components and plugins read folder names and labels from here; the
// look (colours, fonts, home-page texts) stays in quartz.config.ts, quartz.layout.ts and the scss.
import fs from "fs"
import path from "path"

export interface SiteLayout {
  sessions_dir: string
  session_assets_dir: string
  /** session notes are "<word> <n> - <title>.md" */
  session_word: string
  campaign_context_file: string
  people_dir: string
  party_subdir: string
  factions_subdir: string
  npcs_subdir: string
  locations_dir: string
  items_dir: string
  /** the home page's tiles in order: folder or note → its title and description */
  home_sections: Record<string, { title: string; description: string }>
}

export interface SiteConfig {
  schema_version: number
  language: string
  layout: SiteLayout
  strings: Record<string, string>
}

export const SITE_FILE = "site.json"

function load(): SiteConfig {
  let raw: string
  try {
    raw = fs.readFileSync(SITE_FILE, "utf-8")
  } catch {
    throw new Error(`${SITE_FILE} is missing: run \`rpg-tools site sync\` in the wiki repo`)
  }
  return JSON.parse(raw) as SiteConfig
}

export const site: SiteConfig = load()
export const layout: SiteLayout = site.layout

/** An interface string, with `{name}` placeholders filled in. */
export function t(key: string, vars: Record<string, string | number> = {}): string {
  const text = site.strings[key]
  if (text === undefined) throw new Error(`${SITE_FILE} has no string "${key}"`)
  return text.replace(/\{(\w+)\}/g, (match, name: string) =>
    name in vars ? String(vars[name]) : match,
  )
}

/** The plural form of the noun `key` (`<key>_one`, `<key>_few`, `<key>_many`) for `n`. */
export function plural(n: number, key: string): string {
  if (n === 1) return t(`${key}_one`)
  if (site.language === "pl") {
    // Polish: 2–4 sesje (but 12–14 sesji), 5+ sesji
    const lastTwo = n % 100
    const last = n % 10
    if (last >= 2 && last <= 4 && (lastTwo < 12 || lastTwo > 14)) return t(`${key}_few`)
  }
  return t(`${key}_many`)
}

/** The site icon in quartz/static/: the theme's icon.svg when it has one, else icon.png. */
export const ICON_FILE = fs.existsSync(path.join("quartz", "static", "icon.svg"))
  ? "icon.svg"
  : "icon.png"

export function escapeRegex(text: string): string {
  return text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")
}

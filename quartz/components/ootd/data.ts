// Build-time data for the OotD home page and the card-style folder pages:
// cover images, session numbers/dates, story arcs and recap excerpts.
import fs from "fs"
import path from "path"
import { QuartzPluginData } from "../../plugins/vfile"
import { BuildCtx } from "../../util/ctx"
import {
  FilePath,
  FullSlug,
  isAbsoluteURL,
  joinSegments,
  pathToRoot,
  slugifyFilePath,
} from "../../util/path"

const PLACEHOLDER = /(^|\/)placeholder\.webp$/

// The page's cover: frontmatter `cover`, else its first image (found by OgImageExtractor).
// Returned relative to the content root, e.g. "assets/sessions/084/x.webp".
export function coverImage(file: QuartzPluginData | null | undefined): string | undefined {
  const raw = (file?.frontmatter?.cover ?? file?.frontmatter?.socialImage) as string | undefined
  if (!raw || typeof raw !== "string" || !file?.relativePath) return undefined
  if (isAbsoluteURL(raw)) return raw

  let src = raw.trim().replace(/^<|>$/g, "")
  try {
    src = decodeURI(src)
  } catch {}
  // a bare `assets/...` is root-relative; anything else resolves against the page's folder
  const resolved = src.startsWith("assets/")
    ? src
    : path.posix.normalize(path.posix.join(path.posix.dirname(file.relativePath), src))
  if (resolved.startsWith("..") || PLACEHOLDER.test(resolved)) return undefined
  return resolved
}

export function imageHref(currentSlug: FullSlug, image: string): string {
  if (isAbsoluteURL(image)) return image
  return joinSegments(pathToRoot(currentSlug), slugifyFilePath(image as FilePath))
}

export function pageTitle(file: QuartzPluginData): string {
  return (file.frontmatter?.title as string | undefined) ?? file.slug?.split("/").at(-1) ?? ""
}

export interface SessionInfo {
  number: number
  title: string
  date?: string
}

const SESSION_TITLE = /^Sesja\s+(\d+)\s*[:\-–]\s*(.*)$/
const SESSION_DATE = /Data\W{0,4}(\d{1,2}\.\d{1,2}\.\d{4})/

export function sessionInfo(file: QuartzPluginData): SessionInfo | undefined {
  const match = pageTitle(file).match(SESSION_TITLE)
  if (!match) return undefined
  const date = file.text?.slice(0, 400).match(SESSION_DATE)?.[1]
  return { number: Number(match[1]), title: match[2].trim(), date }
}

export function isSessionPage(file: QuartzPluginData): boolean {
  return !!file.slug?.startsWith("01-Sessions/") && !file.slug.endsWith("index")
}

export interface Arc {
  name: string
  subtitle?: string
  from: number
  to: number
}

// Story arcs are the `### Name: subtitle (Sesje 1-10)` headings of Campaign_Context.md.
const ARC_HEADING = /^###\s+(.+?)\s*\(Sesj[aei]\s+(\d+)(?:\s*[-–]\s*(\d+))?\)\s*$/gm

export function readArcs(ctx: BuildCtx): Arc[] {
  const raw = readContent(ctx, "Campaign_Context.md")
  if (!raw) return []
  return [...raw.matchAll(ARC_HEADING)].map((m) => {
    const [name, ...rest] = m[1].split(":")
    const from = Number(m[2])
    return {
      name: name.trim(),
      subtitle: rest.join(":").trim() || undefined,
      from,
      to: m[3] ? Number(m[3]) : from,
    }
  })
}

function readContent(ctx: BuildCtx, relativePath: string): string | undefined {
  try {
    return fs.readFileSync(path.join(ctx.argv.directory, relativePath), "utf-8")
  } catch {
    return undefined
  }
}

// Plain text of the first prose paragraph of a page (skipping images, headings, prompt links).
export function excerpt(
  ctx: BuildCtx,
  file: QuartzPluginData,
  maxLength = 260,
): string | undefined {
  if (!file.relativePath) return undefined
  const raw = readContent(ctx, file.relativePath)
  if (!raw) return undefined
  const body = raw.replace(/^---[\s\S]*?\n---\s*\n/, "")
  const paragraph = body
    .split(/\n\s*\n/)
    .map((p) => p.trim())
    .find((p) => p.length > 80 && !/^(#|!\[|\[|>|\||-|\*\*Data)/.test(p))
  if (!paragraph) return undefined

  const text = paragraph
    .replace(/\[\[[^\]|]*\|([^\]]*)\]\]/g, "$1")
    .replace(/\[\[([^\]]*)\]\]/g, "$1")
    .replace(/\[([^\]]*)\]\([^)]*\)/g, "$1")
    .replace(/[*_`]/g, "")
    .replace(/\s+/g, " ")
    .trim()
  if (text.length <= maxLength) return text
  const cut = text.slice(0, maxLength)
  return cut.slice(0, cut.lastIndexOf(" ")).replace(/[,;:—–-]$/, "") + "…"
}

// Polish plural: 1 sesja, 2–4 sesje, 5+ sesji
export function plural(n: number, one: string, few: string, many: string): string {
  if (n === 1) return one
  const lastTwo = n % 100
  const last = n % 10
  if (last >= 2 && last <= 4 && (lastTwo < 12 || lastTwo > 14)) return few
  return many
}

// A hero's class and epic path from the two italic lines under their portrait:
// `_Elf Druid, [[...|The Seeking One]]_` and `_**Poszukujący**, który ..._`
export function heroTagline(ctx: BuildCtx, file: QuartzPluginData): string | undefined {
  if (!file.relativePath) return undefined
  const raw = readContent(ctx, file.relativePath)
  if (!raw) return undefined
  const italics = raw.split("\n").filter((line) => /^_.*_\s*$/.test(line.trim()))
  const heroClass = italics
    .find((line) => !line.startsWith("_**"))
    ?.replace(/^_|_\s*$/g, "")
    .split(",")[0]
    .trim()
  const epithet = italics.map((line) => line.match(/^_\*\*([^*]+)\*\*/)?.[1]).find(Boolean)
  return [heroClass, epithet].filter(Boolean).join(" · ") || undefined
}

// Folders a page also belongs to besides the one it lives in, from frontmatter
// `also_in: [Mytros, "[[Bohaterowie]]"]`; matched by folder name within the same section.
export function alsoIn(file: QuartzPluginData): string[] {
  const raw = file.frontmatter?.also_in
  const values = Array.isArray(raw) ? raw : typeof raw === "string" ? [raw] : []
  return values
    .filter((v): v is string => typeof v === "string")
    .map((v) =>
      v
        .replace(/^\[\[|\]\]$/g, "")
        .split("|")[0]
        .trim(),
    )
    .filter(Boolean)
}

export function folderName(file: QuartzPluginData): string | undefined {
  if (!file.relativePath) return undefined
  return path.posix.basename(path.posix.dirname(file.relativePath))
}

const summaryCache = new Map<string, { mtime: number; summary: string | undefined }>()

// The one-line "who is this" under a page's portrait: its first italic line
// (`_Złodziejka i członkini Kultu Węża._`), else the first prose sentence.
export function summaryLine(
  ctx: BuildCtx,
  file: QuartzPluginData,
  maxLength = 110,
): string | undefined {
  if (!file.relativePath) return undefined
  const fullPath = path.join(ctx.argv.directory, file.relativePath)
  let mtime = 0
  try {
    mtime = fs.statSync(fullPath).mtimeMs
  } catch {
    return undefined
  }
  const cached = summaryCache.get(fullPath)
  if (cached && cached.mtime === mtime) return cached.summary

  const raw = readContent(ctx, file.relativePath) ?? ""
  const body = raw.replace(/^---[\s\S]*?\n---\s*\n/, "")
  const italic = body
    .split("\n")
    .map((line) => line.trim())
    .find((line) => /^_[^_].*_$/.test(line))
  let summary: string | undefined
  if (italic) {
    const text = plainText(italic.slice(1, -1))
    summary = text.length > maxLength ? truncate(text, maxLength) : text
  } else {
    summary = excerpt(ctx, file, maxLength)
  }
  summaryCache.set(fullPath, { mtime, summary })
  return summary
}

function plainText(markdown: string): string {
  return markdown
    .replace(/\[\[[^\]|]*\|([^\]]*)\]\]/g, "$1")
    .replace(/\[\[([^\]]*)\]\]/g, "$1")
    .replace(/\[([^\]]*)\]\([^)]*\)/g, "$1")
    .replace(/[*_`]/g, "")
    .replace(/\s+/g, " ")
    .trim()
}

function truncate(text: string, maxLength: number): string {
  const cut = text.slice(0, maxLength)
  return cut.slice(0, cut.lastIndexOf(" ")).replace(/[,;:—–-]$/, "") + "…"
}

// Lowercase without diacritics, so "zakon wezy" finds "Kult Węża"; the filter script folds the same way.
export function fold(text: string): string {
  return text
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/ł/g, "l")
}

// A folder's (or page's) `group:` from frontmatter, used to section folder pages.
export function groupOf(file: QuartzPluginData | null | undefined): string | undefined {
  const group = file?.frontmatter?.group
  return typeof group === "string" && group.trim() ? group.trim() : undefined
}

export function stringList(value: unknown): string[] {
  if (Array.isArray(value)) return value.filter((v): v is string => typeof v === "string")
  return typeof value === "string" ? [value] : []
}

export function sectionId(name: string): string {
  return (
    "grupa-" +
    fold(name)
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-|-$/g, "")
  )
}

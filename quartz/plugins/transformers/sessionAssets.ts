import { QuartzTransformerPlugin } from "../types"
import { Root } from "mdast"
import fs from "fs"
import path from "path"

export interface SessionAssetLink {
  label: string
  url: string
}

export interface SessionAssetGroup {
  category: string
  files: SessionAssetLink[]
}

// Ordered category buckets. The order here is the order they render in.
const CATEGORY_ORDER = [
  "Transkrypty",
  "Logi czatu",
  "Dane",
  "Raporty",
  "Wideo",
  "Obrazki",
  "Prompty",
  "Pozostałe",
] as const

// Exact-name mapping: filename -> [category, label]
const KNOWN_FILES: Record<string, { category: string; label: string }> = {
  "transcript.txt": { category: "Transkrypty", label: "Transkrypt (txt)" },
  "transcript.json": { category: "Transkrypty", label: "Transkrypt (json)" },
  "transcript_enriched.txt": { category: "Transkrypty", label: "Transkrypt wzbogacony" },
  "chat_log.json": { category: "Logi czatu", label: "Chat log" },
  "chat_events.json": { category: "Logi czatu", label: "Zdarzenia czatu (json)" },
  "chat_events.txt": { category: "Logi czatu", label: "Zdarzenia czatu (txt)" },
  "quotes.json": { category: "Dane", label: "Cytaty" },
  "visual_log.json": { category: "Dane", label: "Log wizualny" },
  "validation_report.md": { category: "Raporty", label: "Raport walidacji" },
  "video_script.md": { category: "Wideo", label: "Skrypt wideo" },
}

// Determine which category a file belongs to and how to label it.
function categorize(filename: string): { category: string; label: string } {
  const known = KNOWN_FILES[filename]
  if (known) {
    return known
  }
  const ext = path.extname(filename).toLowerCase()
  if (ext === ".webp") {
    return { category: "Obrazki", label: filename }
  }
  if (ext === ".txt") {
    return { category: "Prompty", label: filename }
  }
  return { category: "Pozostałe", label: filename }
}

// Build the ordered, grouped asset structure for a session's asset directory.
function buildGroups(assetsDir: string, sessionId: string): SessionAssetGroup[] {
  const entries = fs
    .readdirSync(assetsDir, { withFileTypes: true })
    .filter((e) => e.isFile())
    .map((e) => e.name)

  const byCategory = new Map<string, SessionAssetLink[]>()
  for (const filename of entries) {
    const { category, label } = categorize(filename)
    const link: SessionAssetLink = {
      label,
      url: `../assets/sessions/${sessionId}/${filename}`,
    }
    const bucket = byCategory.get(category)
    if (bucket) {
      bucket.push(link)
    } else {
      byCategory.set(category, [link])
    }
  }

  const groups: SessionAssetGroup[] = []
  for (const category of CATEGORY_ORDER) {
    const files = byCategory.get(category)
    if (files && files.length > 0) {
      files.sort((a, b) => a.label.localeCompare(b.label, "pl"))
      groups.push({ category, files })
    }
  }
  return groups
}

export const SessionAssets: QuartzTransformerPlugin = () => {
  return {
    name: "SessionAssets",
    markdownPlugins() {
      return [
        () => {
          return (_tree: Root, file) => {
            const fullFp = file.data.filePath
            if (!fullFp) {
              return
            }

            const basename = path.basename(fullFp)
            const match = basename.match(/Sesja\s+(\d+)/)
            if (!match) {
              return
            }

            const sessionId = match[1].padStart(3, "0")
            // content/01-Sessions/<file>.md -> content/assets/sessions/<NNN>
            const assetsDir = path.join(path.dirname(fullFp), "..", "assets", "sessions", sessionId)
            if (!fs.existsSync(assetsDir)) {
              return
            }

            const groups = buildGroups(assetsDir, sessionId)
            if (groups.length > 0) {
              file.data.sessionAssets = groups
            }
          }
        },
      ]
    },
  }
}

declare module "vfile" {
  interface DataMap {
    sessionAssets?: SessionAssetGroup[]
  }
}

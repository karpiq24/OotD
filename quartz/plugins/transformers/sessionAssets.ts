import { QuartzTransformerPlugin } from "../types"
import { Root } from "mdast"
import fs from "fs"
import path from "path"
import { escapeRegex, layout, site, t } from "../../util/site"

export interface SessionAssetLink {
  label: string
  url: string
}

export interface SessionAssetGroup {
  category: string
  files: SessionAssetLink[]
}

// Ordered category buckets (site.json strings `asset_<key>`). The order here is the order
// they render in.
const CATEGORY_ORDER = ["transcripts", "chat_logs", "data", "images", "prompts", "other"]

// rpgnotes' session package: exact file name -> [category, label key]
const KNOWN_FILES: Record<string, { category: string; label: string }> = {
  "transcript.txt": { category: "transcripts", label: "transcript_txt" },
  "transcript.json": { category: "transcripts", label: "transcript_json" },
  "transcript_enriched.txt": { category: "transcripts", label: "transcript_enriched" },
  "chat_log.json": { category: "chat_logs", label: "chat_log" },
  "chat_events.json": { category: "chat_logs", label: "chat_events_json" },
  "chat_events.txt": { category: "chat_logs", label: "chat_events_txt" },
  "quotes.json": { category: "data", label: "quotes" },
  "visual_log.json": { category: "data", label: "visual_log" },
}

const SESSION_FILE = new RegExp(escapeRegex(layout.session_word) + "\\s+(\\d+)")

// rpgnotes' working files and bookkeeping: they sit in the session's asset
// folder but are not listed (and quartz.config.ts's ignorePatterns keeps them
// off the site).
const NEVER_PUBLISHED = [
  /^draft/,
  /^validation_report/,
  /^details\.json$/,
  /^manifest\.json$/,
  /^\./,
]

// Determine which category a file belongs to and how to label it.
function categorize(filename: string): { category: string; label: string } {
  const known = KNOWN_FILES[filename]
  if (known) {
    return { category: known.category, label: t(`asset_${known.label}`) }
  }
  const ext = path.extname(filename).toLowerCase()
  if (ext === ".webp") {
    return { category: "images", label: filename }
  }
  if (ext === ".txt") {
    return { category: "prompts", label: filename }
  }
  return { category: "other", label: filename }
}

// Build the ordered, grouped asset structure for a session's asset directory.
function buildGroups(assetsDir: string, assetsUrl: string): SessionAssetGroup[] {
  const entries = fs
    .readdirSync(assetsDir, { withFileTypes: true })
    .filter((e) => e.isFile())
    .map((e) => e.name)
    .filter((name) => !NEVER_PUBLISHED.some((pattern) => pattern.test(name)))

  const byCategory = new Map<string, SessionAssetLink[]>()
  for (const filename of entries) {
    const { category, label } = categorize(filename)
    const link: SessionAssetLink = {
      label,
      url: `${assetsUrl}/${filename}`,
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
      files.sort((a, b) => a.label.localeCompare(b.label, site.language))
      groups.push({ category: t(`asset_${category}`), files })
    }
  }
  return groups
}

export const SessionAssets: QuartzTransformerPlugin = () => {
  return {
    name: "SessionAssets",
    markdownPlugins(ctx) {
      return [
        () => {
          return (_tree: Root, file) => {
            const fullFp = file.data.filePath
            if (!fullFp) {
              return
            }

            const basename = path.basename(fullFp)
            const match = basename.match(SESSION_FILE)
            if (!match) {
              return
            }

            const sessionId = match[1].padStart(3, "0")
            // OotD: content/01-Sessions/<file>.md -> content/assets/sessions/<NNN>
            const assetsDir = path.join(ctx.argv.directory, layout.session_assets_dir, sessionId)
            if (!fs.existsSync(assetsDir)) {
              return
            }

            // linked from the note's own folder, like the browser resolves it
            const noteDir = path.posix.dirname(file.data.relativePath ?? fullFp)
            const assetsUrl = path.posix.relative(
              noteDir,
              path.posix.join(layout.session_assets_dir, sessionId),
            )
            const groups = buildGroups(assetsDir, assetsUrl)
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

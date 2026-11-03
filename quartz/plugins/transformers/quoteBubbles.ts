// Quote callouts as speech bubbles with the speaker's portrait.
//
//   > [!quote] Arevon
//   > Jesteś oskarżony o zdradę stanu.
//
// The callout title is the speaker. It is looked up among the person pages in
// content/02-People/ (file name, title, aliases); the portrait is that page's first
// image, so post-war pages show the aged one. Runs after ObsidianFlavoredMarkdown,
// which has already turned the blockquote into a callout. Consecutive quotes
// alternate sides, like an exchange. A speaker with no page gets the bubble only.
import fs from "fs"
import path from "path"
import matter from "gray-matter"
import { Root, Blockquote, Parent } from "mdast"
import { QuartzTransformerPlugin } from "../types"

const PEOPLE_DIR = "02-People"
const PLACEHOLDER = /(^|\/)placeholder\.(webp|png)$/
const MD_IMAGE = /!\[[^\]]*\]\(\s*<?([^)>]+?)>?\s*\)/
const WIKI_IMAGE = /!\[\[([^\]|]+)(?:\|[^\]]*)?\]\]/
const TITLE_INNER = /class="callout-title-inner">([\s\S]*?)<\/div>/

const key = (name: string) => name.normalize("NFC").trim().toLowerCase()

function walk(dir: string, out: string[] = []): string[] {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name)
    if (entry.isDirectory()) walk(full, out)
    else if (entry.name.endsWith(".md") && entry.name !== "index.md") out.push(full)
  }
  return out
}

// first non-placeholder image of the page, relative to the content root
function firstImage(body: string, pageRel: string): string | undefined {
  for (const line of body.split("\n")) {
    const md = line.match(MD_IMAGE)
    const wiki = md ? undefined : line.match(WIKI_IMAGE)
    let src = md?.[1] ?? wiki?.[1]
    if (!src || PLACEHOLDER.test(src) || /^https?:/.test(src)) continue
    try {
      src = decodeURI(src)
    } catch {}
    if (wiki) return src.startsWith("assets/") ? src : `assets/${src}`
    return path.posix.normalize(path.posix.join(path.posix.dirname(pageRel), src))
  }
  return undefined
}

function portraitIndex(contentDir: string): Map<string, string> {
  const index = new Map<string, string>()
  const root = path.join(contentDir, PEOPLE_DIR)
  if (!fs.existsSync(root)) return index
  for (const file of walk(root)) {
    const rel = path.relative(contentDir, file).split(path.sep).join("/")
    const { data, content } = matter(fs.readFileSync(file, "utf8"))
    const image = firstImage(content, rel)
    if (!image || image.startsWith("..")) continue
    const aliases = Array.isArray(data.aliases) ? data.aliases : data.aliases ? [data.aliases] : []
    for (const name of [path.basename(file, ".md"), data.title, ...aliases]) {
      if (typeof name === "string" && name.trim() && !index.has(key(name))) {
        index.set(key(name), image)
      }
    }
  }
  return index
}

const isQuote = (node: any): node is Blockquote =>
  node?.type === "blockquote" && node.data?.hProperties?.["data-callout"] === "quote"

function speakerOf(node: Blockquote): string | undefined {
  const title = node.children[0] as any
  if (title?.type !== "html") return undefined
  const inner = title.value.match(TITLE_INNER)?.[1]
  return inner
    ?.replace(/<[^>]+>/g, "")
    .replace(/\s+/g, " ")
    .trim()
}

export const QuoteBubbles: QuartzTransformerPlugin = () => {
  return {
    name: "QuoteBubbles",
    markdownPlugins(ctx) {
      const portraits = portraitIndex(ctx.argv.directory)
      return [
        () => (tree: Root, file) => {
          const pageDir = path.posix.dirname(file.data.relativePath ?? "")
          const visitParent = (parent: Parent) => {
            let run = 0
            for (const child of parent.children as any[]) {
              if (!isQuote(child)) {
                run = 0
                if (Array.isArray(child.children)) visitParent(child)
                continue
              }
              const speaker = speakerOf(child)
              const image = speaker ? portraits.get(key(speaker)) : undefined
              const side = run % 2 === 1 ? "ootd-voice-right" : "ootd-voice-left"
              run += 1

              const bubble: any = {
                type: "blockquote",
                data: { hName: "div", hProperties: { className: ["ootd-voice-bubble"] } },
                children: child.children,
              }
              const children: any[] = [bubble]
              if (image) {
                const src = path.posix.relative(pageDir, image)
                children.unshift({
                  type: "paragraph",
                  children: [],
                  data: {
                    hName: "img",
                    hProperties: {
                      src,
                      alt: speaker,
                      className: ["ootd-voice-portrait"],
                      loading: "lazy",
                    },
                  },
                })
              }
              child.children = children
              const props = child.data!.hProperties as Record<string, unknown>
              props.className = [
                String(props.className ?? ""),
                "ootd-voice",
                side,
                image ? "" : "ootd-voice-noportrait",
              ]
                .join(" ")
                .trim()
            }
          }
          visitParent(tree)
        },
      ]
    },
  }
}

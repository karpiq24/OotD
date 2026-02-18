import { QuartzTransformerPlugin } from "../types"
import { Root } from "mdast"
import { visit } from "unist-util-visit"

interface Options {
  priority: number
}

export const OgImageExtractor: QuartzTransformerPlugin<Partial<Options>> = () => {
  return {
    name: "OgImageExtractor",
    markdownPlugins() {
      return [
        () => {
          return (tree: Root, file) => {
            if (file.data.frontmatter?.socialImage) {
              return
            }

            let foundImage: string | undefined

            visit(tree, (node: any) => {
              if (foundImage) return

              if (node.type === "image") {
                foundImage = node.url
                return
              }

              if (node.type === "html" && node.value.includes("<img")) {
                const srcMatch = node.value.match(/src=["'](.*?)["']/)
                if (srcMatch) {
                  foundImage = srcMatch[1]
                  return
                }
              }

              // Check for text/raw nodes that might contain wikilinks
              if (node.type === "text" || node.type === "raw") {
                 const wikiMatch = node.value.match(/!\[\[(.*?)\]\]/)
                 if (wikiMatch) {
                   let potentialImage = wikiMatch[1]
                   if (potentialImage.includes("|")) {
                     potentialImage = potentialImage.split("|")[0]
                   }
                   foundImage = potentialImage
                   return
                 }
              }
            })

            if (foundImage) {
               if (!file.data.frontmatter) {
                   // Cast to any to avoid strict type checks on partial frontmatter during init
                   file.data.frontmatter = { title: "Untitled", socialImage: foundImage } as any
               } else {
                   file.data.frontmatter.socialImage = foundImage
               }
            }
          }
        },
      ]
    },
  }
}

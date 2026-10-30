import { QuartzConfig } from "./quartz/cfg"
import * as Plugin from "./quartz/plugins"
import * as Component from "./quartz/components"

/**
 * Quartz 4 Configuration
 *
 * See https://quartz.jzhao.xyz/configuration for more information.
 */
const config: QuartzConfig = {
  configuration: {
    pageTitle: "Odyseja Smoczych Lordów",
    pageTitleSuffix: "",
    enableSPA: true,
    enablePopovers: true,
    analytics: null,
    locale: "pl-PL",
    baseUrl: "karpiq24.github.io/OotD",
    ignorePatterns: [
      "private",
      "templates",
      ".obsidian",
      "99-DM-Corner",
      // rpgnotes working files: /import-session keeps them in private/, this
      // keeps one that slips into a session's asset folder off the site.
      "assets/sessions/*/draft*",
      "assets/sessions/*/validation_report*",
      "assets/sessions/*/details.json",
      "assets/sessions/*/manifest.json",
    ],
    defaultDateType: "modified",
    theme: {
      fontOrigin: "googleFonts",
      cdnCaching: true,
      // "Brąz i Patyna": Cinzel capitals like carved stelae; marble, bronze (tertiary)
      // and verdigris (secondary). Extra tokens are in quartz/styles/custom.scss.
      typography: {
        header: { name: "Cinzel", weights: [500, 700] },
        // Alegreya Sans has no 600, so name the weights it does have
        body: { name: "Alegreya Sans", weights: [400, 500, 700], includeItalic: true },
        code: "IBM Plex Mono",
      },
      colors: {
        lightMode: {
          light: "#f1efea",
          lightgray: "#d9d3c7",
          gray: "#8f877a",
          darkgray: "#3a3731",
          dark: "#23211c",
          secondary: "#2d6a5f",
          tertiary: "#94632a",
          highlight: "rgba(148, 99, 42, 0.10)",
          textHighlight: "#e9c57c88",
        },
        darkMode: {
          light: "#111614",
          lightgray: "#2b3532",
          gray: "#7d8a84",
          darkgray: "#d6d0c3",
          dark: "#ece5d6",
          secondary: "#63b2a0",
          tertiary: "#d39a50",
          highlight: "rgba(211, 154, 80, 0.10)",
          textHighlight: "#a4772f88",
        },
      },
    },
  },
  plugins: {
    transformers: [
      Plugin.FrontMatter(),
      Plugin.OgImageExtractor(),
      Plugin.SessionAssets(),
      Plugin.CreatedModifiedDate({
        priority: ["frontmatter", "git", "filesystem"],
      }),
      Plugin.SyntaxHighlighting({
        theme: {
          light: "github-light",
          dark: "github-dark",
        },
        keepBackground: false,
      }),
      Plugin.ObsidianFlavoredMarkdown({ enableInHtmlEmbed: false }),
      Plugin.GitHubFlavoredMarkdown(),
      Plugin.TableOfContents(),
      Plugin.CrawlLinks({ markdownLinkResolution: "shortest" }),
      Plugin.Description(),
      Plugin.Latex({ renderEngine: "katex" }),
    ],
    filters: [Plugin.RemoveDrafts()],
    emitters: [
      Plugin.AliasRedirects(),
      Plugin.ComponentResources(),
      Plugin.ContentPage(),
      Plugin.FolderPage({ pageBody: Component.CardFolderContent() }),
      Plugin.TagPage(),
      Plugin.ContentIndex({
        enableSiteMap: true,
        enableRSS: true,
      }),
      Plugin.Assets(),
      Plugin.Static(),
      Plugin.Favicon(),
      Plugin.NotFoundPage(),
      // Comment out CustomOgImages to speed up build time
      Plugin.CustomOgImages(),
    ],
  },
}

export default config

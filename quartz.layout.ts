import { PageLayout, SharedLayout } from "./quartz/cfg"
import * as Component from "./quartz/components"
import { QuartzComponentProps } from "./quartz/components/types"

const isHome = (page: QuartzComponentProps) => page.fileData.slug === "index"
const notHome = (page: QuartzComponentProps) => !isHome(page)

// The home page's structure is shared (rpg-tools site/); its texts are this wiki's. The tiles
// and their texts are the manifest's home_sections (site.json); Timeline.md stays
// frontmatter-free (export-context hands its preamble to rpgnotes), so its cover is set here.
const homePage = Component.HomePage({
  covers: { Timeline: "assets/sessions/080/tapniecie_mount_volkan_1.webp" },
  partyTitle: "Bohaterowie Przepowiedni",
  sectionsTitle: "Kronika Thylei",
  footerHtml:
    "Cała wiki to pliki Markdown w publicznym repozytorium " +
    '<a href="https://github.com/karpiq24/OotD">karpiq24/OotD na GitHubie</a>. ' +
    "Możesz je sklonować albo wpuścić tam swojego agenta: sesje, postacie i miejsca leżą " +
    "w katalogu <code>content/</code>.",
})

// components shared across all pages
export const sharedPageComponents: SharedLayout = {
  head: Component.Head(),
  header: [],
  afterBody: [Component.RelatedPeople(), Component.PeopleCatalog(), Component.FrontmatterTable()],
  footer: Component.Footer({
    links: {
      "Wiki na GitHubie": "https://github.com/karpiq24/OotD",
    },
  }),
}

// components for pages that display a single page (e.g. a single note)
export const defaultContentPageLayout: PageLayout = {
  beforeBody: [
    Component.ConditionalRender({
      component: Component.Breadcrumbs(),
      condition: (page) => !isHome(page),
    }),
    Component.ConditionalRender({ component: Component.ArticleTitle(), condition: notHome }),
    Component.ConditionalRender({ component: Component.ContentMeta(), condition: notHome }),
    Component.TagList(),
    Component.ConditionalRender({ component: homePage, condition: isHome }),
  ],
  left: [
    Component.PageTitle(),
    Component.MobileOnly(Component.Spacer()),
    Component.Flex({
      components: [
        {
          Component: Component.Search(),
          grow: true,
        },
        { Component: Component.Darkmode() },
        { Component: Component.ReaderMode() },
      ],
    }),
    Component.Explorer({
      filterFn: (node) => !["tags", "assets"].includes(node.slugSegment),
    }),
  ],
  // the home page uses the full width, so it has no right-hand sidebar
  right: [
    Component.ConditionalRender({ component: Component.Graph(), condition: notHome }),
    Component.ConditionalRender({
      component: Component.DesktopOnly(Component.TableOfContents()),
      condition: notHome,
    }),
    Component.ConditionalRender({ component: Component.Backlinks(), condition: notHome }),
  ],
}

// components for pages that display lists of pages  (e.g. tags or folders)
export const defaultListPageLayout: PageLayout = {
  beforeBody: [Component.Breadcrumbs(), Component.ArticleTitle(), Component.ContentMeta()],
  left: [
    Component.PageTitle(),
    Component.MobileOnly(Component.Spacer()),
    Component.Flex({
      components: [
        {
          Component: Component.Search(),
          grow: true,
        },
        { Component: Component.Darkmode() },
      ],
    }),
    Component.Explorer({
      filterFn: (node) => !["tags", "assets"].includes(node.slugSegment),
    }),
  ],
  right: [],
}

import { PageLayout, SharedLayout } from "./quartz/cfg"
import * as Component from "./quartz/components"
import { QuartzComponentProps } from "./quartz/components/types"

const isHome = (page: QuartzComponentProps) => page.fileData.slug === "index"
const notHome = (page: QuartzComponentProps) => !isHome(page)

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
    Component.ConditionalRender({ component: Component.HomePage(), condition: isHome }),
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

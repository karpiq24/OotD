import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import style from "./styles/ootd.scss"
import { folderName } from "./ootd/data"
import { href, Listing, PageCard } from "./ootd/listing"
import { hasOwnPage, isBridged, membersOf, npcFolder, peopleKey } from "./ootd/people"
import { FullSlug } from "../util/path"

// On a faction or location page: cards for the people of the NPC folder with the same
// name (Kult Węża, Mytros, Ultros…) plus everyone who lists it in `also_in`.
const RelatedPeople: QuartzComponent = ({ fileData, allFiles, ctx, cfg }: QuartzComponentProps) => {
  if (!isBridged(fileData)) return null
  const name = peopleKey(fileData)
  if (!name) return null

  // a folder like Locations/…/Mytros/ that holds its own Mytros.md leaves the people to that page
  if (hasOwnPage(allFiles, fileData)) return null

  const l: Listing = { slug: fileData.slug as FullSlug, ctx, locale: cfg.locale, allFiles }
  const { members, guests } = membersOf(l, name)
  if (members.length + guests.length === 0) return null
  const folder = npcFolder(l, name)

  return (
    <section class="ootd-related">
      <h2 class="ootd-label">Postacie</h2>
      <div class="ootd-grid ootd-grid-pages">
        {members.map((page) => (
          <PageCard l={l} page={page} />
        ))}
        {guests.map((page) => (
          <PageCard l={l} page={page} kicker={folderName(page)} />
        ))}
      </div>
      {folder && (
        <a class="ootd-more" href={href(l, folder.slug!)}>
          Folder postaci: {name} →
        </a>
      )}
    </section>
  )
}

RelatedPeople.css = style

export default (() => RelatedPeople) satisfies QuartzComponentConstructor

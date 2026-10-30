// Image-first card: the art fills the card, the title sits on a dark scrim at the bottom.
// Pages without art get a bronze monogram instead. Plain <a> (no `internal` class) so
// SPA navigation still works but hovering a card doesn't open a popover preview.
// `search` and `tags` feed the client-side filter (ootdFilter.inline.ts).
interface CardProps {
  href: string
  title: string
  image?: string
  kicker?: string
  meta?: string
  class?: string
  search?: string
  tags?: string[]
}

export function Card({
  href,
  title,
  image,
  kicker,
  meta,
  class: extraClass,
  search,
  tags,
}: CardProps) {
  return (
    <a
      href={href}
      class={["ootd-card", image ? undefined : "ootd-card-plain", extraClass]
        .filter(Boolean)
        .join(" ")}
      data-search={search}
      data-tags={tags?.join("|")}
    >
      <div class="ootd-card-media">
        {image ? (
          <img src={image} alt="" loading="lazy" decoding="async" />
        ) : (
          <span class="ootd-card-monogram" aria-hidden="true">
            {title.trim().charAt(0)}
          </span>
        )}
      </div>
      <div class="ootd-card-text">
        {kicker && <span class="ootd-card-kicker">{kicker}</span>}
        <span class="ootd-card-title">{title}</span>
        {meta && <span class="ootd-card-meta">{meta}</span>}
      </div>
    </a>
  )
}

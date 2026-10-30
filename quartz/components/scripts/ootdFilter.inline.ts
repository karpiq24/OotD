// Live filtering of card listings: any element with `data-ootd-filter` holding an
// `input.ootd-filter-input`, optional `button.ootd-chip[data-tag]` chips and
// `.ootd-card[data-search]` cards. Text must match `data-search` (folded the same way
// as fold() in components/ootd/data.ts); an active chip must be in `data-tags`.
// Sections marked `data-ootd-section` hide when none of their cards match.

function fold(text: string): string {
  return text
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/ł/g, "l")
}

// several components ship this script; register the listener only once
const w = window as Window & { __ootdFilter?: boolean }
if (!w.__ootdFilter) {
  w.__ootdFilter = true
  document.addEventListener("nav", bindFilters)
}

function bindFilters() {
  for (const root of document.querySelectorAll<HTMLElement>("[data-ootd-filter]")) {
    const input = root.querySelector<HTMLInputElement>("input.ootd-filter-input")
    const count = root.querySelector<HTMLElement>(".ootd-filter-count")
    const chips = [...root.querySelectorAll<HTMLButtonElement>("button.ootd-chip[data-tag]")]
    const cards = [...root.querySelectorAll<HTMLElement>(".ootd-card[data-search]")]
    const sections = [...root.querySelectorAll<HTMLElement>("[data-ootd-section]")]
    let activeTag: string | null = null

    const apply = () => {
      const words = fold(input?.value ?? "")
        .split(/\s+/)
        .filter(Boolean)
      let shown = 0
      for (const card of cards) {
        const search = card.dataset.search ?? ""
        const tags = (card.dataset.tags ?? "").split("|")
        const match =
          words.every((w) => search.includes(w)) && (!activeTag || tags.includes(activeTag))
        card.hidden = !match
        if (match) shown++
      }
      for (const section of sections) {
        section.hidden = !section.querySelector(".ootd-card:not([hidden])")
      }
      for (const chip of chips) {
        chip.setAttribute("aria-pressed", String(chip.dataset.tag === activeTag))
      }
      if (count) {
        count.textContent = words.length || activeTag ? `${shown} z ${cards.length}` : ""
      }
    }

    const onInput = () => apply()
    input?.addEventListener("input", onInput)
    window.addCleanup(() => input?.removeEventListener("input", onInput))

    for (const chip of chips) {
      const onClick = () => {
        activeTag = activeTag === chip.dataset.tag ? null : (chip.dataset.tag ?? null)
        apply()
      }
      chip.addEventListener("click", onClick)
      window.addCleanup(() => chip.removeEventListener("click", onClick))
    }
  }
}

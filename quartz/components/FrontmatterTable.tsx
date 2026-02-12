import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import style from "./styles/frontmatterTable.scss"
import { classNames } from "../util/lang"
import { JSX } from "preact"

interface FrontmatterTableOptions {
  /**
   * Fields to exclude from the table (e.g., 'title', 'tags')
   */
  excludeFields: string[]
  /**
   * Whether to hide the component when there are no displayable frontmatter fields
   */
  hideWhenEmpty: boolean
  /**
   * Custom title for the component
   */
  title: string
}

const defaultOptions: FrontmatterTableOptions = {
  excludeFields: ["title", "tags", "aliases", "cssclasses", "draft"],
  hideWhenEmpty: true,
  title: "Metadane",
}

// Format field names for display (convert camelCase/snake_case to Title Case)
function formatFieldName(field: string): string {
  return field
    .replace(/([A-Z])/g, " $1") // camelCase to spaces
    .replace(/[_-]/g, " ") // snake_case/kebab-case to spaces
    .replace(/^\w/, (c) => c.toUpperCase()) // capitalize first letter
    .trim()
}

// Regex to match markdown links: [text](url)
const markdownLinkRegex = /\[([^\]]+)\]\(([^)]+)\)/g

// Parse a string and convert markdown links to JSX elements
function parseMarkdownLinks(text: string): (string | JSX.Element)[] {
  const result: (string | JSX.Element)[] = []
  let lastIndex = 0
  let match

  // Reset regex state
  markdownLinkRegex.lastIndex = 0

  while ((match = markdownLinkRegex.exec(text)) !== null) {
    // Add text before the match
    if (match.index > lastIndex) {
      result.push(text.slice(lastIndex, match.index))
    }
    // Add the link as JSX
    const linkText = match[1]
    const linkUrl = match[2]
    result.push(
      <a href={linkUrl} class="internal" key={match.index}>
        {linkText}
      </a>
    )
    lastIndex = match.index + match[0].length
  }

  // Add remaining text after last match
  if (lastIndex < text.length) {
    result.push(text.slice(lastIndex))
  }

  return result.length > 0 ? result : [text]
}

// Format field values for display
function formatFieldValue(value: unknown): string | JSX.Element | (string | JSX.Element)[] | null {
  if (value === null || value === undefined) {
    return null
  }

  if (typeof value === "boolean") {
    return value ? "Yes" : "No"
  }

  if (typeof value === "number") {
    return value.toString()
  }

  if (typeof value === "string") {
    // Check if it contains markdown links
    if (markdownLinkRegex.test(value)) {
      return parseMarkdownLinks(value)
    }
    return value
  }

  if (Array.isArray(value)) {
    const formattedItems = value.map((item) => formatFieldValue(item)).filter(Boolean)
    if (formattedItems.length === 0) return null
    // For simple string arrays, join them
    if (formattedItems.every(item => typeof item === 'string')) {
      return (formattedItems as string[]).join(", ")
    }
    // For complex items, return as array
    return formattedItems.flatMap((item, i) => 
      i < formattedItems.length - 1 ? [item, ", "] : [item]
    ) as (string | JSX.Element)[]
  }

  if (typeof value === "object") {
    // For objects, try to create a reasonable string representation
    try {
      return JSON.stringify(value)
    } catch {
      return "[Object]"
    }
  }

  return String(value)
}

export default ((opts?: Partial<FrontmatterTableOptions>) => {
  const options: FrontmatterTableOptions = { ...defaultOptions, ...opts }

  const FrontmatterTable: QuartzComponent = ({
    fileData,
    displayClass,
  }: QuartzComponentProps) => {
    const frontmatter = fileData.frontmatter

    if (!frontmatter) {
      return null
    }

    // Get all frontmatter fields that should be displayed
    const displayableFields = Object.entries(frontmatter).filter(([key, value]) => {
      // Skip excluded fields
      if (options.excludeFields.includes(key)) {
        return false
      }
      // Skip empty values
      const formattedValue = formatFieldValue(value)
      if (formattedValue === null || formattedValue === "") {
        return false
      }
      return true
    })

    // Hide if no displayable fields
    if (options.hideWhenEmpty && displayableFields.length === 0) {
      return null
    }

    return (
      <div class={classNames(displayClass, "frontmatter-table")}>
        {options.title && <h3>{options.title}</h3>}
        <ul class="frontmatter-list">
          {displayableFields.map(([key, value]) => {
            const formattedValue = formatFieldValue(value)
            return (
              <li class="frontmatter-entry" key={key}>
                <span class="field-label">{formatFieldName(key)}</span>:{" "}
                <span class="field-value">{formattedValue}</span>
              </li>
            )
          })}
        </ul>
      </div>
    )
  }

  FrontmatterTable.css = style

  return FrontmatterTable
}) satisfies QuartzComponentConstructor

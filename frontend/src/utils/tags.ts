export const SUGGESTED_TAGS = [
  'JavaScript',
  'TypeScript',
  'Vue',
  'React',
  'Python',
  'FastAPI',
  'Node.js',
  'Docker',
  'DevOps',
  'AWS',
  'Linux',
  'Databases',
  'System Design',
] as const

export const MAX_TAGS_PER_POST = 5

/** Mirrors the backend's slug rule, so tag links match what the API stores. */
export function tagSlug(name: string): string {
  return name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')
}

/** Parse the comma-separated tag input, dropping blanks and case-insensitive
 *  duplicates while keeping the order the author typed. */
export function parseTags(input: string): string[] {
  const seen = new Set<string>()
  const tags: string[] = []
  for (const raw of input.split(',')) {
    const name = raw.trim()
    if (!name) continue
    const key = name.toLowerCase()
    if (seen.has(key)) continue
    seen.add(key)
    tags.push(name)
  }
  return tags
}

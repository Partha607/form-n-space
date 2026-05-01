/** Root-relative URL respecting Astro `base` (e.g. GitHub Pages project site). */
export function withBase(path: string): string {
  const clean = path.replace(/^\/+/, '');
  return `${import.meta.env.BASE_URL}${clean}`;
}

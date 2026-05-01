// @ts-check
import { defineConfig } from 'astro/config';

// GitHub Pages: project sites live under /<repo>/; user/org site repo is <user>.github.io at root.
const repo = process.env.GITHUB_REPOSITORY?.split('/')?.[1];
const onGithubActions = process.env.GITHUB_ACTIONS === 'true';
const owner = process.env.GITHUB_REPOSITORY_OWNER;
const isUserOrOrgPagesRepo = Boolean(repo?.endsWith('.github.io'));
const site =
  onGithubActions && owner ? `https://${owner}.github.io` : undefined;
const base =
  onGithubActions && repo && !isUserOrOrgPagesRepo ? `/${repo}/` : '/';

// https://astro.build/config
export default defineConfig({ site, base });

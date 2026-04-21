# HugoBlox Academic CV Migration

This directory contains a parallel HugoBlox Academic CV project for Linfeng Tang.

## Recommended setup

1. Install Hugo Extended.
2. Install Go.
3. In this directory run `hugo mod tidy`.
4. Preview locally with `hugo server`.

## Current migration scope

- English and Chinese landing pages
- Author profiles
- Full English publication pages and Chinese publication detail pages
- English and Chinese news pages
- Projects and services pages
- Custom highlight-card styling

## Notes

- The repo root `al-folio` site remains the active production site.
- This folder is an isolated migration workspace for the new HugoBlox version.
- Publication cards expect `featured.jpg` inside each publication folder.
- A GitHub Pages workflow is prepared in `.github/workflows/deploy-hugoblox.yml`.
- To avoid overriding the current Jekyll site, Hugo deployment is currently set to run on the `hugoblox` branch or by manual dispatch.

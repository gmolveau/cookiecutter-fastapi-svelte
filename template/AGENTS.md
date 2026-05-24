# Instructions for agents

- Use `just --list` to find available development targets
- Before committing `.py`, `.ts` `html` `.svelte` changes, run `just format` and `just checks`
- Don't edit `pyproject.toml` directly, use `uv` manage dependencies
- Don't edit `package.json` directly, use `pnpm` to manage dependencies

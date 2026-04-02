# MemeGenerator — Frontend

A SvelteKit application for creating memes: browse and upload templates, compose text and image layers, apply effects, and export the result as a JPG.

## Stack

| Tool                   | Role                          |
| ---------------------- | ----------------------------- |
| SvelteKit 2 + Svelte 5 | Framework and routing         |
| TypeScript (strict)    | Type safety                   |
| Tailwind CSS 4         | Utility-first styling         |
| Vite                   | Build tool                    |
| Vitest + Playwright    | Unit, component and E2E tests |
| pnpm                   | Package manager               |

## Project structure

```console
src/
├── lib/
│   ├── api/
│   │   └── templates.ts      # HTTP client for the backend API
│   ├── types/
│   │   └── index.ts          # Shared TypeScript interfaces
│   ├── stores/
│   │   └── editor.svelte.ts  # Global editor state (Svelte 5 runes)
│   └── components/
│       ├── TemplateGallery.svelte  # Browse, search and upload templates
│       ├── MemeEditor.svelte       # Main editor: canvas, toolbar, properties panel
│       ├── TextLayerEl.svelte      # Draggable / resizable text layer
│       └── ImageLayerEl.svelte     # Draggable / resizable image overlay layer
└── routes/
    ├── +layout.svelte    # Root layout — imports Tailwind CSS
    ├── layout.css        # @import 'tailwindcss'
    └── +page.svelte      # Single page: gallery view or editor view
```

## How it works

### Routing and views

The app is a **single page** (`+page.svelte`) with two views toggled by local state:

- **Gallery view** — the default. Renders `TemplateGallery`.
- **Editor view** — shown after a template is selected. Renders `MemeEditor`.

No SvelteKit page-level routing is used for the editor because there is no server-side data to load and no URL to share — the editor is entirely client-side.

### State management — `editor.svelte.ts`

All editor state lives in a single **module-level singleton** built with Svelte 5 runes:

```console
EditorState {
  template       — the selected Template from the API
  textLayers[]   — ordered list of TextLayer objects
  imageLayers[]  — ordered list of ImageLayer objects
  effect         — active image effect ('none' | 'grayscale' | 'blur' | 'sharpen' | 'sepia' | 'invert')
  selectedLayerId — id of the currently selected layer, or null
}
```

The store is created with `$state` inside a factory function that exposes only named methods (`setTemplate`, `addTextLayer`, `updateTextLayer`, ...). Raw state is never exported, so all mutations go through explicit methods. This avoids scattered `$state` declarations across components and keeps the data model in one place.

The store uses the `.svelte.ts` file extension, which enables Svelte 5 rune compilation outside of `.svelte` files.

### The editor canvas

The editing surface is **a positioned `<div>`**, not an `<canvas>` element. Layers (text boxes, image overlays) are absolutely positioned children. This makes editing straightforward: CSS handles visibility, and the browser renders text with full font support.

Each layer component (`TextLayerEl`, `ImageLayerEl`) implements **drag and resize** with the Pointer Events API (`onpointerdown` / `onpointermove` / `onpointerup`). `setPointerCapture` is used so that the pointer can be released outside the element boundary without losing the drag.

Image effects are applied as **CSS `filter`** on the background `<img>`, giving instant visual feedback with no pixel manipulation.

### Export (JPG download)

Because the editing surface is DOM-based, export cannot simply capture the screen. Instead, `downloadMeme` in `MemeEditor` **re-renders the scene onto an off-screen `<canvas>`**:

1. The template image is drawn using `ctx.drawImage` with the CSS filter re-applied as a canvas filter.
2. Image overlay layers (blob URLs, same-origin) are drawn in order.
3. Text layers are drawn with `ctx.fillText` / `ctx.strokeText`, replicating the font, colour, outline and alignment properties.
4. `canvas.toDataURL('image/jpeg', 0.92)` produces the download URL.

#### CORS and the tainted canvas

`toDataURL()` throws a `DOMException` if _any_ image drawn on the canvas was loaded from a cross-origin URL without a CORS request. Template images come from the backend (`localhost:8000`) while the frontend runs on a different port, so they are cross-origin.

Two things must be true simultaneously to avoid tainting:

- The `<img>` tag and any `new Image()` that will be drawn onto a canvas must have `crossOrigin = "anonymous"` (or `crossorigin="anonymous"`) set **before** their `src` is assigned. This makes the browser include an `Origin` header in the request.
- The backend must respond with `Access-Control-Allow-Origin`. FastAPI's `CORSMiddleware` handles this.

Both the visible preview `<img>` and the `new Image()` loaded inside `$effect` carry `crossOrigin = "anonymous"` so that they share the same browser cache entry with CORS credentials, preventing a situation where one caches the response without CORS headers first.

### API client — `templates.ts`

The backend base URL is read from the `PUBLIC_API_URL` environment variable (SvelteKit's convention for client-visible env vars), defaulting to `http://localhost:8000`.

Image URLs returned by the API are relative paths (`/static/templates/<filename>`). The client prepends the base URL so components receive fully-qualified URLs, which is what `crossOrigin` requests and `URL.createObjectURL` alternatives require.

## Environment variables

| Variable         | Default                 | Description      |
| ---------------- | ----------------------- | ---------------- |
| `PUBLIC_API_URL` | `http://localhost:8000` | Backend base URL |

Set it in a `.env` file at the root of the `frontend/` directory:

```bash
PUBLIC_API_URL=http://localhost:8000
```

## Development

```bash
pnpm install
pnpm run dev       # dev server on http://localhost:5173
pnpm run check     # TypeScript + Svelte type check
pnpm run format    # Prettier
pnpm run test:unit # Vitest (headless Chromium)
pnpm run test:e2e  # Playwright
```

The backend must be running for the template gallery and upload to work.

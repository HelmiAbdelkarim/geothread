# GeoThread Frontend

React + TypeScript frontend built with Vite and Tailwind CSS v4.

## Requirements

- Node.js 18+
- npm (comes with Node)

## Running locally

**1. Install dependencies**

```bash
npm install
```

**2. Start the dev server**

```bash
npm run dev
```

The app runs at **http://localhost:5173** with hot module replacement.

The backend must be running at `http://localhost:8000` — see the backend README for setup. CORS is pre-configured to accept requests from `localhost:5173`.

## Other commands

| Command | Description |
|---|---|
| `npm run dev` | Start dev server with HMR |
| `npm run build` | Type-check and build for production (output in `dist/`) |
| `npm run preview` | Serve the production build locally |
| `npm run lint` | Run ESLint |

## Stack

- React 19 + React Router v7
- TypeScript 6
- Tailwind CSS v4 (via `@tailwindcss/vite`)
- Heroicons

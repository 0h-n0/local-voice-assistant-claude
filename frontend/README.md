# Local Voice Assistant - Frontend

Next.js frontend for the Local Voice Assistant application.

## Prerequisites

- Node.js 18+
- npm 9+

## Getting Started

1. Install dependencies:

```bash
npm install
```

2. Start the development server:

```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm test` - Run tests
- `npm run test:watch` - Run tests in watch mode
- `npm run test:coverage` - Run tests with coverage

## Project Structure

```
frontend/
├── src/
│   ├── app/           # Next.js App Router pages
│   ├── components/    # React components
│   ├── hooks/         # Custom React hooks
│   ├── lib/           # Utility functions and API client
│   └── types/         # TypeScript type definitions
├── tests/             # Test files
└── public/            # Static assets
```

## Backend Integration

The frontend connects to the backend API at `http://localhost:8000` by default.

To configure a different API URL, set the `NEXT_PUBLIC_API_URL` environment variable:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

## Technology Stack

- Next.js 16 with App Router
- React 19
- TypeScript (strict mode)
- Tailwind CSS
- Jest + React Testing Library

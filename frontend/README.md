# Video Repurposing Frontend

## Overview
This is the frontend interface for the Video Repurposing application. It is a modern web application built with **Next.js 14**, **React**, and **Tailwind CSS**. It interacts with the backend API to allow users to generate and view repurposed video content.

## Tech Stack
- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **Components:** React Server Components & Client Components
- **Utilities:** `clsx`, `tailwind-merge`

## Project Structure
```
frontend/
├── app/                # App router pages and layouts
├── components/         # Reusable UI components
│   └── ui/             # Generic UI components (likely shadcn/ui generic)
├── lib/                # Utility functions and shared logic
├── public/             # Static assets
├── styles/             # Global styles
└── package.json        # Dependencies and scripts
```

## Getting Started

### Prerequisites
- Node.js 18 or higher
- npm (or yarn/pnpm/bun)

### Installation

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

### Configuration
If the application relies on environment variables (e.g., API base URL), check for a `.env.example` file or create a `.env.local` file.
Common variables might include:
- `NEXT_PUBLIC_API_URL`: URL of the backend API (default usually `http://localhost:8000/api/v1`)

### Running the Application

1. **Start the Development Server:**
   ```bash
   npm run dev
   ```
   Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

2. **Build for Production:**
   ```bash
   npm run build
   npm start
   ```

### Docker Support
The project includes a `Dockerfile` for containerization.
```bash
docker build -t video-repurposing-frontend .
docker run -p 3000:3000 video-repurposing-frontend
```

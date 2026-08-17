# AutoReport Frontend

Professional React frontend for the Car Registration Reports API.

## Tech Stack

- **React 18** + **TypeScript**
- **Vite** — fast dev server
- **Tailwind CSS** — styling
- **React Router** — navigation
- **Lucide React** — icons

## Pages

| Route | Description |
|-------|-------------|
| `/login` | Sign in |
| `/signup` | Create account |
| `/dashboard` | Overview & quick links |
| `/reports` | Search car registration reports |
| `/cars` | Manage user-owned cars |
| `/profile` | Update account settings |

## Setup

**1. Ensure backend is running** at `http://localhost:8000`

**2. Install & run:**

```bash
cd frontend
copy .env.example .env    # Windows
npm install
npm run dev
```

Open **http://localhost:5173**

## Environment

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_URL` | `http://localhost:8000` | FastAPI backend URL |

## Build for production

```bash
npm run build
npm run preview
```

Built files are in `dist/`.

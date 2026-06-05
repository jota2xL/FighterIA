# Documento 7: Briefing para Dev2 — Frontend FighterIA

> **Destinatario:** Agente Dev2 — Desarrollador Frontend Senior
> **Remitente:** Agente Product Owner Senior (a través del Arquitecto)
> **Proyecto:** FighterIA | **Fecha:** 2026-05-28 | **Plazo:** 6 días

---

## 1. Contexto del Proyecto

FighterIA es una plataforma web de entrenamiento de artes marciales con análisis de vídeo por IA. El usuario sube un vídeo ejecutando una técnica, el backend lo procesa con MediaPipe y devuelve: un vídeo con overlay visual (esqueleto + articulaciones coloreadas), puntuación 0-100, y feedback textual priorizado. La plataforma incluye gamificación (XP, cinturones, badges), historial, dashboard y modo instructor.

**Tu trabajo:** implementar el frontend completo. El backend ya está diseñado y sus contratos de API están en este documento. Trabaja de forma autónoma, sin preguntas.

---

## 2. Stack y Versiones Exactas

```
React: 18.3.1
TypeScript: 5.4.5
Vite: 5.3.1
Tailwind CSS: 3.4.4
React Router: 6.23.1
@tanstack/react-query: 5.40.0
Axios: 1.7.2
Zustand: 4.5.2
React Hook Form: 7.51.5
@hookform/resolvers: 3.4.2
Zod: 3.23.8
clsx: 2.1.1
tailwind-merge: 2.3.0
recharts: 2.12.7          (gráficas de progreso)
react-calendar-heatmap: 1.9.0  (heatmap de actividad)
react-hot-toast: 2.4.1    (notificaciones toast)
```

**Puerto de desarrollo:** `localhost:3000` (configurar en vite.config.ts)
**Comando de arranque:** `npm run dev`

---

## 3. Paleta de Colores y Diseño

### 3.1 Tema visual
- **Estética:** Gimnasio underground — modo oscuro permanente, agresivo y moderno
- **Tipografía:** `Inter` para texto general, `Rajdhani` para títulos y puntuaciones (importar desde Google Fonts)
- **Sin toggle de modo claro** — solo dark mode

### 3.2 Colores en `tailwind.config.ts`
```typescript
colors: {
  bg: {
    primary: "#0a0a0a",      // Fondo principal
    secondary: "#111111",    // Cards y paneles
    tertiary: "#1a1a1a",     // Inputs, elevación
    hover: "#222222",        // Hover states
  },
  brand: {
    red: "#dc2626",          // Rojo sangre — acción principal
    "red-dark": "#991b1b",   // Hover rojo
    "red-light": "#ef4444",  // Estados activos
    gold: "#d4af37",         // Dorado — elementos premium/logros
    "gold-light": "#f5d577", // Texto dorado
  },
  text: {
    primary: "#f5f5f0",      // Blanco roto — texto principal
    secondary: "#a3a3a3",    // Texto secundario
    muted: "#525252",        // Texto desactivado
  },
  border: {
    DEFAULT: "#2a2a2a",
    strong: "#3a3a3a",
  },
  score: {
    excellent: "#16a34a",    // Verde — puntuación 80-100
    good: "#ca8a04",         // Amarillo — 60-79
    poor: "#dc2626",         // Rojo — 0-59
    correct: "#22c55e",      // Articulación correcta en overlay
    incorrect: "#ef4444",    // Articulación incorrecta
  },
  belt: {
    blanco: "#f5f5f0",
    amarillo: "#fbbf24",
    naranja: "#f97316",
    verde: "#16a34a",
    azul: "#2563eb",
    marron: "#92400e",
    negro: "#1a1a1a",
  }
}
```

### 3.3 Fuentes en `index.html`
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Rajdhani:wght@500;600;700&display=swap" rel="stylesheet">
```

---

## 4. Estructura de Archivos a Crear

```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Badge.tsx          (componente genérico de badge UI)
│   │   │   ├── Spinner.tsx        (loader con mensajes motivacionales)
│   │   │   ├── ErrorMessage.tsx
│   │   │   ├── EmptyState.tsx
│   │   │   └── Modal.tsx
│   │   ├── layout/
│   │   │   ├── Navbar.tsx
│   │   │   └── Sidebar.tsx        (opcional — nav lateral en desktop)
│   │   ├── analysis/
│   │   │   ├── VideoUploader.tsx
│   │   │   ├── TechniqueSelector.tsx
│   │   │   ├── AnalysisResultCard.tsx
│   │   │   ├── ScoreDisplay.tsx
│   │   │   ├── JointResultsTable.tsx
│   │   │   ├── FeedbackList.tsx
│   │   │   └── VideoPlayer.tsx
│   │   ├── dashboard/
│   │   │   ├── StatsCard.tsx
│   │   │   ├── ProgressChart.tsx
│   │   │   ├── ActivityHeatmap.tsx
│   │   │   └── BeltProgress.tsx
│   │   ├── gamification/
│   │   │   ├── BadgeCard.tsx
│   │   │   ├── StreakCounter.tsx
│   │   │   └── XPBar.tsx
│   │   └── instructor/
│   │       ├── GroupCard.tsx
│   │       ├── StudentRow.tsx
│   │       └── CommentBox.tsx
│   ├── pages/
│   │   ├── LandingPage.tsx
│   │   ├── LoginPage.tsx
│   │   ├── RegisterPage.tsx
│   │   ├── DashboardPage.tsx
│   │   ├── NewAnalysisPage.tsx
│   │   ├── AnalysisResultPage.tsx
│   │   ├── HistoryPage.tsx
│   │   ├── ProfilePage.tsx
│   │   ├── BadgesPage.tsx
│   │   ├── InstructorPanelPage.tsx
│   │   ├── InstructorGroupPage.tsx
│   │   ├── InstructorStudentPage.tsx
│   │   └── NotFoundPage.tsx
│   ├── layouts/
│   │   ├── MainLayout.tsx
│   │   └── AuthLayout.tsx
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useAnalysis.ts
│   │   └── useGamification.ts
│   ├── services/
│   │   ├── api.client.ts
│   │   ├── auth.service.ts
│   │   ├── analysis.service.ts
│   │   ├── dashboard.service.ts
│   │   ├── gamification.service.ts
│   │   └── instructor.service.ts
│   ├── store/
│   │   └── auth.store.ts
│   ├── types/
│   │   ├── auth.types.ts
│   │   ├── analysis.types.ts
│   │   ├── dashboard.types.ts
│   │   ├── gamification.types.ts
│   │   └── instructor.types.ts
│   ├── utils/
│   │   ├── cn.ts
│   │   └── format.ts
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── public/
├── .env
├── .env.example
├── index.html
├── package.json
├── tailwind.config.ts
├── tsconfig.json
└── vite.config.ts
```

---

## 5. Archivos de Configuración Base

### 5.1 `vite.config.ts`
```typescript
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  resolve: { alias: { "@": path.resolve(__dirname, "./src") } },
  server: {
    port: 3000,
    proxy: {
      "/api": { target: "http://localhost:8000", changeOrigin: true, rewrite: (p) => p.replace(/^\/api/, "") }
    }
  }
});
```

### 5.2 `.env.example`
```
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=FighterIA
```

### 5.3 `src/utils/cn.ts`
```typescript
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

### 5.4 `src/main.tsx`
```tsx
import React from "react";
import ReactDOM from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "react-hot-toast";
import App from "./App";
import "./index.css";

const queryClient = new QueryClient({
  defaultOptions: { queries: { staleTime: 1000 * 60 * 5, retry: 1 } }
});

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
      <Toaster
        position="top-right"
        toastOptions={{
          style: { background: "#1a1a1a", color: "#f5f5f0", border: "1px solid #2a2a2a" }
        }}
      />
    </QueryClientProvider>
  </React.StrictMode>
);
```

### 5.5 `src/index.css`
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    @apply bg-bg-primary text-text-primary font-sans;
  }
  h1, h2, h3 {
    font-family: 'Rajdhani', sans-serif;
  }
}

@layer utilities {
  .score-text {
    font-family: 'Rajdhani', sans-serif;
    font-weight: 700;
  }
}
```

---

## 6. Estado Global — Zustand

### `src/store/auth.store.ts`
```typescript
import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { User } from "@/types/auth.types";

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  setTokens: (access: string, refresh: string) => void;
  setUser: (user: User) => void;
  logout: () => void;
  isAuthenticated: () => boolean;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      setTokens: (access, refresh) => set({ accessToken: access, refreshToken: refresh }),
      setUser: (user) => set({ user }),
      logout: () => set({ user: null, accessToken: null, refreshToken: null }),
      isAuthenticated: () => !!get().accessToken,
    }),
    { name: "fighterai-auth" }
  )
);
```

---

## 7. Capa de Servicios API

### `src/services/api.client.ts`
```typescript
import axios from "axios";
import { useAuthStore } from "@/store/auth.store";

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000",
  headers: { "Content-Type": "application/json" },
  timeout: 300000, // 5 minutes — needed for video processing
});

apiClient.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      const refresh = useAuthStore.getState().refreshToken;
      if (refresh) {
        try {
          const { data } = await axios.post(
            `${import.meta.env.VITE_API_BASE_URL}/auth/refresh`,
            { refresh_token: refresh }
          );
          useAuthStore.getState().setTokens(data.access_token, data.refresh_token);
          original.headers.Authorization = `Bearer ${data.access_token}`;
          return apiClient(original);
        } catch {
          useAuthStore.getState().logout();
          window.location.href = "/login";
        }
      } else {
        useAuthStore.getState().logout();
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

### `src/services/auth.service.ts`
```typescript
import apiClient from "./api.client";
import type { LoginRequest, RegisterRequest, TokenResponse, User } from "@/types/auth.types";

export const authService = {
  register: (data: RegisterRequest) =>
    apiClient.post<TokenResponse>("/auth/register", data).then(r => r.data),

  login: (data: LoginRequest) =>
    apiClient.post<TokenResponse>("/auth/login", data).then(r => r.data),

  refresh: (refreshToken: string) =>
    apiClient.post<TokenResponse>("/auth/refresh", { refresh_token: refreshToken }).then(r => r.data),

  forgotPassword: (email: string) =>
    apiClient.post("/auth/forgot-password", { email }).then(r => r.data),

  me: () =>
    apiClient.get<User>("/auth/me").then(r => r.data),

  updateProfile: (data: FormData) =>
    apiClient.put<User>("/users/me", data, { headers: { "Content-Type": "multipart/form-data" } }).then(r => r.data),
};
```

### `src/services/analysis.service.ts`
```typescript
import apiClient from "./api.client";
import type { Analysis, AnalysisList, CompareResponse } from "@/types/analysis.types";

export const analysisService = {
  create: (techniqueId: number, videoFile: File) => {
    const form = new FormData();
    form.append("technique_id", String(techniqueId));
    form.append("video", videoFile);
    return apiClient.post<Analysis>("/analysis", form, {
      headers: { "Content-Type": "multipart/form-data" }
    }).then(r => r.data);
  },

  getById: (id: number) =>
    apiClient.get<Analysis>(`/analysis/${id}`).then(r => r.data),

  getMyHistory: (page = 1, limit = 20, disciplineId?: number) =>
    apiClient.get<AnalysisList>("/analysis/me", { params: { page, limit, discipline_id: disciplineId } }).then(r => r.data),

  compare: (id1: number, id2: number) =>
    apiClient.get<CompareResponse>("/analysis/compare", { params: { id1, id2 } }).then(r => r.data),

  getOverlayUrl: (id: number) => `${import.meta.env.VITE_API_BASE_URL}/analysis/${id}/download/overlay`,
  getOriginalUrl: (id: number) => `${import.meta.env.VITE_API_BASE_URL}/analysis/${id}/download/original`,
};
```

---

## 8. Tipos TypeScript

### `src/types/auth.types.ts`
```typescript
export interface User {
  id: number;
  email: string;
  username: string;
  full_name: string;
  account_type: "alumno" | "instructor";
  bio: string | null;
  gym: string | null;
  city: string | null;
  country: string | null;
  experience_years: number;
  disciplines: string[];
  avatar_url: string | null;
  xp: number;
  belt_level: BeltLevel;
  current_streak: number;
  max_streak: number;
  streak_shields: number;
  created_at: string;
}

export type BeltLevel = "blanco" | "amarillo" | "naranja" | "verde" | "azul" | "marron" | "negro";

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface LoginRequest { email: string; password: string; }

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
  full_name: string;
  account_type: "alumno" | "instructor";
}
```

### `src/types/analysis.types.ts`
```typescript
export interface JointResult {
  joint_name: string;
  measured_angle: number;
  reference_min: number;
  reference_max: number;
  optimal_angle: number;
  is_correct: boolean;
  deviation: number;
}

export interface FeedbackItem {
  priority_order: number;
  correction_title: string;
  correction_text: string;
  biomechanical_explanation: string;
  exercise_suggestion: string;
  impact_score: number;
}

export interface Analysis {
  id: number;
  status: "pending" | "processing" | "completed" | "failed";
  technique: { id: number; display_name: string; discipline: string };
  global_score: number | null;
  power_score: number | null;
  balance_score: number | null;
  alignment_score: number | null;
  speed_score: number | null;
  xp_awarded: number;
  joint_results: JointResult[];
  feedback: FeedbackItem[];
  video_overlay_url: string;
  video_original_url: string;
  created_at: string;
  completed_at: string | null;
  error_message: string | null;
}

export interface AnalysisListItem {
  id: number;
  technique_display_name: string;
  discipline_name: string;
  global_score: number | null;
  status: string;
  video_overlay_url: string;
  created_at: string;
}

export interface AnalysisList {
  items: AnalysisListItem[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}
```

---

## 9. Rutas y Páginas

### `src/App.tsx`
```tsx
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import MainLayout from "@/layouts/MainLayout";
import AuthLayout from "@/layouts/AuthLayout";
import { useAuthStore } from "@/store/auth.store";

// Pages
import LandingPage from "@/pages/LandingPage";
import LoginPage from "@/pages/LoginPage";
import RegisterPage from "@/pages/RegisterPage";
import DashboardPage from "@/pages/DashboardPage";
import NewAnalysisPage from "@/pages/NewAnalysisPage";
import AnalysisResultPage from "@/pages/AnalysisResultPage";
import HistoryPage from "@/pages/HistoryPage";
import ProfilePage from "@/pages/ProfilePage";
import BadgesPage from "@/pages/BadgesPage";
import InstructorPanelPage from "@/pages/InstructorPanelPage";
import InstructorGroupPage from "@/pages/InstructorGroupPage";
import InstructorStudentPage from "@/pages/InstructorStudentPage";
import NotFoundPage from "@/pages/NotFoundPage";

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const isAuthenticated = useAuthStore(s => s.isAuthenticated());
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
};

const InstructorRoute = ({ children }: { children: React.ReactNode }) => {
  const user = useAuthStore(s => s.user);
  if (!user) return <Navigate to="/login" replace />;
  if (user.account_type !== "instructor") return <Navigate to="/dashboard" replace />;
  return <>{children}</>;
};

const App = () => (
  <BrowserRouter>
    <Routes>
      {/* Public routes */}
      <Route path="/" element={<LandingPage />} />
      <Route element={<AuthLayout />}>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
      </Route>

      {/* Protected routes */}
      <Route element={<ProtectedRoute><MainLayout /></ProtectedRoute>}>
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/analysis/new" element={<NewAnalysisPage />} />
        <Route path="/analysis/:id" element={<AnalysisResultPage />} />
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/badges" element={<BadgesPage />} />
      </Route>

      {/* Instructor-only routes */}
      <Route element={<ProtectedRoute><InstructorRoute><MainLayout /></InstructorRoute></ProtectedRoute>}>
        <Route path="/instructor" element={<InstructorPanelPage />} />
        <Route path="/instructor/groups/:groupId" element={<InstructorGroupPage />} />
        <Route path="/instructor/students/:studentId" element={<InstructorStudentPage />} />
      </Route>

      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  </BrowserRouter>
);

export default App;
```

---

## 10. Descripción de Páginas y Componentes Clave

### 10.1 `DashboardPage.tsx`
- Llama a `GET /dashboard/me`, `GET /dashboard/me/progress`, `GET /dashboard/me/heatmap`
- Muestra: stats en cards (total análisis, mejor score, XP, cinturón), BeltProgress, StreakCounter, ProgressChart (Recharts LineChart), ActivityHeatmap, últimos 3 análisis en cards
- Layout grid: 2 columnas en desktop, 1 columna en móvil

### 10.2 `NewAnalysisPage.tsx`
- **Paso 1:** `TechniqueSelector` — dos selectores en cascada: disciplina → técnica (usa `GET /disciplines` y `GET /disciplines/{id}/techniques`)
- **Paso 2:** `VideoUploader` — drag & drop o click para seleccionar. Valida formato (MP4/MOV/AVI) y duración (≤60s con `<video>` element) en cliente antes de enviar
- **Paso 3:** Loader con mensajes motivacionales aleatorios mientras el backend procesa. El array de mensajes incluye: "Analizando tu técnica...", "Calculando ángulos articulares...", "Comparando con referencias biomecánicas...", "Generando overlay visual...", "Calculando puntuación técnica...", "¡Casi listo! Preparando tu feedback..."
- Al recibir respuesta exitosa → redirige a `/analysis/{id}`

### 10.3 `AnalysisResultPage.tsx`
- Llama a `GET /analysis/{id}`
- Layout: VideoPlayer (vídeo overlay) | ScoreDisplay (puntuación global grande + 4 sub-scores en circles)
- JointResultsTable: tabla de articulaciones medidas con columnas: articulación, ángulo medido, rango correcto, estado (verde ✓ / rojo ✗)
- FeedbackList: lista de correcciones ordenadas por prioridad, cada una expandible
- Botones de descarga: overlay y original
- Si `analysis.xp_awarded > 0` → toast "¡+{xp} XP ganados!"

### 10.4 `ScoreDisplay.tsx`
- Puntuación global con número grande en fuente Rajdhani
- Color según puntuación: ≥80 → score-excellent, 60-79 → score-good, <60 → score-poor
- 4 sub-scores en cards pequeñas: Potencia, Equilibrio, Alineación, Velocidad

### 10.5 `BeltProgress.tsx`
- Muestra cinturón actual con color correspondiente
- Barra de progreso hacia el siguiente cinturón con el XP actual / XP requerido
- Colores de cinturón según el objeto `belt` en tailwind.config

### 10.6 `Navbar.tsx`
- Logo "FighterIA" + links de navegación
- Avatar del usuario con dropdown: Ver perfil, Badges, Cerrar sesión
- Si `user.account_type === "instructor"` → mostrar link "Panel Instructor"
- Icono de cinturón con color del nivel actual
- En móvil: hamburger menu con drawer lateral

### 10.7 `VideoUploader.tsx`
- Zona de drag & drop con estilo dark
- Validación frontend: extensiones permitidas (mp4, mov, avi), mensaje de error si duración > 60s
- Barra de progreso de carga del archivo
- Previsualización del vídeo antes de enviar con `<video>` element

### 10.8 `ProgressChart.tsx`
- Recharts `LineChart` con datos de `GET /dashboard/me/progress`
- Selector de disciplina (tabs) y período (últimos 30/60/90 días)
- Colores: brand.red para la línea, bg.secondary para fondo
- Tooltip personalizado con fondo oscuro

### 10.9 `ActivityHeatmap.tsx`
- `react-calendar-heatmap` con 90 días
- Colores: bg.hover para días sin actividad, distintas intensidades de brand.red para 1/2/3+ análisis
- Tooltip mostrando fecha y número de análisis

### 10.10 `InstructorPanelPage.tsx`
- Lista de grupos del instructor (`GET /instructor/groups`)
- Botón "Crear grupo" → modal con formulario (nombre, descripción)
- Cada GroupCard muestra: nombre, código de invitación, número de alumnos, botón para ver detalle
- Panel para alumnos: sección separada donde el alumno puede unirse a un grupo con código

### 10.11 `LoginPage.tsx` y `RegisterPage.tsx`
- `AuthLayout` centra el formulario con el logo de FighterIA encima
- React Hook Form + Zod para validación
- En Login: email + contraseña + link a recuperar contraseña (mock) + link a Register
- En Register: email + username + nombre + contraseña + confirmar contraseña + tipo de cuenta (radio buttons) + link a Login

---

## 11. Componentes UI Base

### `src/components/ui/Spinner.tsx`
```tsx
const MOTIVATIONAL_MESSAGES = [
  "Analizando tu técnica...",
  "Calculando ángulos articulares...",
  "Comparando con referencias biomecánicas...",
  "Generando overlay visual...",
  "Evaluando tu potencia...",
  "¡Casi listo! Preparando tu feedback..."
];

interface SpinnerProps {
  size?: "sm" | "md" | "lg";
  motivational?: boolean;
}

const Spinner = ({ size = "md", motivational = false }: SpinnerProps) => {
  const [msgIdx, setMsgIdx] = React.useState(0);

  React.useEffect(() => {
    if (!motivational) return;
    const interval = setInterval(() => setMsgIdx(i => (i + 1) % MOTIVATIONAL_MESSAGES.length), 2500);
    return () => clearInterval(interval);
  }, [motivational]);

  const sizeClass = { sm: "h-5 w-5", md: "h-10 w-10", lg: "h-16 w-16" }[size];

  return (
    <div className="flex flex-col items-center gap-4 py-8">
      <div className={`animate-spin rounded-full border-2 border-bg-hover border-t-brand-red ${sizeClass}`} />
      {motivational && (
        <p className="text-text-secondary text-sm text-center animate-pulse max-w-xs">
          {MOTIVATIONAL_MESSAGES[msgIdx]}
        </p>
      )}
    </div>
  );
};

export default Spinner;
```

### `src/components/ui/Button.tsx`
```tsx
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost" | "danger";
  size?: "sm" | "md" | "lg";
  isLoading?: boolean;
}

const Button = ({ variant = "primary", size = "md", isLoading, children, className, disabled, ...props }: ButtonProps) => {
  const base = "inline-flex items-center justify-center font-semibold rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-brand-red focus:ring-offset-2 focus:ring-offset-bg-primary disabled:opacity-50 disabled:cursor-not-allowed";
  const variants = {
    primary: "bg-brand-red text-white hover:bg-brand-red-dark",
    secondary: "bg-bg-tertiary text-text-primary border border-border hover:bg-bg-hover",
    ghost: "text-text-secondary hover:text-text-primary hover:bg-bg-hover",
    danger: "bg-red-900 text-white hover:bg-red-800",
  };
  const sizes = { sm: "px-3 py-1.5 text-sm", md: "px-4 py-2 text-sm", lg: "px-6 py-3 text-base" };

  return (
    <button className={cn(base, variants[variant], sizes[size], className)} disabled={disabled || isLoading} {...props}>
      {isLoading && <span className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />}
      {children}
    </button>
  );
};
```

---

## 12. `package.json`

```json
{
  "name": "fighterai-frontend",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "test": "vitest",
    "lint": "eslint src --ext ts,tsx"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.23.1",
    "@tanstack/react-query": "^5.40.0",
    "axios": "^1.7.2",
    "zustand": "^4.5.2",
    "react-hook-form": "^7.51.5",
    "@hookform/resolvers": "^3.4.2",
    "zod": "^3.23.8",
    "clsx": "^2.1.1",
    "tailwind-merge": "^2.3.0",
    "recharts": "^2.12.7",
    "react-calendar-heatmap": "^1.9.0",
    "react-hot-toast": "^2.4.1"
  },
  "devDependencies": {
    "@types/react": "^18.3.3",
    "@types/react-dom": "^18.3.0",
    "@types/react-calendar-heatmap": "^1.6.4",
    "@vitejs/plugin-react": "^4.3.0",
    "typescript": "^5.4.5",
    "vite": "^5.3.1",
    "tailwindcss": "^3.4.4",
    "autoprefixer": "^10.4.19",
    "postcss": "^8.4.38",
    "vitest": "^1.6.0",
    "@testing-library/react": "^16.0.0",
    "@testing-library/jest-dom": "^6.4.6",
    "msw": "^2.3.1",
    "eslint": "^8.57.0",
    "@typescript-eslint/eslint-plugin": "^7.13.0"
  }
}
```

---

## 13. Criterios de Calidad del Frontend

- [ ] `npm run dev` arranca en localhost:3000 sin errores TypeScript
- [ ] Un usuario puede registrarse y se le redirige al dashboard
- [ ] Un usuario puede hacer login y el token se persiste en localStorage
- [ ] El logout borra el token y redirige a /login
- [ ] El formulario de nuevo análisis valida formato y duración antes de enviar
- [ ] El loader muestra mensajes motivacionales rotatorios durante el procesamiento
- [ ] La página de resultado muestra vídeo con overlay, puntuaciones y feedback
- [ ] El dashboard muestra gráfica de progreso y heatmap
- [ ] Las rutas protegidas redirigen a /login si no hay sesión
- [ ] Las rutas de instructor redirigen a /dashboard para cuentas de tipo alumno
- [ ] El diseño es responsive: funciona en 375px (mobile) y 1280px (desktop)
- [ ] No hay `console.log` en el código entregado
- [ ] No hay uso de `any` sin justificación
- [ ] Los estados de loading, error y vacío están implementados en todas las vistas que consumen datos

✅ DOCUMENTO COMPLETADO

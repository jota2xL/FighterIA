# Arquitectura FighterIA — Entregable 7: Briefing Dev2 (Frontend)

> **Autor:** Agente Arquitecto de Software Senior
> **Destinatario:** Agente Dev2 — Desarrollador Frontend Senior
> **Fecha:** 2026-05-28 | **Plazo:** 6 días

---

## 1. Tu misión

Implementar el frontend completo de FighterIA. Tienes aquí los contratos de API exactos, los tipos TypeScript, la configuración de tema y la descripción detallada de cada página y componente. No preguntes nada al Arquitecto. Trabaja sobre los contratos definidos en `arquitectura/03_api_endpoints.md` — si el backend no está listo usa mocks con la misma estructura.

---

## 2. Stack exacto

```
React 18.3.1 + TypeScript 5.4.5
Vite 5.3.1 (puerto 3000)
Tailwind CSS 3.4.4
React Router DOM 6.23.1
@tanstack/react-query 5.40.0
Axios 1.7.2
Zustand 4.5.2
React Hook Form 7.51.5 + @hookform/resolvers 3.4.2
Zod 3.23.8
clsx 2.1.1 + tailwind-merge 2.3.0
recharts 2.12.7
react-calendar-heatmap 1.9.0
react-hot-toast 2.4.1
```

---

## 3. Tema Tailwind — `tailwind.config.ts`

```typescript
import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: {
          primary:   "#0a0a0a",
          secondary: "#111111",
          tertiary:  "#1a1a1a",
          hover:     "#222222",
        },
        brand: {
          red:        "#dc2626",
          "red-dark": "#991b1b",
          "red-light":"#ef4444",
          gold:       "#d4af37",
          "gold-light":"#f5d577",
        },
        text: {
          primary:   "#f5f5f0",
          secondary: "#a3a3a3",
          muted:     "#525252",
        },
        border: {
          DEFAULT: "#2a2a2a",
          strong:  "#3a3a3a",
        },
        score: {
          excellent: "#16a34a",
          good:      "#ca8a04",
          poor:      "#dc2626",
          correct:   "#22c55e",
          incorrect: "#ef4444",
        },
        belt: {
          blanco:  "#f5f5f0",
          amarillo:"#fbbf24",
          naranja: "#f97316",
          verde:   "#16a34a",
          azul:    "#2563eb",
          marron:  "#92400e",
          negro:   "#1a1a1a",
        },
      },
      fontFamily: {
        sans:    ["Inter", "system-ui", "sans-serif"],
        heading: ["Rajdhani", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
} satisfies Config;
```

---

## 4. Tipos TypeScript Completos

### `src/types/auth.types.ts`
```typescript
export type BeltLevel = "blanco" | "amarillo" | "naranja" | "verde" | "azul" | "marron" | "negro";
export type AccountType = "alumno" | "instructor";

export interface User {
  id: number;
  email: string;
  username: string;
  full_name: string;
  account_type: AccountType;
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
  is_active: boolean;
  created_at: string;
}

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
  account_type: AccountType;
}
```

### `src/types/analysis.types.ts`
```typescript
export interface Technique {
  id: number;
  name: string;
  display_name: string;
  discipline_name: string;
  difficulty: "easy" | "medium" | "hard";
}

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

export interface NewlyEarnedBadge {
  badge_id: number;
  display_name: string;
  xp_reward: number;
}

export interface Analysis {
  id: number;
  status: "pending" | "processing" | "completed" | "failed";
  technique: Technique | null;
  global_score: number | null;
  power_score: number | null;
  balance_score: number | null;
  alignment_score: number | null;
  speed_score: number | null;
  xp_awarded: number;
  belt_upgraded: boolean;
  new_belt: string | null;
  newly_earned_badges: NewlyEarnedBadge[];
  joint_results: JointResult[];
  feedback: FeedbackItem[];
  video_overlay_url: string | null;
  video_original_url: string | null;
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
  video_overlay_url: string | null;
  created_at: string;
}

export interface AnalysisList {
  items: AnalysisListItem[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export interface DisciplineOption {
  id: number;
  name: string;
  display_name: string;
  icon_name: string;
}

export interface TechniqueOption {
  id: number;
  discipline_id: number;
  name: string;
  display_name: string;
  difficulty: string;
  xp_multiplier: number;
}
```

### `src/types/dashboard.types.ts`
```typescript
export interface DashboardStats {
  total_analyses: number;
  best_score: number | null;
  average_score: number | null;
  favorite_discipline: string | null;
  most_analyzed_technique: string | null;
  xp: number;
  belt_level: string;
  xp_for_next_belt: number | null;
  xp_next_belt_name: string | null;
  current_streak: number;
  max_streak: number;
  streak_shields: number;
  recent_badges: RecentBadge[];
  recent_analyses: RecentAnalysis[];
}

export interface RecentBadge {
  badge_id: number;
  display_name: string;
  icon_name: string;
  level: string;
  earned_at: string;
}

export interface RecentAnalysis {
  id: number;
  technique_display_name: string;
  discipline_name: string;
  global_score: number | null;
  created_at: string;
}

export interface ProgressDataset {
  discipline: string;
  discipline_id: number;
  color: string;
  data: (number | null)[];
}

export interface ProgressData {
  labels: string[];
  datasets: ProgressDataset[];
}

export interface HeatmapEntry {
  date: string;
  count: number;
}

export interface HeatmapData {
  data: HeatmapEntry[];
}
```

### `src/types/gamification.types.ts`
```typescript
export interface Badge {
  id: number;
  name: string;
  display_name: string;
  description: string;
  level: "bronze" | "silver" | "gold";
  icon_name: string;
  xp_reward: number;
}

export interface UserBadge {
  badge_id: number;
  display_name: string;
  icon_name: string;
  level: string;
  xp_reward: number;
  earned_at: string;
}

export interface RankingItem {
  rank: number;
  user_id: number;
  username: string;
  full_name: string;
  belt_level: string;
  xp: number;
  average_score: number | null;
  avatar_url: string | null;
}

export interface RankingData {
  items: RankingItem[];
  my_rank: number | null;
  total_users: number;
}
```

### `src/types/instructor.types.ts`
```typescript
export interface Group {
  id: number;
  name: string;
  description: string | null;
  invite_code: string;
  member_count: number;
  is_active: boolean;
  created_at: string;
}

export interface GroupMember {
  student_id: number;
  username: string;
  full_name: string;
  belt_level: string;
  xp: number;
  total_analyses: number;
  last_activity_date: string | null;
  average_score: number | null;
  joined_at: string;
}

export interface GroupDetail {
  id: number;
  name: string;
  invite_code: string;
  members: GroupMember[];
}
```

---

## 5. Validación de Formularios con Zod

### Schemas de validación para React Hook Form
```typescript
// src/utils/validation.schemas.ts
import { z } from "zod";

export const loginSchema = z.object({
  email: z.string().email("Email inválido"),
  password: z.string().min(1, "La contraseña es requerida"),
});

export const registerSchema = z.object({
  email: z.string().email("Email inválido"),
  username: z
    .string()
    .min(3, "Mínimo 3 caracteres")
    .max(30, "Máximo 30 caracteres")
    .regex(/^[a-zA-Z0-9_]+$/, "Solo letras, números y guiones bajos"),
  password: z.string().min(8, "Mínimo 8 caracteres"),
  confirm_password: z.string(),
  full_name: z.string().min(2, "Mínimo 2 caracteres"),
  account_type: z.enum(["alumno", "instructor"]),
}).refine((d) => d.password === d.confirm_password, {
  message: "Las contraseñas no coinciden",
  path: ["confirm_password"],
});

export const profileSchema = z.object({
  full_name: z.string().min(2).max(100),
  bio: z.string().max(500).optional(),
  gym: z.string().max(100).optional(),
  city: z.string().max(100).optional(),
  country: z.string().max(100).optional(),
  experience_years: z.number().min(0).max(100).optional(),
});

export type LoginFormData     = z.infer<typeof loginSchema>;
export type RegisterFormData  = z.infer<typeof registerSchema>;
export type ProfileFormData   = z.infer<typeof profileSchema>;
```

---

## 6. Capa de Servicios API

### `src/services/dashboard.service.ts`
```typescript
import apiClient from "./api.client";
import type { DashboardStats, ProgressData, HeatmapData } from "@/types/dashboard.types";

export const dashboardService = {
  getStats: () =>
    apiClient.get<DashboardStats>("/dashboard/me").then(r => r.data),

  getProgress: (disciplineId?: number, days = 30) =>
    apiClient.get<ProgressData>("/dashboard/me/progress", {
      params: { discipline_id: disciplineId, days }
    }).then(r => r.data),

  getHeatmap: () =>
    apiClient.get<HeatmapData>("/dashboard/me/heatmap").then(r => r.data),
};
```

### `src/services/gamification.service.ts`
```typescript
import apiClient from "./api.client";
import type { Badge, UserBadge, RankingData } from "@/types/gamification.types";

export const gamificationService = {
  getAllBadges: () =>
    apiClient.get<Badge[]>("/gamification/badges").then(r => r.data),

  getMyBadges: () =>
    apiClient.get<UserBadge[]>("/gamification/me/badges").then(r => r.data),

  getRanking: (page = 1, limit = 50, disciplineId?: number) =>
    apiClient.get<RankingData>("/gamification/ranking", {
      params: { page, limit, discipline_id: disciplineId }
    }).then(r => r.data),

  buyShield: () =>
    apiClient.post("/gamification/me/buy-shield").then(r => r.data),

  useShield: () =>
    apiClient.post("/gamification/me/use-shield").then(r => r.data),
};
```

### `src/services/instructor.service.ts`
```typescript
import apiClient from "./api.client";
import type { Group, GroupDetail, AnalysisList } from "@/types/instructor.types";

export const instructorService = {
  createGroup: (name: string, description?: string) =>
    apiClient.post<Group>("/instructor/groups", { name, description }).then(r => r.data),

  getGroups: () =>
    apiClient.get<Group[]>("/instructor/groups").then(r => r.data),

  getGroupDetail: (groupId: number) =>
    apiClient.get<GroupDetail>(`/instructor/groups/${groupId}`).then(r => r.data),

  joinGroup: (inviteCode: string) =>
    apiClient.post("/instructor/groups/join", { invite_code: inviteCode }).then(r => r.data),

  getStudentAnalyses: (studentId: number, page = 1) =>
    apiClient.get<AnalysisList>(`/instructor/students/${studentId}/analyses`, {
      params: { page }
    }).then(r => r.data),

  getStudentStats: (studentId: number) =>
    apiClient.get(`/instructor/students/${studentId}/stats`).then(r => r.data),

  addComment: (analysisId: number, content: string) =>
    apiClient.post(`/instructor/analyses/${analysisId}/comment`, { content }).then(r => r.data),
};
```

---

## 7. Custom Hooks

### `src/hooks/useAuth.ts`
```typescript
import { useAuthStore } from "@/store/auth.store";
import { useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { authService } from "@/services/auth.service";

export function useAuth() {
  const { user, accessToken, setTokens, setUser, logout, isAuthenticated } = useAuthStore();
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    queryClient.clear();
    navigate("/login");
  };

  const isInstructor = user?.account_type === "instructor";

  return { user, accessToken, isAuthenticated: isAuthenticated(), isInstructor, logout: handleLogout };
}
```

### `src/hooks/useAnalysis.ts`
```typescript
import { useMutation, useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { analysisService } from "@/services/analysis.service";
import toast from "react-hot-toast";

export function useCreateAnalysis() {
  const navigate = useNavigate();

  return useMutation({
    mutationFn: ({ techniqueId, videoFile }: { techniqueId: number; videoFile: File }) =>
      analysisService.create(techniqueId, videoFile),
    onSuccess: (data) => {
      if (data.xp_awarded > 0) {
        toast.success(`¡+${data.xp_awarded} XP ganados!`);
      }
      if (data.belt_upgraded && data.new_belt) {
        toast.success(`🥋 ¡Has subido al cinturón ${data.new_belt}!`, { duration: 5000 });
      }
      data.newly_earned_badges.forEach(b => {
        toast.success(`🏆 Badge desbloqueado: ${b.display_name}`, { duration: 4000 });
      });
      navigate(`/analysis/${data.id}`);
    },
    onError: (error: any) => {
      const msg = error?.response?.data?.detail ?? "Error al procesar el vídeo";
      toast.error(msg);
    }
  });
}

export function useAnalysisHistory(page = 1) {
  return useQuery({
    queryKey: ["analysis", "history", page],
    queryFn: () => analysisService.getMyHistory(page),
  });
}
```

---

## 8. Descripción Detallada de Páginas

### `NewAnalysisPage.tsx` — Flujo de 3 pasos

**Paso 1 — Selector de técnica:**
```
Disciplina (tabs o dropdown): Muay Thai | BJJ | Boxeo
Al seleccionar → cargar técnicas con useQuery([disciplines, {id}/techniques])
Técnica (grid de cards con nombre, dificultad y XP multiplier)
```

**Paso 2 — Carga del vídeo:**
```
Zona drag & drop con borde punteado en brand-red
Click para abrir file picker (accept=".mp4,.mov,.avi")
Validación cliente:
  - Extensión: solo .mp4, .mov, .avi
  - Duración: crear <video> element, cargar src, leer duration en onloadedmetadata
  - Si duration > 60 → error "El vídeo no puede superar los 60 segundos"
Previsualización del vídeo con player HTML5
Botón "Analizar técnica" → activa Paso 3
```

**Paso 3 — Procesamiento:**
```
Llama a analysisService.create(techniqueId, file) con useMutation
Mientras loading=true:
  Mostrar <Spinner motivational={true} size="lg" />
  Spinner rota mensajes cada 2.5 segundos
  El botón de cancelar NO existe (procesamiento síncrono)
onSuccess → navigate a /analysis/{id}
onError → toast.error con el mensaje del backend
```

---

### `AnalysisResultPage.tsx` — Layout de resultados

```
Layout desktop: 2 columnas (60% vídeo | 40% scores)
Layout móvil: 1 columna (vídeo → scores → feedback)

COLUMNA IZQUIERDA:
  <VideoPlayer> con el vídeo overlay (src={analysis.video_overlay_url})
  Botones bajo el player:
    "Ver original" → cambia src del player
    "Descargar overlay" → <a href={overlay_url} download>
    "Descargar original" → <a href={original_url} download>

COLUMNA DERECHA:
  <ScoreDisplay> 
    Puntuación global grande (Rajdhani font, 96px)
    Color: ≥80 → score-excellent, 60-79 → score-good, <60 → score-poor
    4 sub-scores en grid 2x2: Potencia | Equilibrio / Alineación | Velocidad
    Cada sub-score: número + barra de progreso coloreada

SECCIÓN JOINTS (tabla):
  Columns: Articulación | Ángulo medido | Rango correcto | Estado
  Estado: ✓ verde si is_correct, ✗ rojo si no
  Tooltip: muestra deviation y optimal_angle al hover

SECCIÓN FEEDBACK (lista desplegable):
  Cada FeedbackItem:
    Encabezado: #N (priority_order) + correction_title + impact_score como badge
    Expandible con acordeón:
      correction_text
      biomechanical_explanation (si existe)
      exercise_suggestion como chip destacado en brand-gold
```

---

### `DashboardPage.tsx` — Layout grid

```
FILA 1 (4 stats cards):
  Total análisis | Mejor puntuación | XP actual | Racha actual

FILA 2 (2 columnas):
  IZQUIERDA (60%):
    <BeltProgress> — cinturón actual + barra XP hasta el siguiente
    <ProgressChart> — Recharts LineChart (últimos 30 días por defecto)
    Selector de disciplina: tabs All | Muay Thai | BJJ | Boxeo

  DERECHA (40%):
    <StreakCounter> — flame icon + número de racha
    <ActivityHeatmap> — 90 días (react-calendar-heatmap)
    Últimos badges desbloqueados (3 BadgeCards)

FILA 3:
  Últimos 3 análisis como AnalysisCards linkables
```

---

### `BadgesPage.tsx` — Galería de badges

```
Header: "Tus Logros" + conteo earned/total
Grid de BadgeCards (3 col desktop, 2 col tablet, 1 col mobile)

BadgeCard states:
  earned: fondo brillante con icono a color completo + earned_at date
  locked: fondo gris, icono en grayscale, description visible
  
Filtro: All | Desbloqueados | Pendientes
```

---

### `InstructorPanelPage.tsx` — Solo instructores

```
Header: "Mi Panel de Instructor"
Botón "Crear grupo" → <Modal> con form (nombre + descripción)

Grid de GroupCards:
  Cada card: nombre, código invitación (copiable al click), N alumnos
  Click → InstructorGroupPage

Sección inferior: "Unirse a un grupo como alumno"
  Input de código → POST /instructor/groups/join
```

---

## 9. Componentes Críticos — Implementación

### `ScoreDisplay.tsx`
```tsx
interface ScoreDisplayProps {
  globalScore: number;
  powerScore: number;
  balanceScore: number;
  alignmentScore: number;
  speedScore: number;
}

const getScoreColor = (score: number) => {
  if (score >= 80) return "text-score-excellent";
  if (score >= 60) return "text-score-good";
  return "text-score-poor";
};

const ScoreDisplay = ({ globalScore, powerScore, balanceScore, alignmentScore, speedScore }: ScoreDisplayProps) => (
  <div className="bg-bg-secondary rounded-xl p-6 border border-border">
    <div className="text-center mb-6">
      <p className="text-text-secondary text-sm uppercase tracking-widest mb-1">Puntuación</p>
      <span className={`font-heading font-bold text-8xl ${getScoreColor(globalScore)}`}>
        {globalScore.toFixed(1)}
      </span>
      <span className="text-text-secondary text-lg">/100</span>
    </div>
    <div className="grid grid-cols-2 gap-3">
      {[
        { label: "Potencia", value: powerScore },
        { label: "Equilibrio", value: balanceScore },
        { label: "Alineación", value: alignmentScore },
        { label: "Velocidad", value: speedScore },
      ].map(({ label, value }) => (
        <div key={label} className="bg-bg-tertiary rounded-lg p-3">
          <p className="text-text-muted text-xs uppercase mb-1">{label}</p>
          <p className={`font-heading font-bold text-2xl ${getScoreColor(value)}`}>{value.toFixed(0)}</p>
          <div className="mt-1 h-1 bg-bg-hover rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full ${value >= 80 ? "bg-score-excellent" : value >= 60 ? "bg-score-good" : "bg-score-poor"}`}
              style={{ width: `${value}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  </div>
);
```

### `BeltProgress.tsx`
```tsx
import type { BeltLevel } from "@/types/auth.types";

const BELT_XP: Record<BeltLevel, number> = {
  blanco: 0, amarillo: 501, naranja: 1501, verde: 3001,
  azul: 5001, marron: 8001, negro: 12001
};

const BELT_NEXT: Partial<Record<BeltLevel, BeltLevel>> = {
  blanco: "amarillo", amarillo: "naranja", naranja: "verde",
  verde: "azul", azul: "marron", marron: "negro"
};

const BELT_DISPLAY: Record<BeltLevel, string> = {
  blanco: "Blanco", amarillo: "Amarillo", naranja: "Naranja",
  verde: "Verde", azul: "Azul", marron: "Marrón", negro: "Negro"
};

interface BeltProgressProps { beltLevel: BeltLevel; xp: number; }

const BeltProgress = ({ beltLevel, xp }: BeltProgressProps) => {
  const nextBelt = BELT_NEXT[beltLevel];
  const currentMin = BELT_XP[beltLevel];
  const nextMin = nextBelt ? BELT_XP[nextBelt] : null;
  const progress = nextMin ? Math.round(((xp - currentMin) / (nextMin - currentMin)) * 100) : 100;

  return (
    <div className="bg-bg-secondary rounded-xl p-4 border border-border">
      <div className="flex items-center gap-3 mb-3">
        <div className={`w-8 h-3 rounded-full bg-belt-${beltLevel} border border-border`} />
        <span className="font-heading font-bold text-text-primary text-lg">
          Cinturón {BELT_DISPLAY[beltLevel]}
        </span>
        <span className="ml-auto text-text-secondary text-sm">{xp.toLocaleString()} XP</span>
      </div>
      {nextBelt && (
        <>
          <div className="h-2 bg-bg-hover rounded-full overflow-hidden">
            <div
              className="h-full bg-brand-red rounded-full transition-all duration-500"
              style={{ width: `${Math.min(progress, 100)}%` }}
            />
          </div>
          <p className="text-text-muted text-xs mt-1">
            {(nextMin! - xp).toLocaleString()} XP para cinturón {BELT_DISPLAY[nextBelt]}
          </p>
        </>
      )}
    </div>
  );
};
```

### `TechniqueSelector.tsx`
```tsx
import { useQuery } from "@tanstack/react-query";
import type { DisciplineOption, TechniqueOption } from "@/types/analysis.types";
import apiClient from "@/services/api.client";

interface TechniqueSelectorProps {
  onSelect: (technique: TechniqueOption) => void;
  selectedId: number | null;
}

const DIFFICULTY_LABELS = { easy: "Fácil", medium: "Medio", hard: "Difícil" };
const DIFFICULTY_COLORS = { easy: "text-score-excellent", medium: "text-score-good", hard: "text-score-poor" };

const TechniqueSelector = ({ onSelect, selectedId }: TechniqueSelectorProps) => {
  const [selectedDisciplineId, setSelectedDisciplineId] = React.useState<number | null>(null);

  const { data: disciplines } = useQuery({
    queryKey: ["disciplines"],
    queryFn: () => apiClient.get<DisciplineOption[]>("/disciplines").then(r => r.data),
  });

  const { data: techniques } = useQuery({
    queryKey: ["techniques", selectedDisciplineId],
    queryFn: () => apiClient.get<TechniqueOption[]>(`/disciplines/${selectedDisciplineId}/techniques`).then(r => r.data),
    enabled: !!selectedDisciplineId,
  });

  return (
    <div className="space-y-4">
      {/* Discipline tabs */}
      <div className="flex gap-2 flex-wrap">
        {disciplines?.map(d => (
          <button
            key={d.id}
            onClick={() => setSelectedDisciplineId(d.id)}
            className={cn(
              "px-4 py-2 rounded-lg text-sm font-semibold transition-colors",
              selectedDisciplineId === d.id
                ? "bg-brand-red text-white"
                : "bg-bg-tertiary text-text-secondary hover:bg-bg-hover"
            )}
          >
            {d.display_name}
          </button>
        ))}
      </div>

      {/* Techniques grid */}
      {techniques && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {techniques.map(t => (
            <button
              key={t.id}
              onClick={() => onSelect(t)}
              className={cn(
                "text-left p-4 rounded-lg border transition-all",
                selectedId === t.id
                  ? "border-brand-red bg-bg-tertiary"
                  : "border-border bg-bg-secondary hover:border-border-strong"
              )}
            >
              <p className="font-semibold text-text-primary">{t.display_name}</p>
              <div className="flex items-center gap-2 mt-1">
                <span className={`text-xs ${DIFFICULTY_COLORS[t.difficulty as keyof typeof DIFFICULTY_COLORS]}`}>
                  {DIFFICULTY_LABELS[t.difficulty as keyof typeof DIFFICULTY_LABELS]}
                </span>
                <span className="text-text-muted text-xs">×{t.xp_multiplier} XP</span>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
};
```

---

## 10. Rutas y Guards

```tsx
// src/App.tsx — estructura completa de rutas
<BrowserRouter>
  <Routes>
    {/* Públicas */}
    <Route path="/" element={<LandingPage />} />
    <Route element={<AuthLayout />}>
      <Route path="/login"    element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
    </Route>

    {/* Protegidas (cualquier usuario autenticado) */}
    <Route element={<ProtectedRoute><MainLayout /></ProtectedRoute>}>
      <Route path="/dashboard"       element={<DashboardPage />} />
      <Route path="/analysis/new"    element={<NewAnalysisPage />} />
      <Route path="/analysis/:id"    element={<AnalysisResultPage />} />
      <Route path="/history"         element={<HistoryPage />} />
      <Route path="/profile"         element={<ProfilePage />} />
      <Route path="/badges"          element={<BadgesPage />} />
    </Route>

    {/* Solo instructores */}
    <Route element={<ProtectedRoute requireInstructor><MainLayout /></ProtectedRoute>}>
      <Route path="/instructor"                    element={<InstructorPanelPage />} />
      <Route path="/instructor/groups/:groupId"   element={<InstructorGroupPage />} />
      <Route path="/instructor/students/:studentId" element={<InstructorStudentPage />} />
    </Route>

    <Route path="*" element={<NotFoundPage />} />
  </Routes>
</BrowserRouter>
```

```tsx
// ProtectedRoute con soporte instructor
interface ProtectedRouteProps {
  requireInstructor?: boolean;
  children: React.ReactNode;
}

const ProtectedRoute = ({ requireInstructor = false, children }: ProtectedRouteProps) => {
  const { isAuthenticated, isInstructor } = useAuth();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (requireInstructor && !isInstructor) return <Navigate to="/dashboard" replace />;
  return <>{children}</>;
};
```

---

## 11. Criterios de Calidad del Frontend

- [ ] `npm run dev` arranca en localhost:3000 sin errores de TypeScript
- [ ] El usuario puede completar registro → login → nuevo análisis → ver resultado
- [ ] El vídeo overlay se reproduce en el player de `AnalysisResultPage`
- [ ] El loader con mensajes motivacionales aparece durante el procesamiento
- [ ] El dashboard muestra gráfica de progreso y heatmap (aunque estén vacíos al inicio)
- [ ] Las rutas protegidas redirigen a /login si no hay sesión
- [ ] Las rutas de instructor redirigen a /dashboard para cuentas de alumno
- [ ] Los estados de loading, error y vacío están implementados en TODAS las páginas que consumen datos
- [ ] El diseño es funcional en 375px (móvil) y 1280px (escritorio)
- [ ] No hay `console.log` en el código entregado
- [ ] No hay `any` sin justificación comentada
- [ ] Los toasts aparecen tras desbloquear XP, badge o cinturón

✅ ENTREGABLE 7 COMPLETADO

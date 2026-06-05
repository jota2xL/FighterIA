/**
 * ProgressChart
 * Recharts LineChart showing score evolution with discipline and period filters.
 */
import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { useQuery } from "@tanstack/react-query";
import { dashboardService } from "@/services/dashboard.service";
import { disciplineService } from "@/services/analysis.service";
import type { Discipline } from "@/types/analysis.types";
import Spinner from "@/components/ui/Spinner";
import ErrorMessage from "@/components/ui/ErrorMessage";
import { cn } from "@/utils/cn";

const PERIODS = [
  { label: "30d", value: 30 },
  { label: "60d", value: 60 },
  { label: "90d", value: 90 },
];

const CustomTooltip = ({ active, payload, label }: {
  active?: boolean;
  payload?: { value: number }[];
  label?: string;
}) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-lg border border-border bg-bg-secondary px-3 py-2 shadow-lg">
      <p className="text-xs text-text-muted">{label}</p>
      <p className="font-display text-lg font-bold text-brand-red">
        {payload[0].value.toFixed(1)}
      </p>
    </div>
  );
};

const ProgressChart = () => {
  const [period, setPeriod] = React.useState(30);
  const [disciplineId, setDisciplineId] = React.useState<number | undefined>(undefined);

  const { data: disciplines } = useQuery<Discipline[]>({
    queryKey: ["disciplines"],
    queryFn: disciplineService.getAll,
  });

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["progress", period, disciplineId],
    queryFn: () => dashboardService.getProgress(period, disciplineId),
  });

  return (
    <div className="rounded-lg border border-border bg-bg-secondary p-4">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <h3 className="font-display text-lg font-semibold text-text-primary">
          Progreso de Puntuación
        </h3>
        <div className="flex items-center gap-2">
          {/* Discipline filter */}
          {disciplines && disciplines.length > 0 && (
            <select
              value={disciplineId ?? ""}
              onChange={(e) =>
                setDisciplineId(e.target.value ? Number(e.target.value) : undefined)
              }
              className="rounded-md border border-border bg-bg-tertiary px-2 py-1 text-xs text-text-secondary focus:outline-none focus:ring-1 focus:ring-brand-red"
            >
              <option value="">Todas</option>
              {disciplines.map((d: Discipline) => (
                <option key={d.id} value={d.id}>
                  {d.display_name}
                </option>
              ))}
            </select>
          )}
          {/* Period tabs */}
          <div className="flex rounded-md border border-border overflow-hidden">
            {PERIODS.map((p) => (
              <button
                key={p.value}
                onClick={() => setPeriod(p.value)}
                className={cn(
                  "px-3 py-1 text-xs font-medium transition-colors",
                  period === p.value
                    ? "bg-brand-red text-white"
                    : "text-text-muted hover:bg-bg-hover"
                )}
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {isLoading ? (
        <div className="flex h-48 items-center justify-center">
          <Spinner size="sm" />
        </div>
      ) : isError ? (
        <ErrorMessage message="Error cargando datos de progreso" onRetry={() => refetch()} />
      ) : !data?.data?.length ? (
        <div className="flex h-48 items-center justify-center">
          <p className="text-sm text-text-muted">Sin datos para este período</p>
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={data.data} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2a2a2a" />
            <XAxis
              dataKey="date"
              tick={{ fill: "#525252", fontSize: 11 }}
              tickLine={false}
              axisLine={{ stroke: "#2a2a2a" }}
              tickFormatter={(v: string) => v.slice(5)}
            />
            <YAxis
              domain={[0, 100]}
              tick={{ fill: "#525252", fontSize: 11 }}
              tickLine={false}
              axisLine={{ stroke: "#2a2a2a" }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Line
              type="monotone"
              dataKey="score"
              stroke="#dc2626"
              strokeWidth={2}
              dot={{ fill: "#dc2626", r: 3 }}
              activeDot={{ r: 5, fill: "#ef4444" }}
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
};

export default ProgressChart;

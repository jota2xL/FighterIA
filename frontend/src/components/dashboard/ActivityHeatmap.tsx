/**
 * ActivityHeatmap
 * 90-day activity heatmap using react-calendar-heatmap with dark theme.
 */
import { useQuery } from "@tanstack/react-query";
import CalendarHeatmap from "react-calendar-heatmap";
import "react-calendar-heatmap/dist/styles.css";
import { dashboardService } from "@/services/dashboard.service";
import Spinner from "@/components/ui/Spinner";
import ErrorMessage from "@/components/ui/ErrorMessage";

const ActivityHeatmap = () => {
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["heatmap"],
    queryFn: () => dashboardService.getHeatmap(90),
  });

  const endDate = new Date();
  const startDate = new Date();
  startDate.setDate(endDate.getDate() - 90);

  if (isLoading) return <Spinner size="sm" />;
  if (isError)
    return (
      <ErrorMessage
        message="Error cargando actividad"
        onRetry={() => refetch()}
      />
    );

  const heatmapValues =
    data?.data.map((d) => ({ date: d.date, count: d.count })) ?? [];

  return (
    <div className="rounded-lg border border-border bg-bg-secondary p-4">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="font-display text-lg font-semibold text-text-primary">
          Actividad
        </h3>
        <span className="text-xs text-text-muted">
          {data?.total_days_active ?? 0} días activos
        </span>
      </div>
      <style>{`
        .react-calendar-heatmap rect { rx: 2; }
        .react-calendar-heatmap .color-empty { fill: #222222; }
        .react-calendar-heatmap .color-scale-1 { fill: #7f1d1d; }
        .react-calendar-heatmap .color-scale-2 { fill: #991b1b; }
        .react-calendar-heatmap .color-scale-3 { fill: #dc2626; }
        .react-calendar-heatmap text { fill: #525252; font-size: 9px; }
      `}</style>
      <CalendarHeatmap
        startDate={startDate}
        endDate={endDate}
        values={heatmapValues}
        classForValue={(value) => {
          if (!value || value.count === 0) return "color-empty";
          if (value.count === 1) return "color-scale-1";
          if (value.count === 2) return "color-scale-2";
          return "color-scale-3";
        }}
        titleForValue={(value) =>
          value && value.count > 0
            ? `${value.date}: ${value.count} análisis`
            : "Sin actividad"
        }
        showMonthLabels
        gutterSize={2}
      />
    </div>
  );
};

export default ActivityHeatmap;

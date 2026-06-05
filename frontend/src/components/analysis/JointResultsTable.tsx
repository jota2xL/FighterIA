/**
 * JointResultsTable
 * Table of joint measurements with correct/incorrect status indicators.
 */
import type { JointResult } from "@/types/analysis.types";

interface JointResultsTableProps {
  joints: JointResult[];
}

const JointResultsTable = ({ joints }: JointResultsTableProps) => {
  if (joints.length === 0) return null;

  return (
    <div className="overflow-x-auto rounded-lg border border-border">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border bg-bg-tertiary">
            <th className="px-4 py-3 text-left font-semibold text-text-secondary">
              Articulación
            </th>
            <th className="px-4 py-3 text-right font-semibold text-text-secondary">
              Ángulo medido
            </th>
            <th className="px-4 py-3 text-right font-semibold text-text-secondary hidden sm:table-cell">
              Rango correcto
            </th>
            <th className="px-4 py-3 text-right font-semibold text-text-secondary hidden md:table-cell">
              Óptimo
            </th>
            <th className="px-4 py-3 text-center font-semibold text-text-secondary">
              Estado
            </th>
          </tr>
        </thead>
        <tbody>
          {joints.map((joint, idx) => (
            <tr
              key={joint.joint_name}
              className={idx % 2 === 0 ? "bg-bg-secondary" : "bg-bg-primary/50"}
            >
              <td className="px-4 py-3 font-medium text-text-primary capitalize">
                {joint.joint_name.replace(/_/g, " ")}
              </td>
              <td className="px-4 py-3 text-right font-mono text-text-primary">
                {joint.measured_angle.toFixed(1)}°
              </td>
              <td className="px-4 py-3 text-right text-text-secondary hidden sm:table-cell">
                {joint.reference_min.toFixed(0)}° – {joint.reference_max.toFixed(0)}°
              </td>
              <td className="px-4 py-3 text-right text-text-secondary hidden md:table-cell">
                {joint.optimal_angle.toFixed(1)}°
              </td>
              <td className="px-4 py-3 text-center">
                {joint.is_correct ? (
                  <span
                    className="inline-flex items-center gap-1 text-score-correct"
                    aria-label="Correcto"
                  >
                    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                    </svg>
                    <span className="hidden sm:inline text-xs font-medium">Correcto</span>
                  </span>
                ) : (
                  <span
                    className="inline-flex items-center gap-1 text-score-incorrect"
                    aria-label="Incorrecto"
                  >
                    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                    <span className="hidden sm:inline text-xs font-medium">
                      {Math.abs(joint.deviation).toFixed(1)}° desv.
                    </span>
                  </span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default JointResultsTable;

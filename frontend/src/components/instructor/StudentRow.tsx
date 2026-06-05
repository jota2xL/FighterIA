/**
 * StudentRow
 * Table row displaying a student's key stats inside a group view.
 */
import { Link } from "react-router-dom";
import type { GroupStudent } from "@/types/instructor.types";
import { getScoreColor, formatScore, getBeltLabel } from "@/utils/format";
import { formatRelativeTime } from "@/utils/format";
import { cn } from "@/utils/cn";

interface StudentRowProps {
  student: GroupStudent;
  groupId: number;
}

const StudentRow = ({ student }: StudentRowProps) => (
  <tr className="border-b border-border hover:bg-bg-hover transition-colors">
    <td className="px-4 py-3">
      <Link
        to={`/instructor/students/${student.id}`}
        className="flex items-center gap-3 hover:text-brand-red transition-colors"
      >
        {student.avatar_url ? (
          <img
            src={student.avatar_url}
            alt={student.username}
            className="h-8 w-8 rounded-full object-cover border border-border"
          />
        ) : (
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-red text-sm font-bold text-white">
            {student.username[0].toUpperCase()}
          </div>
        )}
        <div>
          <p className="text-sm font-medium text-text-primary">{student.full_name}</p>
          <p className="text-xs text-text-muted">@{student.username}</p>
        </div>
      </Link>
    </td>
    <td className="px-4 py-3 text-sm text-text-secondary">
      {getBeltLabel(student.belt_level as Parameters<typeof getBeltLabel>[0])}
    </td>
    <td className="px-4 py-3 text-right">
      <span
        className={cn("font-display text-lg font-bold", getScoreColor(student.average_score))}
      >
        {formatScore(student.average_score)}
      </span>
    </td>
    <td className="px-4 py-3 text-center text-sm text-text-secondary">
      {student.total_analyses}
    </td>
    <td className="px-4 py-3 text-right text-xs text-text-muted hidden md:table-cell">
      {student.last_analysis_at
        ? formatRelativeTime(student.last_analysis_at)
        : "Nunca"}
    </td>
    <td className="px-4 py-3 text-right">
      <span className="text-xs font-semibold text-brand-gold">
        {student.current_streak}🔥
      </span>
    </td>
  </tr>
);

export default StudentRow;

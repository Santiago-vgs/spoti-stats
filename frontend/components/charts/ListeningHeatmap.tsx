"use client";

import { HeatmapCell } from "@/lib/types";

const DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
const HOURS = Array.from({ length: 24 }, (_, i) => i);

interface Props {
  data: HeatmapCell[];
}

export default function ListeningHeatmap({ data }: Props) {
  const maxCount = Math.max(...data.map((d) => d.play_count), 1);

  // Build a lookup map
  const lookup = new Map<string, number>();
  for (const cell of data) {
    lookup.set(`${cell.day_of_week}-${cell.hour}`, cell.play_count);
  }

  function getOpacity(count: number): number {
    if (count === 0) return 0.05;
    return 0.15 + (count / maxCount) * 0.85;
  }

  return (
    <div className="overflow-x-auto">
      <div className="min-w-[600px]">
        {/* Hour labels */}
        <div className="flex items-center mb-1">
          <div className="w-10" />
          {HOURS.map((h) => (
            <div key={h} className="flex-1 text-center text-[10px] text-zinc-500">
              {h % 6 === 0 ? `${h}:00` : ""}
            </div>
          ))}
        </div>

        {/* Grid */}
        {DAYS.map((day, dayIdx) => (
          <div key={day} className="flex items-center gap-0.5 mb-0.5">
            <div className="w-10 text-xs text-zinc-400 text-right pr-2">{day}</div>
            {HOURS.map((hour) => {
              const count = lookup.get(`${dayIdx}-${hour}`) || 0;
              return (
                <div
                  key={hour}
                  className="flex-1 aspect-square rounded-sm"
                  style={{
                    backgroundColor: `rgba(34, 197, 94, ${getOpacity(count)})`,
                  }}
                  title={`${day} ${hour}:00 — ${count} plays`}
                />
              );
            })}
          </div>
        ))}

        {/* Legend */}
        <div className="flex items-center justify-end gap-1.5 mt-2">
          <span className="text-[10px] text-zinc-500">Less</span>
          {[0.05, 0.25, 0.5, 0.75, 1].map((opacity) => (
            <div
              key={opacity}
              className="w-3 h-3 rounded-sm"
              style={{ backgroundColor: `rgba(34, 197, 94, ${opacity})` }}
            />
          ))}
          <span className="text-[10px] text-zinc-500">More</span>
        </div>
      </div>
    </div>
  );
}

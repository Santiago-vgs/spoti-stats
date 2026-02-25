"use client";

const ranges = [
  { value: "short_term", label: "4 Weeks" },
  { value: "medium_term", label: "6 Months" },
  { value: "long_term", label: "All Time" },
];

interface TimeRangeSelectorProps {
  selected: string;
  onChange: (value: string) => void;
}

export default function TimeRangeSelector({ selected, onChange }: TimeRangeSelectorProps) {
  return (
    <div className="flex space-x-2" role="tablist" aria-label="Time range">
      {ranges.map((r) => (
        <button
          key={r.value}
          role="tab"
          aria-selected={selected === r.value}
          onClick={() => onChange(r.value)}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors focus-visible:ring-2 focus-visible:ring-green-500 focus-visible:ring-offset-2 focus-visible:ring-offset-zinc-950 outline-none ${
            selected === r.value
              ? "bg-green-600 text-white"
              : "bg-zinc-800 text-zinc-400 hover:text-white"
          }`}
        >
          {r.label}
        </button>
      ))}
    </div>
  );
}

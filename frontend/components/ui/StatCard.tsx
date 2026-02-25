interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
}

export default function StatCard({ title, value, subtitle }: StatCardProps) {
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 shadow-sm shadow-black/20 hover:border-zinc-700 transition-colors">
      <p className="text-sm text-zinc-400">{title}</p>
      <p className="text-2xl font-bold text-white mt-1 truncate">{value}</p>
      {subtitle && <p className="text-sm text-zinc-400 mt-1">{subtitle}</p>}
    </div>
  );
}

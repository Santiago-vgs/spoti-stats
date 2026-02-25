interface CardProps {
  children: React.ReactNode;
  className?: string;
}

export default function Card({ children, className = "" }: CardProps) {
  return (
    <div className={`bg-zinc-900 border border-zinc-800 rounded-xl p-6 shadow-sm shadow-black/20 ${className}`}>
      {children}
    </div>
  );
}

import React from 'react';

interface StatusBadgeProps {
  status: string;
  occupancyPct?: number;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, occupancyPct }) => {
  let bg = 'bg-emerald-50 text-emerald-700 border-emerald-200';
  let dot = 'bg-emerald-500';

  if (status.toLowerCase().includes('nearly') || status.toLowerCase().includes('full') || (occupancyPct && occupancyPct >= 90)) {
    bg = 'bg-rose-50 text-rose-700 border-rose-200';
    dot = 'bg-rose-500';
  } else if (status.toLowerCase().includes('busy') || (occupancyPct && occupancyPct >= 70)) {
    bg = 'bg-amber-50 text-amber-700 border-amber-200';
    dot = 'bg-amber-500';
  }

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold border ${bg}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${dot} animate-pulse`} />
      {status}
      {occupancyPct !== undefined && <span className="opacity-75">({occupancyPct}%)</span>}
    </span>
  );
};

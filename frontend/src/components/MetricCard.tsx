import React from 'react';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: any;
  trend?: {
    value?: string;
    isPositive?: boolean;
    direction?: 'up' | 'down' | 'neutral';
    label?: string;
  };
  accentColor?: 'blue' | 'teal' | 'emerald' | 'amber' | 'purple' | 'indigo' | string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  accentColor = 'blue'
}) => {
  const colorMap: Record<string, string> = {
    blue: 'bg-blue-50 text-blue-600 border-blue-100',
    teal: 'bg-teal-50 text-teal-600 border-teal-100',
    emerald: 'bg-emerald-50 text-emerald-600 border-emerald-100',
    amber: 'bg-amber-50 text-amber-600 border-amber-100',
    purple: 'bg-purple-50 text-purple-600 border-purple-100',
    indigo: 'bg-indigo-50 text-indigo-600 border-indigo-100',
  };

  const badgeStyle = trend?.isPositive ?? (trend?.direction === 'up')
    ? 'bg-emerald-50 text-emerald-700'
    : trend?.direction === 'down'
    ? 'bg-rose-50 text-rose-700'
    : 'bg-slate-100 text-slate-700';

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold tracking-wider uppercase text-slate-500">{title}</span>
        <div className={`p-2 rounded-lg border ${colorMap[accentColor] || colorMap.blue}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
      <div className="mt-3 flex items-baseline gap-2">
        <span className="text-2xl font-black tracking-tight text-slate-900">{value}</span>
        {trend && (trend.value || trend.label) && (
          <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${badgeStyle}`}>
            {trend.value || trend.label}
          </span>
        )}
      </div>
      {(subtitle || (trend && trend.label && trend.value)) && (
        <p className="mt-1 text-xs text-slate-500 flex items-center gap-1">
          {subtitle || trend?.label}
        </p>
      )}
    </div>
  );
};

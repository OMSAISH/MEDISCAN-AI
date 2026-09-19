import React from 'react';

export const CardSkeleton: React.FC = () => (
  <div className="bg-white rounded-lg border border-slate-200 p-5 animate-pulse">
    <div className="flex justify-between items-start">
      <div className="h-5 bg-slate-200 rounded w-1/3 mb-2"></div>
      <div className="h-6 bg-slate-200 rounded-full w-20"></div>
    </div>
    <div className="h-4 bg-slate-100 rounded w-2/3 mb-4"></div>
    <div className="grid grid-cols-4 gap-2 mb-4">
      <div className="h-10 bg-slate-100 rounded"></div>
      <div className="h-10 bg-slate-100 rounded"></div>
      <div className="h-10 bg-slate-100 rounded"></div>
      <div className="h-10 bg-slate-100 rounded"></div>
    </div>
    <div className="h-8 bg-slate-100 rounded w-full"></div>
  </div>
);

export const TableRowSkeleton: React.FC = () => (
  <tr className="animate-pulse">
    <td className="px-6 py-4"><div className="h-4 bg-slate-200 rounded w-32"></div></td>
    <td className="px-6 py-4"><div className="h-4 bg-slate-100 rounded w-48"></div></td>
    <td className="px-6 py-4"><div className="h-4 bg-slate-100 rounded w-16"></div></td>
    <td className="px-6 py-4"><div className="h-6 bg-slate-200 rounded-full w-20"></div></td>
    <td className="px-6 py-4"><div className="h-4 bg-slate-100 rounded w-24"></div></td>
  </tr>
);

import React from 'react';

export default function NavItem({ icon, label, active = false, onClick }) {
  return (
    <button 
      onClick={onClick} 
      className={`flex flex-col items-center justify-center gap-1 w-16 group transition-colors duration-200 ${active ? 'text-teal-600' : 'text-gray-400 hover:text-gray-600'}`}
    >
      <div className={`transition-all duration-300 ease-out ${active ? '-translate-y-1 scale-110' : 'group-hover:scale-105'}`}>
        {icon}
      </div>
      <span className={`text-[10px] transition-all duration-200 ${active ? 'font-bold opacity-100' : 'font-medium opacity-0 group-hover:opacity-100 -translate-y-2 group-hover:translate-y-0'}`}>
        {label}
      </span>
    </button>
  );
}


import React from 'react';
import { Search, History, X } from 'lucide-react';

export default function SearchTab() {
  const searchHistory = ['Panadol Extra', 'Berberin', 'Vitamin D3', 'Oresol'];

  return (
    <div className="animate-in fade-in duration-300 pt-2">
      <h2 className="text-xl font-bold text-gray-800 mb-4 px-2">Tìm kiếm</h2>
      <div className="bg-white rounded-2xl flex items-center px-4 py-3 shadow-sm border border-teal-500 mb-6">
        <Search className="text-teal-500 w-5 h-5 mr-3" />
        <input 
          autoFocus
          type="text" 
          placeholder="Nhập tên thuốc..." 
          className="bg-transparent w-full outline-none text-gray-800 placeholder-gray-400 text-sm"
        />
      </div>
      <div className="px-2">
        <h3 className="text-sm font-bold text-gray-400 uppercase mb-3">Lịch sử tìm kiếm</h3>
        <div className="space-y-3">
          {searchHistory.map((item, i) => (
            <div key={i} className="flex items-center justify-between text-gray-600 py-2 border-b border-gray-100 last:border-0 cursor-pointer hover:text-teal-600">
              <div className="flex items-center gap-3">
                <History className="w-4 h-4 text-gray-400" />
                <span className="text-sm">{item}</span>
              </div>
              <X className="w-3 h-3 text-gray-300" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}


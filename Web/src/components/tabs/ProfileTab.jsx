import React from 'react';
import { User, History, Settings, LogOut } from 'lucide-react';

export default function ProfileTab() {
  const menuItems = [
    { icon: <User className="w-5 h-5 text-gray-400" />, label: 'Hồ sơ sức khỏe' },
    { icon: <History className="w-5 h-5 text-gray-400" />, label: 'Lịch sử quét' },
    { icon: <Settings className="w-5 h-5 text-gray-400" />, label: 'Cài đặt' },
    { icon: <LogOut className="w-5 h-5" />, label: 'Đăng xuất', isDanger: true }
  ];

  return (
    <div className="animate-in fade-in duration-300 pt-2">
      <div className="flex items-center gap-4 mb-8 px-2">
        <div className="w-16 h-16 bg-teal-100 rounded-full flex items-center justify-center text-teal-600 text-2xl font-bold border-4 border-white shadow-md">
          MK
        </div>
        <div>
          <h2 className="text-xl font-bold text-gray-800">Minh Khôi</h2>
          <p className="text-xs text-gray-500 bg-gray-200 w-fit px-2 py-0.5 rounded-full mt-1">
            Thành viên Premium
          </p>
        </div>
      </div>
      
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        {menuItems.map((item, index) => (
          <div 
            key={index}
            className={`p-4 ${index < menuItems.length - 1 ? 'border-b border-gray-50' : ''} flex items-center gap-3 hover:bg-gray-50 cursor-pointer ${item.isDanger ? 'hover:bg-red-50 text-red-500' : ''}`}
          >
            {item.icon}
            <span className={`text-sm font-medium ${item.isDanger ? 'text-red-500' : 'text-gray-700'}`}>
              {item.label}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}


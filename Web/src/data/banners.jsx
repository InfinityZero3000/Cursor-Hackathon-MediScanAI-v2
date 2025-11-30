import React from 'react';
import { 
  Pill, 
  User, 
  EyeOff, 
  BrainCircuit, 
  MessageSquare, 
  Stethoscope 
} from 'lucide-react';

export const banners = [
  // Banner 1: "Đôi mắt thứ hai" (New Design)
  <div key="banner1" className="bg-gradient-to-r from-teal-400 to-cyan-400 rounded-3xl p-5 text-white shadow-md relative overflow-hidden h-full flex items-center select-none">
    <div className="z-10 w-2/3">
      <h2 className="text-lg font-bold leading-tight mb-2 drop-shadow-sm">
        Đôi mắt thứ hai<br/>cho tủ thuốc gia đình
      </h2>
      <p className="text-[10px] opacity-90 mb-3 font-medium">
        Chế độ "Không cần kính" • Tự động đọc kết quả
      </p>
      <button className="text-[10px] bg-white text-teal-600 px-4 py-1.5 rounded-full font-bold shadow-sm hover:bg-teal-50 transition transform active:scale-95">
        Tìm hiểu thêm
      </button>
    </div>
    <div className="absolute right-[-10px] bottom-[-20px] w-32 h-32 opacity-90 transform rotate-12">
      <div className="relative w-full h-full">
        <div className="absolute top-4 right-4 bg-white/20 w-20 h-20 rounded-full blur-xl"></div>
        <Pill className="w-24 h-24 text-white drop-shadow-lg transform -rotate-45" fill="white" fillOpacity="0.2" />
      </div>
    </div>
    <div className="absolute -top-10 -right-10 w-40 h-40 bg-white opacity-10 rounded-full mix-blend-overlay"></div>
  </div>,

  // Banner 2: Founder & 3 "KHÔNG" (Compact)
  <div key="banner2" className="bg-gradient-to-r from-emerald-500 to-teal-600 rounded-3xl p-4 text-white shadow-md relative overflow-hidden h-full flex flex-col justify-between select-none">
    <div className="flex justify-between items-start z-10">
      <div>
        <div className="flex items-center gap-1.5 mb-2 bg-white/20 w-fit px-2 py-0.5 rounded-full backdrop-blur-sm">
          <User className="w-2.5 h-2.5" />
          <span className="text-[9px] font-bold uppercase">Founder: Minh Tân & Tuấn Khải</span>
        </div>
        <h2 className="text-base font-bold leading-tight">
          Giải quyết 3 "KHÔNG"<br/>cho người cao tuổi
        </h2>
      </div>
    </div>
    <div className="grid grid-cols-3 gap-2 text-center mt-1 z-10">
      {[
        { icon: <EyeOff className="w-4 h-4" />, text: "Không thấy" },
        { icon: <BrainCircuit className="w-4 h-4" />, text: "Không hiểu" },
        { icon: <MessageSquare className="w-4 h-4" />, text: "Quên lời dặn" }
      ].map((item, idx) => (
        <div key={idx} className="bg-white/10 rounded-lg p-1.5 flex flex-col items-center justify-center backdrop-blur-sm border border-white/5">
          {item.icon}
          <span className="text-[9px] mt-1 opacity-90">{item.text}</span>
        </div>
      ))}
    </div>
    <div className="absolute top-0 right-0 w-32 h-32 bg-teal-300 opacity-20 rounded-full blur-2xl"></div>
  </div>,

  // Banner 3: AI Doctor
  <div key="banner3" className="bg-gradient-to-br from-teal-500 to-cyan-600 rounded-3xl p-5 text-white shadow-md relative overflow-hidden h-full flex items-center justify-between select-none">
    <div className="z-10 w-2/3">
      <div className="flex items-center gap-2 mb-2">
        <div className="p-1 bg-white/20 rounded-md">
          <BrainCircuit className="w-4 h-4" />
        </div>
        <span className="text-[10px] font-bold uppercase tracking-wider opacity-90">AI Support</span>
      </div>
      <h2 className="text-lg font-bold leading-tight mb-2">
        Bác sĩ gia đình<br/>trực tuyến 24/7
      </h2>
      <button className="text-[10px] bg-white text-teal-600 px-3 py-1.5 rounded-full font-bold shadow-sm hover:bg-teal-50 transition">
        Chat ngay
      </button>
    </div>
    <div className="w-1/3 flex justify-center relative">
      <div className="absolute inset-0 bg-teal-400 blur-2xl opacity-40 rounded-full"></div>
      <Stethoscope className="w-20 h-20 text-white/20 -rotate-12 transform translate-x-4" />
    </div>
  </div>
];


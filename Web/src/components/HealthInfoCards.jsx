import React from 'react';
import { healthInfos } from '../data/healthInfos.jsx';

export default function HealthInfoCards() {
  return (
    <div className="mb-4">
      <div className="flex justify-between items-end mb-3 px-1">
        <h3 className="text-base font-bold text-gray-800">Thông tin sức khoẻ hữu ích</h3>
        <span className="text-[11px] text-teal-600 font-semibold cursor-pointer">Xem tất cả</span>
      </div>
      
      <div className="flex overflow-x-auto gap-4 pb-4 -mx-5 px-5 scrollbar-hide snap-x">
        {healthInfos.map((info) => (
          <div key={info.id} className="min-w-[240px] bg-white p-4 rounded-2xl border border-gray-100 shadow-sm snap-center flex flex-col justify-between h-[130px]">
            <div>
              <span className={`text-[10px] font-bold px-2 py-1 rounded-md uppercase tracking-wider mb-2 inline-block ${info.tagColor}`}>
                {info.tag}
              </span>
              <h4 className="font-bold text-gray-800 text-sm leading-snug mb-1 line-clamp-2">
                {info.title}
              </h4>
              <p className="text-[11px] text-gray-500 line-clamp-1">{info.desc}</p>
            </div>
            <div className="flex justify-end">
              {info.icon}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}


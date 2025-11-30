import React from 'react';
import { banners } from '../data/banners.jsx';

export default function BannerSlider({ currentBanner }) {
  return (
    <div className="relative w-full h-44 mb-6 group rounded-3xl overflow-hidden shadow-sm">
      {banners.map((banner, index) => (
        <div
          key={index}
          className={`absolute inset-0 transition-all duration-700 ease-[cubic-bezier(0.25,0.8,0.25,1)] ${
            index === currentBanner 
              ? 'opacity-100 translate-x-0 scale-100 z-10' 
              : 'opacity-0 translate-x-4 scale-95 z-0'
          }`}
        >
          {banner}
        </div>
      ))}
      {/* Dots */}
      <div className="absolute bottom-3 left-1/2 transform -translate-x-1/2 flex gap-1.5 z-20 bg-black/10 px-2 py-1 rounded-full backdrop-blur-sm">
        {banners.map((_, index) => (
          <div
            key={index}
            className={`h-1.5 rounded-full transition-all duration-300 ${
              index === currentBanner ? 'w-4 bg-white' : 'w-1.5 bg-white/40'
            }`}
          ></div>
        ))}
      </div>
    </div>
  );
}


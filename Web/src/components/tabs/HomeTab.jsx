import React from 'react';
import { Search } from 'lucide-react';
import BannerSlider from '../BannerSlider';
import CategoryGrid from '../CategoryGrid';
import HealthInfoCards from '../HealthInfoCards';

export default function HomeTab({ currentBanner }) {
  return (
    <div className="animate-in fade-in duration-300">
      {/* Search Bar */}
      <div className="mb-5">
        <div className="bg-white rounded-2xl flex items-center px-4 py-3 shadow-sm border border-gray-100 focus-within:border-teal-400 focus-within:ring-2 focus-within:ring-teal-50 transition-all group">
          <Search className="text-gray-400 w-5 h-5 mr-3 group-focus-within:text-teal-500 transition-colors" />
          <input 
            type="text" 
            placeholder="Nhập tên thuốc, hoạt chất..." 
            className="bg-transparent w-full outline-none text-gray-700 placeholder-gray-400 text-sm font-medium"
          />
        </div>
      </div>

      {/* Slider Banner */}
      <BannerSlider currentBanner={currentBanner} />

      {/* Categories Grid */}
      <CategoryGrid />

      {/* Useful Health Info Section */}
      <HealthInfoCards />
    </div>
  );
}


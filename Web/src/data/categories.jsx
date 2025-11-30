import React from 'react';
import { 
  Pill, 
  Tablets, 
  Activity, 
  Leaf, 
  Droplet, 
  Stethoscope, 
  Wind 
} from 'lucide-react';

export const categories = [
  { id: 1, name: 'Thuốc kê đơn', icon: <Pill className="w-7 h-7 text-white" /> },
  { id: 2, name: 'Không kê đơn', icon: <Tablets className="w-7 h-7 text-white" /> },
  { id: 3, name: 'Vitamin', icon: <Activity className="w-7 h-7 text-white" /> },
  { id: 4, name: 'Thảo dược', icon: <Leaf className="w-7 h-7 text-white" /> },
  { id: 5, name: 'Thuốc bôi', icon: <Droplet className="w-7 h-7 text-white" /> },
  { id: 6, name: 'Dụng cụ y tế', icon: <Stethoscope className="w-7 h-7 text-white" /> },
  { id: 7, name: 'Tiêu hoá', icon: <Activity className="w-7 h-7 text-white" /> },
  { id: 8, name: 'Hô hấp', icon: <Wind className="w-7 h-7 text-white" /> },
];


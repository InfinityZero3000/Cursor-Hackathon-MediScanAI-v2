import React from 'react';
import { 
  ShieldCheck, 
  BookOpen, 
  Lightbulb 
} from 'lucide-react';

export const healthInfos = [
  {
    id: 1,
    tag: 'Lưu ý',
    tagColor: 'bg-orange-100 text-orange-600',
    title: 'Cách sử dụng thuốc an toàn',
    desc: 'Các nguyên tắc vàng để tránh uống nhầm thuốc...',
    icon: <ShieldCheck className="w-5 h-5 text-orange-500" />
  },
  {
    id: 2,
    tag: 'Kiến thức',
    tagColor: 'bg-teal-100 text-teal-600',
    title: 'Tác dụng phụ thường gặp',
    desc: 'Nhận biết sớm các dấu hiệu bất thường khi dùng thuốc...',
    icon: <BookOpen className="w-5 h-5 text-teal-500" />
  },
  {
    id: 3,
    tag: 'Lời khuyên',
    tagColor: 'bg-blue-100 text-blue-600',
    title: 'Lời khuyên từ dược sĩ',
    desc: 'Những điều cần tránh khi kết hợp thực phẩm chức năng...',
    icon: <Lightbulb className="w-5 h-5 text-blue-500" />
  }
];


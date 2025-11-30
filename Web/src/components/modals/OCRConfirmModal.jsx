import React, { useState } from 'react';
import { X, Check, Edit2, Search } from 'lucide-react';

export default function OCRConfirmModal({ 
  ocrText, 
  allOcrTexts, 
  onConfirm, 
  onCancel 
}) {
  const [editedText, setEditedText] = useState(ocrText || '');
  const [isEditing, setIsEditing] = useState(false);

  const handleConfirm = () => {
    onConfirm(editedText.trim() || ocrText);
  };

  const handleSelectFromList = (text) => {
    setEditedText(text);
    setIsEditing(false);
  };

  return (
    <div className="absolute inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-5 animate-in fade-in duration-300">
      <div className="bg-white w-full rounded-[32px] overflow-hidden shadow-2xl animate-in slide-in-from-bottom-12 duration-400 relative max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="bg-teal-500 px-6 pt-6 pb-4 text-white relative">
          <button 
            onClick={onCancel} 
            className="absolute top-5 right-5 text-white/70 hover:text-white bg-white/10 rounded-full p-1 transition"
          >
            <X className="w-5 h-5" />
          </button>
          <div className="flex items-center gap-2 mb-2">
            <Search className="w-6 h-6" />
            <h2 className="text-xl font-bold">Xác nhận Text OCR</h2>
          </div>
          <p className="text-teal-50 text-sm">Vui lòng kiểm tra và chỉnh sửa text đã nhận diện</p>
        </div>

        {/* Body */}
        <div className="px-5 py-6 flex-1 overflow-y-auto">
          {/* Text đã chọn */}
          <div className="mb-5">
            <label className="block text-sm font-bold text-gray-700 mb-2">
              Text đã nhận diện (để tìm kiếm):
            </label>
            {isEditing ? (
              <div className="space-y-2">
                <textarea
                  value={editedText}
                  onChange={(e) => setEditedText(e.target.value)}
                  className="w-full px-4 py-3 border-2 border-teal-500 rounded-xl text-base focus:outline-none focus:ring-2 focus:ring-teal-500 resize-none"
                  rows={3}
                  placeholder="Nhập hoặc chỉnh sửa text..."
                  autoFocus
                />
                <div className="flex gap-2">
                  <button
                    onClick={() => setIsEditing(false)}
                    className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg font-medium hover:bg-gray-300 transition"
                  >
                    Hủy
                  </button>
                  <button
                    onClick={() => setIsEditing(false)}
                    className="flex-1 px-4 py-2 bg-teal-500 text-white rounded-lg font-medium hover:bg-teal-600 transition"
                  >
                    Xong
                  </button>
                </div>
              </div>
            ) : (
              <div className="relative">
                <div className="px-4 py-3 bg-teal-50 border-2 border-teal-200 rounded-xl text-base font-medium text-gray-800 min-h-[60px] flex items-center">
                  {editedText || 'Không có text'}
                </div>
                <button
                  onClick={() => setIsEditing(true)}
                  className="absolute top-2 right-2 p-2 bg-white rounded-lg shadow-sm hover:bg-gray-50 transition"
                  title="Chỉnh sửa"
                >
                  <Edit2 className="w-4 h-4 text-teal-600" />
                </button>
              </div>
            )}
          </div>

          {/* Tất cả text OCR được */}
          {allOcrTexts && allOcrTexts.length > 0 && (
            <div>
              <label className="block text-sm font-bold text-gray-700 mb-2">
                Tất cả text đã nhận diện ({allOcrTexts.length}):
              </label>
              <div className="bg-gray-50 rounded-xl p-3 max-h-[200px] overflow-y-auto space-y-2">
                {allOcrTexts.map((text, index) => (
                  <button
                    key={index}
                    onClick={() => handleSelectFromList(text)}
                    className={`w-full text-left px-3 py-2 rounded-lg text-sm transition ${
                      text === editedText
                        ? 'bg-teal-100 border-2 border-teal-500 text-teal-800 font-medium'
                        : 'bg-white border border-gray-200 text-gray-700 hover:bg-teal-50 hover:border-teal-300'
                    }`}
                  >
                    {text}
                  </button>
                ))}
              </div>
              <p className="text-xs text-gray-500 mt-2">
                💡 Nhấn vào text bất kỳ để chọn làm text tìm kiếm
              </p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-5 pb-6 pt-4 border-t border-gray-200">
          <div className="flex gap-3">
            <button
              onClick={onCancel}
              className="flex-1 px-4 py-3 bg-gray-200 text-gray-700 rounded-xl font-bold text-sm hover:bg-gray-300 transition"
            >
              Hủy
            </button>
            <button
              onClick={handleConfirm}
              className="flex-1 px-4 py-3 bg-teal-500 text-white rounded-xl font-bold text-sm hover:bg-teal-600 transition flex items-center justify-center gap-2"
            >
              <Check className="w-5 h-5" />
              Xác nhận & Tìm kiếm
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}


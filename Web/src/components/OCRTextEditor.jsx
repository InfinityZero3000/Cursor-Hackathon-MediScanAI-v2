import React, { useState, useEffect } from 'react';
import { X, Check, Edit2, Search } from 'lucide-react';

export default function OCRTextEditor({ 
  initialText, 
  allTexts, 
  onConfirm, 
  onClose,
  onSearch 
}) {
  const [editedText, setEditedText] = useState(initialText || '');
  const [isEditing, setIsEditing] = useState(false);

  useEffect(() => {
    setEditedText(initialText || '');
  }, [initialText]);

  const handleSelectFromList = (text) => {
    setEditedText(text);
    setIsEditing(false);
  };

  const handleSearch = () => {
    if (editedText.trim()) {
      onSearch(editedText.trim());
    }
  };

  return (
    <div>
      <div className="flex items-start gap-3 mb-3">
        <div className="flex-1">
          <div className="text-xs font-bold text-teal-600 uppercase tracking-wider mb-1">
            📝 Text đã nhận diện:
          </div>
          {isEditing ? (
            <textarea
              value={editedText}
              onChange={(e) => setEditedText(e.target.value)}
              className="w-full px-3 py-2 border-2 border-teal-500 rounded-lg text-base font-bold text-gray-800 focus:outline-none focus:ring-2 focus:ring-teal-500 resize-none"
              rows={2}
              autoFocus
              placeholder="Nhập hoặc chỉnh sửa text..."
            />
          ) : (
            <div 
              onClick={() => setIsEditing(true)}
              className="px-3 py-2 bg-teal-50 border-2 border-teal-200 rounded-lg text-base font-bold text-gray-800 break-words cursor-text hover:border-teal-400 transition"
            >
              {editedText || 'Không có text'}
            </div>
          )}
          {allTexts && allTexts.length > 1 && (
            <div className="mt-2">
              <div className="text-xs font-medium text-gray-600 mb-1">
                Tất cả text đã nhận diện ({allTexts.length}):
              </div>
              <div className="flex flex-wrap gap-1 max-h-20 overflow-y-auto">
                {allTexts.map((text, index) => (
                  <button
                    key={index}
                    onClick={() => handleSelectFromList(text)}
                    className={`px-2 py-1 rounded text-xs transition ${
                      text === editedText
                        ? 'bg-teal-500 text-white font-medium'
                        : 'bg-gray-100 text-gray-700 hover:bg-teal-100'
                    }`}
                  >
                    {text}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
        <div className="flex gap-2">
          {!isEditing && (
            <button
              onClick={() => setIsEditing(true)}
              className="p-2 bg-teal-100 rounded-lg hover:bg-teal-200 transition"
              title="Chỉnh sửa"
            >
              <Edit2 className="w-4 h-4 text-teal-600" />
            </button>
          )}
          <button
            onClick={onClose}
            className="p-2 bg-gray-200 rounded-lg hover:bg-gray-300 transition"
            title="Đóng"
          >
            <X className="w-4 h-4 text-gray-600" />
          </button>
        </div>
      </div>
      
      {isEditing && (
        <div className="flex gap-2 mb-3">
          <button
            onClick={() => setIsEditing(false)}
            className="flex-1 px-3 py-2 bg-gray-200 text-gray-700 rounded-lg font-medium text-sm hover:bg-gray-300 transition"
          >
            Hủy
          </button>
          <button
            onClick={() => setIsEditing(false)}
            className="flex-1 px-3 py-2 bg-teal-500 text-white rounded-lg font-medium text-sm hover:bg-teal-600 transition"
          >
            Xong
          </button>
        </div>
      )}
      
      <div className="flex gap-2">
        <button
          onClick={handleSearch}
          disabled={!editedText.trim()}
          className="flex-1 px-4 py-2 bg-teal-500 text-white rounded-lg font-bold text-sm hover:bg-teal-600 transition flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Check className="w-4 h-4" />
          Xác nhận & Tìm kiếm
        </button>
        <button
          onClick={() => {
            setIsEditing(false);
            setEditedText(initialText || '');
            onClose();
          }}
          className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg font-medium text-sm hover:bg-gray-300 transition"
        >
          Scan lại
        </button>
      </div>
    </div>
  );
}


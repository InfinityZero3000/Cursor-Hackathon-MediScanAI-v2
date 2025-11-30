import React, { useState, useEffect, useRef } from 'react';
import { X, Zap, ScanLine, Camera, Loader2, Check, Edit2 } from 'lucide-react';
import { getApiEndpoint } from '../utils/api';
import OCRTextEditor from './OCRTextEditor';

export default function ScanOverlay({ onClose, onComplete, onScanResult }) {
  const [progress, setProgress] = useState(0);
  const [isScanning, setIsScanning] = useState(false);
  const [error, setError] = useState(null);
  const [cameraReady, setCameraReady] = useState(false);
  const [ocrResult, setOcrResult] = useState(null); // Lưu kết quả OCR
  const [showOCRText, setShowOCRText] = useState(false); // Hiển thị text OCR
  const videoRef = useRef(null);
  const streamRef = useRef(null);

  // Khởi tạo camera
  useEffect(() => {
    startCamera();
    return () => {
      stopCamera();
    };
  }, []);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: 'environment', // Camera sau (mobile)
          width: { ideal: 1280 },
          height: { ideal: 720 }
        }
      });
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        streamRef.current = stream;
        setCameraReady(true);
      }
    } catch (err) {
      console.error('Error accessing camera:', err);
      setError('Không thể truy cập camera. Vui lòng cấp quyền truy cập.');
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
  };

  const captureAndScan = async () => {
    if (!videoRef.current || isScanning) return;

    setIsScanning(true);
    setProgress(0);
    setError(null);

    try {
      // Chụp ảnh từ video
      const canvas = document.createElement('canvas');
      canvas.width = videoRef.current.videoWidth;
      canvas.height = videoRef.current.videoHeight;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(videoRef.current, 0, 0);
      
      // Convert sang base64
      const imageData = canvas.toDataURL('image/jpeg', 0.8);

      // Simulate progress
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 100);

      // Gửi ảnh đến backend
      const response = await fetch(getApiEndpoint('scan'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          image: imageData
        })
      });

      clearInterval(progressInterval);
      setProgress(100);

      const result = await response.json();

      // Luôn truyền kết quả lên component cha (bao gồm OCR data)
      if (onScanResult) {
        onScanResult(result);
      }

      // Hiển thị text OCR ngay trên camera
      if (result.extracted_text || result.all_ocr_texts) {
        setOcrResult({
          extracted_text: result.extracted_text || '',
          all_ocr_texts: result.all_ocr_texts || []
        });
        setShowOCRText(true);
        setIsScanning(false);
        setProgress(0);
      } else if (result.error === 'PRESCRIPTION_REQUIRED') {
        // Thuốc kê đơn - hiển thị kết quả ngay
        setTimeout(() => {
          onComplete();
        }, 500);
      } else {
        // Lỗi không có OCR
        setError(result.message || 'Không thể nhận diện text từ ảnh');
        setIsScanning(false);
        setProgress(0);
      }
    } catch (err) {
      console.error('Error scanning:', err);
      setError('Lỗi khi quét. Vui lòng thử lại.');
      setIsScanning(false);
      setProgress(0);
    }
  };

  const handleClose = () => {
    stopCamera();
    onClose();
  };

  return (
    <div className="absolute inset-0 z-50 bg-black flex flex-col items-center justify-between py-6 animate-in fade-in duration-200">
      <div className="flex justify-between w-full px-6 pt-4 z-10">
        <button 
          onClick={handleClose} 
          className="p-2 rounded-full bg-white/20 text-white hover:bg-white/30 transition"
        >
          <X className="w-6 h-6" />
        </button>
        <button 
          onClick={() => startCamera()} 
          className="p-2 rounded-full bg-white/20 text-white hover:bg-white/30 transition"
        >
          <Zap className="w-6 h-6 fill-current" />
        </button>
      </div>

      {/* Camera View */}
      <div className="relative w-full flex-1 flex items-center justify-center">
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          className="w-full h-full object-cover"
          style={{ display: cameraReady ? 'block' : 'none' }}
        />
        
        {/* Scan Frame Overlay */}
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="relative w-72 h-72">
            {/* Frame border */}
            <div className="absolute inset-0 border-4 border-teal-500/50 rounded-2xl"></div>
            
            {/* Corner indicators */}
            <div className="absolute top-0 left-0 w-8 h-8 border-t-4 border-l-4 border-teal-400 rounded-tl-2xl"></div>
            <div className="absolute top-0 right-0 w-8 h-8 border-t-4 border-r-4 border-teal-400 rounded-tr-2xl"></div>
            <div className="absolute bottom-0 left-0 w-8 h-8 border-b-4 border-l-4 border-teal-400 rounded-bl-2xl"></div>
            <div className="absolute bottom-0 right-0 w-8 h-8 border-b-4 border-r-4 border-teal-400 rounded-br-2xl"></div>

            {/* Progress indicator */}
            {isScanning && (
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="relative">
                  <svg className="w-32 h-32 -rotate-90" viewBox="0 0 100 100">
                    <circle 
                      className="text-teal-500/20 stroke-current" 
                      strokeWidth="4" 
                      fill="none" 
                      cx="50" 
                      cy="50" 
                      r="48" 
                    />
                    <circle 
                      className="text-teal-400 transition-[stroke-dashoffset] duration-100 ease-linear stroke-current" 
                      strokeWidth="4" 
                      strokeLinecap="round" 
                      fill="none" 
                      cx="50" 
                      cy="50" 
                      r="48" 
                      strokeDasharray="301.59" 
                      strokeDashoffset={301.59 - (progress / 100) * 301.59} 
                    />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center">
                    {isScanning ? (
                      <Loader2 className="w-8 h-8 text-teal-400 animate-spin" />
                    ) : (
                      <ScanLine className="w-8 h-8 text-teal-300" />
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Scanning line animation */}
            {!isScanning && (
              <div className="absolute w-full h-1 bg-teal-400/80 shadow-[0_0_10px_rgba(45,212,191,0.8)] animate-[scan-line_1.5s_ease-in-out_infinite]"></div>
            )}
          </div>
        </div>

        {/* OCR Result - Hiển thị text đã nhận diện ngay trên camera */}
        {showOCRText && ocrResult && (
          <div className="absolute top-20 left-0 right-0 px-6 z-20 animate-in slide-in-from-top-4 duration-300">
            <div className="bg-white/95 backdrop-blur-sm rounded-2xl p-4 shadow-2xl border-2 border-teal-400">
              <OCRTextEditor 
                initialText={ocrResult.extracted_text}
                allTexts={ocrResult.all_ocr_texts}
                onConfirm={(editedText) => {
                  // Cập nhật text đã chỉnh sửa
                  setOcrResult({ ...ocrResult, extracted_text: editedText });
                }}
                onClose={() => {
                  setShowOCRText(false);
                  setOcrResult(null);
                }}
                onSearch={async (searchText) => {
                  // Tìm kiếm với text đã chỉnh sửa
                  try {
                    const response = await fetch(getApiEndpoint('scan'), {
                      method: 'POST',
                      headers: {
                        'Content-Type': 'application/json',
                      },
                      body: JSON.stringify({
                        text: searchText
                      })
                    });
                    
                    const result = await response.json();
                    
                    if (onScanResult) {
                      onScanResult({
                        ...result,
                        extracted_text: searchText,
                        all_ocr_texts: ocrResult.all_ocr_texts
                      });
                    }
                    
                    setTimeout(() => {
                      onComplete();
                    }, 300);
                  } catch (err) {
                    console.error('Error searching:', err);
                    setError('Lỗi khi tìm kiếm thuốc');
                  }
                }}
              />
            </div>
          </div>
        )}

        {/* Error message */}
        {error && !showOCRText && (
          <div className="absolute bottom-20 left-0 right-0 px-6">
            <div className="bg-red-500/90 text-white px-4 py-2 rounded-lg text-sm text-center">
              {error}
            </div>
          </div>
        )}

        {/* Loading camera message */}
        {!cameraReady && !error && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-white text-center">
              <Loader2 className="w-12 h-12 animate-spin mx-auto mb-4" />
              <p className="text-lg">Đang khởi động camera...</p>
            </div>
          </div>
        )}
      </div>

      {/* Bottom controls */}
      <div className="flex flex-col items-center w-full px-6 pb-6 z-10">
        <span className="text-white text-base font-medium mb-4">
          {isScanning 
            ? `Đang quét AI... ${progress}%` 
            : showOCRText 
              ? 'Kiểm tra text đã nhận diện ở trên' 
              : 'Đặt thuốc trong khung và chụp'}
        </span>
        {!showOCRText && (
          <div className="flex justify-center w-full items-center">
            <button
              onClick={captureAndScan}
              disabled={!cameraReady || isScanning}
              className="w-18 h-18 p-1 bg-transparent rounded-full border-4 border-white flex items-center justify-center shadow-lg transform active:scale-95 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <div className="w-14 h-14 bg-white rounded-full flex items-center justify-center">
                {isScanning ? (
                  <Loader2 className="w-6 h-6 text-teal-500 animate-spin" />
                ) : (
                  <Camera className="w-6 h-6 text-teal-500" />
                )}
              </div>
            </button>
          </div>
        )}
      </div>
    </div>
  );
}


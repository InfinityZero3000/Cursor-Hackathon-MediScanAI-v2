import React, { useState, useRef, useEffect } from 'react';
import { 
  X, 
  CheckCircle2, 
  Activity, 
  Clock, 
  Volume2, 
  ShieldCheck,
  AlertCircle,
  Play,
  Pause,
  RotateCcw,
  Sparkles
} from 'lucide-react';

export default function ScanResultModal({ onClose, result }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [audioProgress, setAudioProgress] = useState(0);
  const audioRef = useRef(null);

  // Khởi tạo audio khi có audioUrl
  useEffect(() => {
    if (result?.audio?.url && audioRef.current) {
      const audio = audioRef.current;
      
      const handlePlay = () => setIsPlaying(true);
      const handlePause = () => setIsPlaying(false);
      const handleEnded = () => {
        setIsPlaying(false);
        setAudioProgress(0);
      };
      const handleTimeUpdate = () => {
        if (audio.duration) {
          setAudioProgress((audio.currentTime / audio.duration) * 100);
        }
      };

      audio.addEventListener('play', handlePlay);
      audio.addEventListener('pause', handlePause);
      audio.addEventListener('ended', handleEnded);
      audio.addEventListener('timeupdate', handleTimeUpdate);

      return () => {
        audio.removeEventListener('play', handlePlay);
        audio.removeEventListener('pause', handlePause);
        audio.removeEventListener('ended', handleEnded);
        audio.removeEventListener('timeupdate', handleTimeUpdate);
      };
    }
  }, [result?.audio?.url]);

  const toggleAudio = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
    }
  };

  const replayAudio = () => {
    if (audioRef.current) {
      audioRef.current.currentTime = 0;
      audioRef.current.play();
    }
  };

  const speakText = (text) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'vi-VN';
      window.speechSynthesis.speak(utterance);
    }
  };

  if (!result) {
    return (
      <div className="absolute inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-5 animate-in fade-in duration-300">
        <div className="bg-white w-full rounded-[32px] overflow-hidden shadow-2xl animate-in slide-in-from-bottom-12 duration-400 relative">
          <div className="px-6 pt-6 pb-10 text-center">
            <AlertCircle className="w-16 h-16 text-yellow-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold mb-2">Không tìm thấy</h2>
            <p className="text-gray-600 mb-6">Không thể nhận diện thuốc từ ảnh</p>
            <button 
              onClick={onClose}
              className="w-full py-4 bg-gray-900 text-white rounded-2xl font-bold text-sm hover:bg-black transition"
            >
              Đóng
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Xử lý cả format cũ và mới
  const drugInfo = result.drug_info || result;
  const drugName = drugInfo.name || drugInfo.drug_name || 'Không xác định';
  const activeIngredient = drugInfo.active_ingredient || 'Chưa có thông tin';
  const pageNumber = drugInfo.page_number || drugInfo.page_number || '';
  const rxStatus = drugInfo.is_prescription ? 'RX' : 'OTC';
  const category = drugInfo.category || '';
  
  // Thông tin tóm tắt từ Gemini AI
  const summary = result.summary;
  const hasAudio = result.audio && result.audio.url;

  return (
    <div className="absolute inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-5 animate-in fade-in duration-300">
      <div className="bg-white w-full rounded-[32px] overflow-hidden shadow-2xl animate-in slide-in-from-bottom-12 duration-400 relative">
        {/* Result Header */}
        <div className="bg-emerald-500 px-6 pt-6 pb-10 text-white relative">
          <button 
            onClick={onClose} 
            className="absolute top-5 right-5 text-white/70 hover:text-white bg-white/10 rounded-full p-1 transition"
          >
            <X className="w-5 h-5" />
          </button>
          <div className="flex flex-col gap-1">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-7 h-7 rounded-full border-2 border-white/90 flex items-center justify-center">
                <CheckCircle2 className="w-4 h-4 text-white" />
              </div>
              <span className="bg-emerald-600/50 border border-white/20 px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wide">
                {rxStatus === 'OTC' ? 'AN TOÀN (OTC)' : 'CẦN ĐƠN (RX)'}
              </span>
            </div>
            <h2 className="text-2xl font-bold tracking-tight">{drugName}</h2>
            <div className="flex items-center gap-1.5 text-emerald-50 text-xs">
              <Activity className="w-3.5 h-3.5" />
              <span className="font-medium">{activeIngredient}</span>
            </div>
          </div>
        </div>

        {/* Result Body */}
        <div className="px-5 py-6 -mt-6 bg-white rounded-t-[28px] relative z-10">
          {pageNumber && (
            <div className="flex items-center gap-2 bg-cyan-50 border border-cyan-100 p-3 rounded-xl mb-5 shadow-sm">
              <ShieldCheck className="w-5 h-5 text-cyan-600 flex-shrink-0" />
              <span className="text-[11px] font-medium text-cyan-800 leading-tight">
                Đã đối chiếu: Dược thư QG 2018 - Trang {pageNumber}
              </span>
            </div>
          )}

          <div className="flex justify-between items-center mb-6 px-1">
            <div className="flex items-center gap-1.5 text-gray-400">
              <Clock className="w-3.5 h-3.5" />
              <span className="text-xs font-medium">Vừa xong</span>
            </div>
            {!hasAudio && (
              <button 
                onClick={() => speakText(`${drugName}. ${activeIngredient}`)}
                className="flex items-center gap-1.5 text-teal-600 bg-teal-50 px-3 py-1.5 rounded-full font-bold text-xs hover:bg-teal-100 transition"
              >
                <Volume2 className="w-3.5 h-3.5" />
                Đọc to
              </button>
            )}
          </div>

          {/* AI Summary Section */}
          {summary && (
            <div className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-2xl p-4 mb-5 border border-purple-100">
              <div className="flex items-center gap-2 mb-3">
                <Sparkles className="w-4 h-4 text-purple-600" />
                <span className="text-[10px] font-bold text-purple-600 uppercase tracking-wider">
                  TÓM TẮT TỪ GEMINI AI ({summary.word_count || 0} từ)
                </span>
              </div>
              <p className="text-sm text-gray-700 leading-relaxed mb-4">
                {summary.text}
              </p>

              {/* Audio Player */}
              {hasAudio && (
                <div className="bg-white rounded-xl p-3 border border-purple-200">
                  <audio 
                    ref={audioRef} 
                    src={`http://localhost:5000${result.audio.url}`}
                    preload="auto"
                  />
                  
                  {/* Progress Bar */}
                  <div className="mb-3">
                    <div className="w-full h-1.5 bg-gray-200 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-gradient-to-r from-purple-500 to-blue-500 transition-all duration-200"
                        style={{ width: `${audioProgress}%` }}
                      />
                    </div>
                  </div>

                  {/* Controls */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <button
                        onClick={toggleAudio}
                        className="flex items-center gap-1.5 bg-gradient-to-r from-purple-600 to-blue-600 text-white px-4 py-2 rounded-lg font-bold text-xs hover:from-purple-700 hover:to-blue-700 transition"
                      >
                        {isPlaying ? (
                          <>
                            <Pause className="w-3.5 h-3.5" />
                            Tạm dừng
                          </>
                        ) : (
                          <>
                            <Play className="w-3.5 h-3.5" />
                            Nghe
                          </>
                        )}
                      </button>
                      
                      <button
                        onClick={replayAudio}
                        className="flex items-center gap-1 text-gray-600 bg-gray-100 px-3 py-2 rounded-lg font-bold text-xs hover:bg-gray-200 transition"
                      >
                        <RotateCcw className="w-3.5 h-3.5" />
                        Lại
                      </button>
                    </div>

                    <div className="text-[10px] text-gray-500 font-medium">
                      ~{result.audio.duration || 0}s
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          <div className="space-y-4 mb-6">
            <div className="bg-gray-50 rounded-2xl p-4 border border-gray-100">
              <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider block mb-1">
                HOẠT CHẤT
              </span>
              <p className="text-sm font-bold text-gray-800">{activeIngredient}</p>
            </div>

            {category && (
              <div className="bg-emerald-50/60 rounded-2xl p-4 border border-emerald-100">
                <span className="text-[10px] font-bold text-emerald-600 uppercase tracking-wider block mb-1">
                  DANH MỤC
                </span>
                <p className="text-sm text-gray-700 font-medium">{category}</p>
              </div>
            )}
            
            {result.extracted_text && (
              <div className="bg-blue-50/60 rounded-2xl p-4 border border-blue-100">
                <span className="text-[10px] font-bold text-blue-500 uppercase tracking-wider block mb-1">
                  TEXT NHẬN DIỆN ĐƯỢC
                </span>
                <p className="text-sm text-gray-700 leading-relaxed font-medium">
                  {result.extracted_text}
                </p>
              </div>
            )}
          </div>

          <button 
            onClick={onClose}
            className="w-full py-4 bg-gray-900 text-white rounded-2xl font-bold text-sm hover:bg-black transition shadow-lg shadow-gray-300 transform active:scale-[0.98]"
          >
            Đã hiểu
          </button>
        </div>
      </div>
    </div>
  );
}


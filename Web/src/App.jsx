import React, { useState } from "react";
import { Home, Search, Heart, User, ScanLine } from "lucide-react";

import Header from "./components/Header";
import NavItem from "./components/NavItem";
import ScanOverlay from "./components/ScanOverlay";
import ScanResultModal from "./components/modals/ScanResultModal";
import OCRConfirmModal from "./components/modals/OCRConfirmModal";
import HomeTab from "./components/tabs/HomeTab";
import SearchTab from "./components/tabs/SearchTab";
import FavoritesTab from "./components/tabs/FavoritesTab";
import ProfileTab from "./components/tabs/ProfileTab";
import { useBannerAutoScroll } from "./hooks/useBannerAutoScroll";
import { banners } from "./data/banners.jsx";
import { API_URL } from "./utils/api";
import "./styles/animations.css";

export default function MediScanApp() {
  const [isScanning, setIsScanning] = useState(false);
  const [showScanResult, setShowScanResult] = useState(false);
  const [showOCRConfirm, setShowOCRConfirm] = useState(false);
  const [scanResult, setScanResult] = useState(null);
  const [ocrData, setOcrData] = useState(null); // Lưu OCR data để xác nhận
  const [currentTab, setCurrentTab] = useState("home");
  const [showNotifications, setShowNotifications] = useState(false);
  const [currentBanner] = useBannerAutoScroll(banners.length, 5000);

  const handleScanClick = () => setIsScanning(true);
  const handleTabClick = (tab) => setCurrentTab(tab);
  const handleScanComplete = () => {
    setIsScanning(false);
    // Nếu đã có kết quả từ camera overlay (đã tìm kiếm), hiển thị kết quả
    if (scanResult) {
      setShowScanResult(true);
    } else if (ocrData && ocrData.extracted_text) {
      // Nếu chỉ có OCR data, hiển thị modal xác nhận
      setShowOCRConfirm(true);
    } else {
      setShowScanResult(true);
    }
  };
  const handleScanResult = (result) => {
    setScanResult(result);
    // Lưu OCR data nếu có
    if (result.all_ocr_texts || result.extracted_text) {
      setOcrData({
        extracted_text: result.extracted_text,
        all_ocr_texts: result.all_ocr_texts || [],
      });
    }
  };

  const handleOCRConfirm = async (confirmedText) => {
    setShowOCRConfirm(false);
    // Gửi lại request scan với text đã xác nhận
    try {
      const response = await fetch(`${API_URL}/scan`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text: confirmedText,
        }),
      });

      const result = await response.json();

      // Cập nhật kết quả với OCR data
      setScanResult({
        ...result,
        extracted_text: confirmedText,
        all_ocr_texts: ocrData?.all_ocr_texts || [],
      });
      setShowScanResult(true);
    } catch (err) {
      console.error("Error searching:", err);
      setScanResult({
        success: false,
        message: "Lỗi khi tìm kiếm thuốc",
        extracted_text: confirmedText,
        all_ocr_texts: ocrData?.all_ocr_texts || [],
      });
      setShowScanResult(true);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex justify-center items-start pt-4 pb-20 font-sans select-none">
      <div className="w-full max-w-md bg-white shadow-2xl rounded-[32px] overflow-hidden min-h-[800px] relative flex flex-col border border-gray-200">
        {/* HEADER */}
        <Header
          showNotifications={showNotifications}
          setShowNotifications={setShowNotifications}
        />

        {/* MAIN CONTENT AREA (Scrollable) */}
        <div className="flex-1 overflow-y-auto pb-28 px-5 scrollbar-hide bg-gray-50/50">
          {currentTab === "home" && <HomeTab currentBanner={currentBanner} />}
          {currentTab === "search" && <SearchTab />}
          {currentTab === "heart" && <FavoritesTab />}
          {currentTab === "user" && <ProfileTab />}
        </div>

        {/* BOTTOM NAVIGATION BAR */}
        <div className="absolute bottom-0 left-0 w-full bg-white border-t border-gray-100 shadow-[0_-5px_20px_rgba(0,0,0,0.03)] px-6 py-2 flex justify-between items-end h-[85px] rounded-t-[32px] z-30">
          <NavItem
            icon={<Home className="w-6 h-6" />}
            label="Trang chủ"
            active={currentTab === "home"}
            onClick={() => handleTabClick("home")}
          />
          <NavItem
            icon={<Search className="w-6 h-6" />}
            label="Tìm kiếm"
            active={currentTab === "search"}
            onClick={() => handleTabClick("search")}
          />

          {/* SCAN BUTTON (Center Floating) */}
          <div className="relative -top-8 group z-40">
            <button
              onClick={handleScanClick}
              className="w-16 h-16 bg-gradient-to-tr from-teal-400 to-cyan-500 rounded-full shadow-[0_8px_25px_rgba(45,212,191,0.5)] flex flex-col items-center justify-center text-white border-4 border-white transform transition-all duration-300 group-hover:scale-110 group-active:scale-95"
            >
              <ScanLine className="w-7 h-7 mb-0.5" />
              <span className="text-[9px] font-bold tracking-wider">SCAN</span>
            </button>
            <div className="absolute top-0 left-0 w-16 h-16 bg-teal-400 rounded-full opacity-0 animate-ping -z-10 group-hover:opacity-30"></div>
          </div>

          <NavItem
            icon={<Heart className="w-6 h-6" />}
            label="Yêu thích"
            active={currentTab === "heart"}
            onClick={() => handleTabClick("heart")}
          />
          <NavItem
            icon={<User className="w-6 h-6" />}
            label="Tài khoản"
            active={currentTab === "user"}
            onClick={() => handleTabClick("user")}
          />
        </div>

        {/* MODALS & OVERLAYS */}
        {isScanning && (
          <ScanOverlay
            onClose={() => setIsScanning(false)}
            onComplete={handleScanComplete}
            onScanResult={handleScanResult}
          />
        )}

        {showOCRConfirm && ocrData && (
          <OCRConfirmModal
            ocrText={ocrData.extracted_text}
            allOcrTexts={ocrData.all_ocr_texts}
            onConfirm={handleOCRConfirm}
            onCancel={() => {
              setShowOCRConfirm(false);
              setOcrData(null);
              setScanResult(null);
            }}
          />
        )}

        {showScanResult && (
          <ScanResultModal
            onClose={() => {
              setShowScanResult(false);
              setScanResult(null);
              setOcrData(null);
            }}
            result={scanResult}
          />
        )}
      </div>
    </div>
  );
}

// Main entry point
export { default as App } from './App';
export { default as MediScanApp } from './App';

// Components
export { default as Header } from './components/Header';
export { default as NavItem } from './components/NavItem';
export { default as ScanOverlay } from './components/ScanOverlay';
export { default as BannerSlider } from './components/BannerSlider';
export { default as CategoryGrid } from './components/CategoryGrid';
export { default as HealthInfoCards } from './components/HealthInfoCards';

// Tabs
export { default as HomeTab } from './components/tabs/HomeTab';
export { default as SearchTab } from './components/tabs/SearchTab';
export { default as FavoritesTab } from './components/tabs/FavoritesTab';
export { default as ProfileTab } from './components/tabs/ProfileTab';

// Modals
export { default as ScanResultModal } from './components/modals/ScanResultModal';

// Hooks
export { useBannerAutoScroll } from './hooks/useBannerAutoScroll';

// Data
export { banners } from './data/banners.jsx';
export { categories } from './data/categories.jsx';
export { healthInfos } from './data/healthInfos.jsx';


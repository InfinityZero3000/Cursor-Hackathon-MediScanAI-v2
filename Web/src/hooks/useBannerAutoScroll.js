import { useState, useEffect } from 'react';

export function useBannerAutoScroll(bannerCount, interval = 5000) {
  const [currentBanner, setCurrentBanner] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentBanner((prev) => (prev + 1) % bannerCount);
    }, interval);

    return () => clearInterval(timer);
  }, [bannerCount, interval]);

  return [currentBanner, setCurrentBanner];
}


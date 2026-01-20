import { useState, useRef, useEffect } from 'react';
import { Play, Pause, Loader2, VolumeX } from 'lucide-react';

const previewCache = new Map();

const PlayButton = ({ title, artist }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [hasError, setHasError] = useState(false);

  const audioRef = useRef(new Audio());
  const abortControllerRef = useRef(null);

  useEffect(() => {
    return () => {
      audioRef.current.pause();
      audioRef.current.src = "";
    };
  }, []);

  const handleToggle = async () => {
    if (isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
      return;
    }

    // Play if already ready
    if (audioRef.current.src && !hasError && audioRef.current.src !== window.location.href) {
      try {
        await audioRef.current.play();
        setIsPlaying(true);
      } catch (e) {
        console.error("Playback failed:", e);
        setHasError(true);
      }
      return;
    }

    setIsLoading(true);
    setHasError(false);

    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();

    try {
      const cacheKey = `${title}-${artist}`;
      let url = previewCache.get(cacheKey);

      if (!url) {
        const query = encodeURIComponent(`${title} ${artist}`);
        
        // REFACTORED: Use Env Var + Backend Proxy Endpoint
        const API_BASE = import.meta.env.VITE_API_URL || '';
        
        //  Render Backend, which proxies to Apple
        const res = await fetch(`${API_BASE}/api/v1/proxy/itunes?term=${query}`, {
          signal: abortControllerRef.current.signal
        });
        
        if (!res.ok) throw new Error(`Proxy error: ${res.status}`);
        
        const data = await res.json();
        
        // Strict check for previewUrl
        if (data.results && data.results.length > 0 && data.results[0].previewUrl) {
          url = data.results[0].previewUrl;
          console.log(`🎵 Preview found for ${title}:`, url);
          previewCache.set(cacheKey, url);
        } else {
          console.warn(`❌ No preview URL found for: ${title}`);
          throw new Error("No preview found");
        }
      }

      audioRef.current.src = url;
      audioRef.current.volume = 0.4;
      audioRef.current.onended = () => setIsPlaying(false);
      
      await audioRef.current.play();
      setIsPlaying(true);

    } catch (err) {
      if (err.name === 'AbortError') return;
      console.warn(`Preview fetch failed for ${title}:`, err);
      setHasError(true);
    } finally {
      setIsLoading(false);
    }
  };

  if (hasError) {
    return (
      <div className="w-10 h-10 flex items-center justify-center rounded-full bg-white/5 cursor-not-allowed" title="No preview available">
        <VolumeX className="w-4 h-4 text-gray-600" />
      </div>
    );
  }

  return (
    <button 
      onClick={handleToggle}
      className={`w-10 h-10 flex items-center justify-center rounded-full transition-all shadow-lg 
        ${isPlaying 
          ? 'bg-spotify-green text-black scale-105 shadow-green-500/20' 
          : 'bg-white text-black hover:scale-105 hover:bg-gray-200'
        }`}
    >
      {isLoading ? (
        <Loader2 className="w-4 h-4 animate-spin" />
      ) : isPlaying ? (
        <Pause className="w-4 h-4 fill-current" />
      ) : (
        <Play className="w-4 h-4 fill-current ml-0.5" />
      )}
    </button>
  );
};

export default PlayButton;
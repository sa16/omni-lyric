import { useState, useEffect } from 'react';
import { Search, Zap, Activity, Server } from 'lucide-react'; 
import PlayButton from './PlayButton';
import logoImg from './assets/logo.jpeg'; 

// FEEDBACK ITEM 3: Extract API_BASE once at top-level.
// This reduces noise and ensures consistency across the module.
const API_BASE = import.meta.env.VITE_API_URL ?? '';

function App() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState(null);
  
  // Server State Machine: 'checking' -> 'booting' -> 'online'
  const [serverStatus, setServerStatus] = useState('checking'); 
  const [bootProgress, setBootProgress] = useState(0);

  useEffect(() => {
    let progressInterval;
    let pollInterval;

    const checkServer = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/v1/health`);
        if (res.ok) {
          setBootProgress(100);
          setServerStatus('online');
          clearInterval(progressInterval);
          clearInterval(pollInterval);
        }
      } catch (e) {
        setServerStatus('booting');
      }
    };

    // Simulate "Cold Start" progress (capped at 90% until real response)
    progressInterval = setInterval(() => {
      setBootProgress(prev => {
        if (prev >= 90) return 90; 
        return prev + 2; 
      });
    }, 1000);

    pollInterval = setInterval(checkServer, 2000);
    checkServer();

    return () => {
      clearInterval(progressInterval);
      clearInterval(pollInterval);
    };
  }, []);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    // FEEDBACK ITEM 2: Strict blocking. 
    // Don't "try" to search if offline. Don't set an error. Just block.
    if (serverStatus !== 'online') return;

    setLoading(true);
    setError(null);
    setStats(null);

    try {
      const response = await fetch(`${API_BASE}/api/v1/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: query, limit: 10 }),
      });

      if (!response.ok) throw new Error("Failed to connect to backend");

      const data = await response.json();
      setResults(data.results);
      setStats({
        latency: data.latency_ms,
        version: data.model_version
      });
      
      // If a search succeeds, we are definitely online
      setServerStatus('online');
      setBootProgress(100); 

    } catch (err) {
      setError("Connection failed. Please try again.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-spotify-black text-white font-sans selection:bg-spotify-green selection:text-black flex flex-col relative">
      
      {/* --- FEEDBACK ITEM 1: INFRA-LITERATE BOOT BAR --- */}
      {serverStatus !== 'online' && (
        <div className="w-full bg-gray-900 border-b border-white/10 sticky top-0 z-50">
           <div className="max-w-2xl mx-auto px-6 py-2">
              <div className="flex justify-between text-xs font-mono text-spotify-green mb-1">
                 <span className="flex items-center gap-2 uppercase">
                    <Server className="w-3 h-3 animate-pulse" />
                    Cold start in progress (Render free tier-May take 1-2mins to boot)
                 </span>
                 <span>{bootProgress}%</span>
              </div>
              <div className="w-full h-1 bg-gray-800 rounded-full overflow-hidden">
                 <div 
                   className="h-full bg-spotify-green transition-all duration-1000 ease-out"
                   style={{ width: `${bootProgress}%` }}
                 ></div>
              </div>
           </div>
        </div>
      )}

      {/* MAIN CONTENT */}
      <div className="flex-grow p-6 md:p-12">
        
        {/* HEADER */}
        <div className="max-w-2xl mx-auto mb-10 text-center">
          <h1 className="text-4xl md:text-5xl font-bold mb-2 tracking-tight flex items-center justify-center gap-4">
            <div className="relative group">
              <div className="absolute -inset-1 bg-spotify-green rounded-full blur opacity-40 group-hover:opacity-75 transition duration-500"></div>
              <img 
                src={logoImg} 
                alt="Omni Logo" 
                className="relative w-14 h-14 rounded-full object-cover border-2 border-spotify-green shadow-lg"
                style={{ filter: 'grayscale(100%) sepia(100%) hue-rotate(90deg) saturate(350%) contrast(1.1)' }}
              />
            </div>
            Omni Search
          </h1>
          <p className="text-gray-400">Semantic Search • pgvector • 57k Songs</p>
        </div>

        {/* SEARCH INPUT */}
        <div className="max-w-2xl mx-auto relative mb-12">
          <form onSubmit={handleSearch} className="relative group z-10">
            <div className="absolute -inset-1 bg-gradient-to-r from-spotify-green to-blue-600 rounded-full blur opacity-20 group-hover:opacity-40 transition duration-500"></div>
            <div className="relative flex items-center bg-spotify-gray rounded-full ring-1 ring-white/10 focus-within:ring-spotify-green transition-all shadow-xl">
              <Search className="ml-4 w-6 h-6 text-gray-400" />
              <input
                type="text"
                className="w-full bg-transparent p-4 outline-none text-lg placeholder-gray-500 text-white rounded-full disabled:opacity-50"
                placeholder={serverStatus === 'online' ? "Search by lyric, mood, or meaning..." : "Waiting for system to boot..."}
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                disabled={serverStatus !== 'online'} 
              />
              <button 
                type="submit" 
                disabled={loading || serverStatus !== 'online'}
                className="mr-2 px-6 py-2 bg-white text-black font-semibold rounded-full hover:bg-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Thinking...' : serverStatus === 'online' ? 'Search' : 'Booting...'}
              </button>
            </div>
          </form>

          {stats && (
            <div className="absolute -bottom-8 right-4 flex items-center gap-4 text-xs font-mono text-gray-500 animate-fade-in">
              <span className="flex items-center gap-1">
                <Zap className="w-3 h-3 text-yellow-400" /> 
                {stats.latency.toFixed(1)}ms
              </span>
              <span className="flex items-center gap-1">
                <Activity className="w-3 h-3 text-blue-400" /> 
                {stats.version}
              </span>
            </div>
          )}
        </div>

        {/* ERROR MSG */}
        {error && (
          <div className="max-w-2xl mx-auto mb-8 p-4 bg-red-900/20 border border-red-800 rounded-lg text-red-200 text-center font-mono text-sm">
            {error}
          </div>
        )}

        {/* RESULTS */}
        <div className="max-w-2xl mx-auto space-y-3">
          {results.map((result, index) => (
            <div 
              key={result.id || index}
              className="group flex items-center gap-4 p-4 bg-spotify-gray/40 hover:bg-white/5 rounded-xl border border-transparent hover:border-white/10 transition-all duration-200"
            >
              <div className="shrink-0">
                <PlayButton title={result.metadata?.title} artist={result.metadata?.artist} />
              </div>
              <div className="flex-1 min-w-0 flex flex-col justify-center">
                <h3 className="font-semibold text-white truncate text-lg leading-tight">
                  {result.metadata?.title || "Unknown Title"}
                </h3>
                <p className="text-sm text-gray-400 truncate mt-0.5">
                  {result.metadata?.artist || "Unknown Artist"}
                </p>
              </div>
              <div className="text-right shrink-0 pl-4">
                {/* FEEDBACK ITEM 4: SEMANTIC LABELING */}
                <div className="text-[10px] text-gray-500 uppercase tracking-wider font-bold mb-0.5">Similarity</div>
                <div className={`text-sm font-mono font-bold ${
                  result.score > 0.6 ? 'text-spotify-green' : 
                  result.score > 0.4 ? 'text-yellow-400' : 'text-gray-400'
                }`}>
                  {(result.score * 100).toFixed(0)}%
                </div>
              </div>
            </div>
          ))}
          {results.length === 0 && !loading && !error && query && serverStatus === 'online' && (
            <div className="text-center text-gray-500 py-12">
              <p>No match found. Try describing the vibe differently.</p>
            </div>
          )}
        </div>
      </div>

      {/* FOOTER */}
      <footer className="w-full py-6 border-t border-white/5 bg-black/20 backdrop-blur-sm mt-auto">
        <div className="max-w-2xl mx-auto px-6 text-center flex flex-col md:flex-row items-center justify-between gap-2 text-xs font-mono text-gray-600">
          <div className="flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${serverStatus === 'online' ? 'bg-spotify-green' : 'bg-yellow-500 animate-pulse'}`}></span>
            <span>{serverStatus === 'online' ? 'SYSTEM ONLINE' : 'BOOTING SEQUENCE...'}</span>
          </div>
          <div className="flex items-center gap-4">
            <span className="hover:text-gray-400 transition-colors">Made by SA16</span>
            <span className="bg-white/10 px-2 py-0.5 rounded text-gray-400">V1.0.0</span>
          </div>
        </div>
      </footer>

    </div>
  );
}

export default App;
import { useState } from 'react';
import { Search, Zap, Activity, Code } from 'lucide-react'; 
import PlayButton from './PlayButton';
import logoImg from './assets/logo.jpeg'; 

function App() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setStats(null);

    try {
      const API_BASE = import.meta.env.VITE_API_URL || '';
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
    } catch (err) {
      setError("Backend connection failed. Is the server running?");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-spotify-black text-white font-sans selection:bg-spotify-green selection:text-black flex flex-col">
      
      {/* MAIN CONTENT WRAPPER (Grows to fill space) */}
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
                className="w-full bg-transparent p-4 outline-none text-lg placeholder-gray-500 text-white rounded-full"
                placeholder="Search by lyric, mood, or meaning..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
              <button 
                type="submit" 
                disabled={loading}
                className="mr-2 px-6 py-2 bg-white text-black font-semibold rounded-full hover:bg-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Thinking...' : 'Search'}
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

        {/* ERROR */}
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
                <div className="text-[10px] text-gray-500 uppercase tracking-wider font-bold mb-0.5">Match</div>
                <div className={`text-sm font-mono font-bold ${
                  result.score > 0.6 ? 'text-spotify-green' : 
                  result.score > 0.4 ? 'text-yellow-400' : 'text-gray-400'
                }`}>
                  {(result.score * 100).toFixed(0)}%
                </div>
              </div>
            </div>
          ))}
          {results.length === 0 && !loading && !error && query && (
            <div className="text-center text-gray-500 py-12">
              <p>No match found, try again!</p>
            </div>
          )}
        </div>
      </div>

      {/* FOOTER */}
      <footer className="w-full py-6 border-t border-white/5 bg-black/20 backdrop-blur-sm mt-auto">
        <div className="max-w-2xl mx-auto px-6 text-center flex flex-col md:flex-row items-center justify-between gap-2 text-xs font-mono text-gray-600">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-spotify-green animate-pulse"></span>
            <span>SYSTEM ONLINE</span>
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
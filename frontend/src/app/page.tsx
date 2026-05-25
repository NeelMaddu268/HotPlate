"use client";

import { useState, useEffect, useCallback } from "react";
import { Search, Loader2, UtensilsCrossed, Flame, Filter, ArrowUpDown } from "lucide-react";
import { DealCard } from "@/components/DealCard";

interface Deal {
  id: string;
  item_name: string;
  price: number;
  image_url: string;
  expires_at: string | null;
  start_at: string | null;
  is_weekly: boolean;
  recurrence_day: number | null;
  cuisine_type: string | null;
  is_currently_active: boolean;
  restaurant_name: string;
  restaurant_phone: string;
  similarity: number;
}

const CUISINES = ["All", "Burgers", "Sushi", "Mexican", "Italian", "Thai", "Healthy"];

export default function Home() {
  const [query, setQuery] = useState("");
  const [deals, setDeals] = useState<Deal[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Filters
  const [selectedCuisine, setSelectedCuisine] = useState("All");
  const [sortBy, setSortBy] = useState("similarity");
  const [mode, setMode] = useState("all");

  const fetchDeals = useCallback(async (currentQuery: string, cuisine: string, sort: string, currentMode: string) => {
    setLoading(true);
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const baseUrl = currentQuery.trim() 
        ? `${API_URL}/search?q=${encodeURIComponent(currentQuery)}` 
        : `${API_URL}/deals?`;
      
      const queryParams = new URLSearchParams();
      if (cuisine !== "All") queryParams.append("cuisine_type", cuisine);
      queryParams.append("sort_by", sort);
      queryParams.append("mode", currentMode);
      
      const connector = baseUrl.includes('?') ? '&' : '?';
      const res = await fetch(`${baseUrl}${connector}${queryParams.toString()}`);
      const data = await res.json();
      setDeals(data.deals || []);
    } catch (error) {
      console.error("Failed to fetch deals:", error);
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch all active deals on initial load and when filters change (unless searching)
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchDeals(query, selectedCuisine, sortBy, mode);
  }, [selectedCuisine, sortBy, mode, fetchDeals]); // Removed query to prevent fetch-as-you-type spam

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    fetchDeals(query, selectedCuisine, sortBy, mode);
  };

  return (
    <main className="min-h-screen bg-[#050810] text-slate-50 font-sans selection:bg-rose-500/30">
      
      {/* Dynamic Background Effects */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-[20%] -left-[10%] w-[50%] h-[50%] rounded-full bg-rose-600/10 blur-[120px]"></div>
        <div className="absolute top-[20%] -right-[10%] w-[50%] h-[50%] rounded-full bg-purple-600/10 blur-[120px]"></div>
      </div>

      {/* Hero Section */}
      <div className="relative pt-32 pb-8 px-6 max-w-5xl mx-auto text-center flex flex-col items-center z-10">
        <div className="inline-flex items-center justify-center p-3 bg-gradient-to-br from-rose-500/20 to-orange-500/20 text-rose-400 rounded-2xl mb-8 shadow-[0_0_40px_rgba(244,63,94,0.15)] border border-rose-500/30 backdrop-blur-xl">
          <Flame size={32} className="animate-pulse" />
        </div>
        <h1 className="text-6xl md:text-8xl font-black tracking-tighter mb-6 text-transparent bg-clip-text bg-gradient-to-br from-white via-slate-200 to-slate-500 drop-shadow-sm">
          Discover Food. <br className="hidden md:block"/>
          <span className="bg-gradient-to-r from-rose-400 to-orange-500 bg-clip-text text-transparent">Instantly.</span>
        </h1>
        <p className="text-xl md:text-2xl text-slate-400 mb-12 max-w-2xl font-light tracking-wide">
          An AI-powered feed of live flash deals happening around you. Search your cravings or browse what&apos;s hot right now.
        </p>

        {/* Search Bar */}
        <form onSubmit={handleSearch} className="w-full max-w-3xl relative group">
          <div className="absolute inset-0 bg-gradient-to-r from-rose-500/40 to-orange-500/40 rounded-full blur-2xl group-hover:blur-3xl transition-all duration-500 opacity-60"></div>
          <div className="relative flex items-center bg-[#0B0F19]/90 backdrop-blur-2xl border border-white/10 rounded-full shadow-2xl p-2.5 transition-all duration-500 focus-within:border-rose-500/50 focus-within:shadow-[0_0_30px_rgba(244,63,94,0.2)]">
            <Search className="text-rose-400 ml-5 h-7 w-7" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Craving spicy tuna or cheap pizza..."
              className="w-full bg-transparent border-none text-white px-5 py-4 focus:outline-none text-xl placeholder-slate-500 font-medium"
            />
            <button
              type="submit"
              disabled={loading}
              className="bg-gradient-to-r from-rose-500 to-orange-500 hover:from-rose-400 hover:to-orange-400 text-white font-bold text-lg py-4 px-10 rounded-full shadow-[0_0_20px_rgba(244,63,94,0.4)] transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center hover:scale-[1.02] active:scale-[0.98]"
            >
              {loading ? <Loader2 className="animate-spin h-6 w-6" /> : "Find Deals"}
            </button>
          </div>
        </form>
      </div>

      {/* Filter and Sort Bar */}
      <div className="relative max-w-7xl mx-auto px-6 mb-12 z-10">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4 bg-[#0B0F19]/50 backdrop-blur-md border border-white/5 p-4 rounded-3xl">
          
          {/* Cuisines */}
          <div className="flex items-center gap-2 overflow-x-auto w-full md:w-auto pb-2 md:pb-0 scrollbar-hide">
            <Filter size={18} className="text-slate-400 mr-2 shrink-0" />
            {CUISINES.map(c => (
              <button
                key={c}
                onClick={() => setSelectedCuisine(c)}
                className={`px-4 py-2 rounded-full text-sm font-bold whitespace-nowrap transition-all duration-300 border ${
                  selectedCuisine === c 
                    ? 'bg-rose-500 border-rose-400 text-white shadow-[0_0_15px_rgba(244,63,94,0.3)]' 
                    : 'bg-white/5 border-white/10 text-slate-300 hover:bg-white/10'
                }`}
              >
                {c}
              </button>
            ))}
          </div>

          {/* Controls */}
          <div className="flex items-center gap-4 shrink-0 w-full md:w-auto justify-between md:justify-end">
            <select
              value={mode}
              onChange={(e) => setMode(e.target.value)}
              className="bg-white/5 border border-white/10 text-slate-300 text-sm font-bold rounded-xl px-4 py-2 focus:outline-none focus:border-rose-500/50 appearance-none cursor-pointer hover:bg-white/10 transition-colors"
            >
              <option value="all">All Deals Today</option>
              <option value="active">Active Right Now</option>
            </select>
            
            <div className="flex items-center gap-2 bg-white/5 border border-white/10 rounded-xl px-4 py-2 hover:bg-white/10 transition-colors">
              <ArrowUpDown size={16} className="text-rose-400" />
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="bg-transparent border-none text-slate-300 text-sm font-bold focus:outline-none appearance-none cursor-pointer"
              >
                <option value="similarity">Sort by Relevance</option>
                <option value="price_asc">Price: Low to High</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Results Feed */}
      <div className="relative max-w-7xl mx-auto px-6 pb-32 z-10">
        
        {/* Feed Header */}
        <div className="flex items-center justify-between mb-10 border-b border-white/5 pb-6">
          <h2 className="text-3xl font-black text-white tracking-tight flex items-center gap-3">
            {query.trim() ? "Search Results" : "Live Deals"}
            {!loading && <span className="text-sm font-bold bg-white/10 px-3 py-1 rounded-full text-slate-300">{deals.length}</span>}
          </h2>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="h-[400px] bg-white/5 border border-white/10 rounded-3xl animate-pulse"></div>
            ))}
          </div>
        ) : deals.length === 0 ? (
          <div className="text-center text-slate-400 mt-20 p-16 bg-[#0B0F19]/50 rounded-[3rem] border border-white/5 backdrop-blur-xl max-w-2xl mx-auto shadow-2xl">
            <UtensilsCrossed className="mx-auto h-16 w-16 mb-6 text-slate-600 opacity-50" />
            <p className="text-3xl font-black text-white mb-3">No deals found.</p>
            <p className="text-xl text-slate-500 font-light">Try adjusting your filters or search for something else!</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
            {deals.map((deal, index) => (
              <DealCard key={deal.id} deal={deal} priority={index < 4} />
            ))}
          </div>
        )}
      </div>
    </main>
  );
}

"use client";

import { useState, useEffect, useCallback } from "react";
import { Search, UtensilsCrossed, ArrowDownRight, Filter, ChevronDown } from "lucide-react";
import { FeaturedDealCard, StandardDealCard, CompactDealCard, Deal } from "@/components/DealCard";

const CUISINES = ["All", "Burgers", "Sushi", "Mexican", "Italian", "Thai", "Healthy"];

export default function Home() {
  const [query, setQuery] = useState("");
  const [searchInput, setSearchInput] = useState(""); // For the input field before submission
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
  }, [selectedCuisine, sortBy, mode, fetchDeals, query]);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setQuery(searchInput);
  };

  // Live Deal Preview Data (Mocked for Hero if no deals loaded yet, or use first few deals)
  const previewDeals = deals.slice(0, 3);

  return (
    <main className="min-h-screen bg-background text-text font-sans selection:bg-accent/20">
      
      {/* Hero Section */}
      <section className="max-w-[1240px] mx-auto px-6 pt-20 pb-24 md:pt-32 md:pb-32">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-16 items-center">
          
          {/* Left: Copy & CTA */}
          <div className="lg:col-span-7 flex flex-col items-start text-left">
            <h1 className="font-display text-5xl md:text-7xl font-bold tracking-tight text-text leading-[1.1] mb-6">
              Live flash deals,<br />
              happening <span className="text-accent italic pr-2">right now.</span>
            </h1>
            <p className="text-lg md:text-xl text-text-muted mb-10 max-w-lg leading-relaxed">
              Discover spontaneous food drops and time-sensitive discounts from the best spots in your neighborhood.
            </p>

            <div className="flex flex-col sm:flex-row items-center gap-4 w-full max-w-xl">
              <button 
                onClick={() => {
                  document.getElementById('deals-feed')?.scrollIntoView({ behavior: 'smooth' });
                }}
                className="w-full sm:w-auto bg-accent hover:bg-accent-hover text-white font-bold py-4 px-8 rounded-lg shadow-sm transition-colors text-lg"
              >
                Browse Nearby
              </button>
              
              <form onSubmit={handleSearch} className="w-full relative flex items-center shadow-sm hover:shadow-md transition-shadow rounded-lg overflow-hidden border border-border focus-within:border-accent focus-within:ring-1 focus-within:ring-accent bg-surface">
                <div className="pl-4 pr-2 py-3 text-text-muted">
                  <Search size={20} />
                </div>
                <input
                  type="text"
                  value={searchInput}
                  onChange={(e) => setSearchInput(e.target.value)}
                  placeholder="Sushi, pizza..."
                  className="w-full bg-transparent text-text py-4 pr-4 focus:outline-none placeholder-text-muted text-base"
                />
              </form>
            </div>
          </div>

          {/* Right: Live Preview Panel */}
          <div className="hidden lg:block lg:col-span-5 relative">
            <div className="bg-surface border border-border p-6 rounded-xl shadow-lg relative z-10">
              <div className="flex items-center justify-between mb-6 pb-4 border-b border-border">
                <h3 className="font-display text-lg font-bold flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-accent animate-pulse"></span>
                  Live Feed
                </h3>
                <span className="text-xs font-semibold text-text-muted uppercase tracking-wider">Nearby</span>
              </div>
              
              <div className="flex flex-col gap-4">
                {previewDeals.length > 0 ? (
                  previewDeals.map(deal => (
                    <CompactDealCard key={deal.id} deal={deal} />
                  ))
                ) : (
                  <div className="flex flex-col gap-4">
                     {/* Skeleton loaders if empty */}
                     {[1,2,3].map(i => (
                       <div key={i} className="flex gap-4 items-center p-3 border border-stone-100 rounded-lg">
                         <div className="w-20 h-20 bg-stone-100 animate-pulse rounded-md"></div>
                         <div className="flex-1 space-y-3">
                           <div className="h-4 bg-stone-100 animate-pulse rounded w-3/4"></div>
                           <div className="h-3 bg-stone-100 animate-pulse rounded w-1/2"></div>
                         </div>
                       </div>
                     ))}
                  </div>
                )}
              </div>
            </div>
            {/* Decorative offset background to make it feel like layered UI */}
            <div className="absolute top-4 -right-4 w-full h-full border border-border rounded-xl -z-10 bg-stone-50"></div>
          </div>
        </div>
      </section>

      {/* Control Row */}
      <section className="border-y border-border bg-surface sticky top-0 z-40 shadow-sm">
        <div className="max-w-[1240px] mx-auto px-6 py-4 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          
          <div className="flex items-center gap-2 overflow-x-auto w-full md:w-auto pb-2 md:pb-0 scrollbar-hide shrink-0">
            <span className="text-sm font-semibold text-text-muted mr-2 flex items-center gap-1 shrink-0 uppercase tracking-wider">
              <Filter size={14} /> Filters
            </span>
            {CUISINES.map(c => (
              <button
                key={c}
                onClick={() => setSelectedCuisine(c)}
                className={`px-3.5 py-1.5 rounded-md text-sm font-medium whitespace-nowrap transition-colors ${
                  selectedCuisine === c 
                    ? 'bg-text text-surface' 
                    : 'bg-stone-50 text-text-muted hover:bg-stone-100 hover:text-text border border-transparent'
                }`}
              >
                {c}
              </button>
            ))}
          </div>

          <div className="flex flex-col sm:flex-row items-center gap-3 w-full md:w-auto justify-between md:justify-end">
            <form onSubmit={handleSearch} className="w-full sm:w-48 relative flex items-center border border-border rounded-md bg-stone-50 focus-within:border-accent focus-within:ring-1 focus-within:ring-accent overflow-hidden transition-colors">
              <div className="pl-3 py-2 text-text-muted">
                <Search size={14} />
              </div>
              <input
                type="text"
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                placeholder="Search..."
                className="w-full bg-transparent text-text py-2 pr-3 text-sm focus:outline-none placeholder-text-muted"
              />
            </form>

            <div className="flex items-center gap-3 w-full sm:w-auto">
              <div className="relative group flex-1 sm:flex-none">
              <select
                value={mode}
                onChange={(e) => setMode(e.target.value)}
                className="appearance-none bg-stone-50 border border-border text-text text-sm font-medium rounded-md pl-3 pr-8 py-2 focus:outline-none focus:border-text cursor-pointer transition-colors"
              >
                <option value="all">All Deals Today</option>
                <option value="active">Active Right Now</option>
              </select>
              <ChevronDown size={14} className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted pointer-events-none" />
            </div>
            
            <div className="relative group">
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="appearance-none bg-stone-50 border border-border text-text text-sm font-medium rounded-md pl-3 pr-8 py-2 focus:outline-none focus:border-text cursor-pointer transition-colors"
              >
                <option value="similarity">Relevance</option>
                <option value="price_asc">Price: Low to High</option>
              </select>
              <ChevronDown size={14} className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted pointer-events-none" />
            </div>
            </div>
          </div>
        </div>
      </section>

      {/* Feed Section */}
      <section id="deals-feed" className="max-w-[1240px] mx-auto px-6 py-16 pb-32">
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-3xl font-display font-bold text-text flex items-center gap-2">
            {query.trim() ? "Search Results" : "Live Deals"}
            {!loading && <span className="text-sm font-medium text-text-muted bg-stone-100 px-2 py-0.5 rounded-md">{deals.length}</span>}
          </h2>
          {query.trim() && (
            <button onClick={() => {setQuery(""); setSearchInput("");}} className="text-sm font-medium text-text hover:text-accent flex items-center gap-1 transition-colors">
              Clear search <ArrowDownRight size={16} />
            </button>
          )}
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="h-64 bg-stone-100 rounded-lg animate-pulse border border-border"></div>
            ))}
          </div>
        ) : deals.length === 0 ? (
          <div className="text-center mt-12 p-12 border border-border rounded-xl bg-surface max-w-2xl mx-auto">
            <UtensilsCrossed className="mx-auto h-12 w-12 mb-4 text-stone-300" />
            <p className="text-xl font-display font-bold text-text mb-2">No deals found.</p>
            <p className="text-text-muted">Try adjusting your filters or search for something else.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 auto-rows-max">
            {deals.map((deal, index) => {
              // Create visual rhythm:
              // Index 0 is Featured and spans 2 columns on large screens
              // Index 3, 4 are Compact and stacked? Actually, CSS grid doesn't easily stack items in the same cell.
              // Let's use standard grid with col-span for Featured.
              if (index === 0) {
                return (
                  <div key={deal.id} className="md:col-span-2 lg:col-span-2">
                    <FeaturedDealCard deal={deal} priority={true} />
                  </div>
                );
              }
              // Mix in a few compact cards occasionally (e.g. index 3, 7)
              if (index % 4 === 3) {
                return <CompactDealCard key={deal.id} deal={deal} />;
              }
              // Default to standard card
              return <StandardDealCard key={deal.id} deal={deal} />;
            })}
          </div>
        )}
      </section>
    </main>
  );
}

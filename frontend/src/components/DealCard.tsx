import { MapPin, Clock, Tag, History, Flame } from "lucide-react";
import Image from "next/image";

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

export function DealCard({ deal, priority = false }: { deal: Deal, priority?: boolean }) {
  // Calculate remaining time
  const expires = deal.expires_at ? new Date(deal.expires_at) : null;
  const now = new Date();
  const diffHours = expires ? Math.max(0, Math.floor((expires.getTime() - now.getTime()) / (1000 * 60 * 60))) : 0;

  const isActive = deal.is_currently_active;

  return (
    <div className={`group relative overflow-hidden rounded-3xl bg-[#0B0F19] border border-white/5 shadow-2xl transition-all duration-500 hover:-translate-y-2 hover:shadow-rose-500/30 flex flex-col h-[400px] ${!isActive ? 'opacity-70 grayscale-[30%]' : ''}`}>
      
      {/* Edge-to-edge image background */}
      <div className="absolute inset-0 w-full h-full">
        {deal.image_url ? (
          <Image 
            src={deal.image_url} 
            alt={deal.item_name} 
            fill
            sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
            priority={priority}
            className="object-cover transition-transform duration-700 group-hover:scale-110"
          />
        ) : (
          <div className="h-full w-full bg-slate-900 flex items-center justify-center"></div>
        )}
      </div>

      {/* Dynamic Gradient Overlay */}
      <div className="absolute inset-0 bg-gradient-to-t from-[#0B0F19] via-[#0B0F19]/80 to-transparent transition-opacity duration-500"></div>

      {/* Inactive Overlay */}
      {!isActive && (
        <div className="absolute inset-0 bg-black/40 backdrop-blur-[2px] z-0 flex items-center justify-center">
          <div className="bg-black/60 border border-white/10 px-6 py-2 rounded-full backdrop-blur-md flex items-center gap-2 text-slate-300 font-bold uppercase tracking-widest shadow-xl transform -rotate-12 scale-110">
            <History size={18} />
            Ended
          </div>
        </div>
      )}

      {/* Content Container - Pushed to the bottom */}
      <div className="relative z-10 flex flex-col h-full p-6 justify-end">
        
        {/* Top Badges */}
        <div className="absolute top-5 right-5 flex flex-col items-end gap-2">
          <div className={`bg-white/10 backdrop-blur-xl border border-white/20 text-white font-black px-4 py-1.5 rounded-full text-lg shadow-2xl flex items-center gap-1 transition-all duration-300 ${isActive ? 'group-hover:bg-rose-500 group-hover:border-rose-400 group-hover:text-white' : ''}`}>
            <Tag size={16} className={`${isActive ? 'text-rose-400 group-hover:text-white' : 'text-slate-400'} transition-colors`} />
            ${deal.price.toFixed(2)}
          </div>
          {deal.cuisine_type && (
            <div className="bg-black/50 backdrop-blur-md border border-white/10 text-slate-200 text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider">
              {deal.cuisine_type}
            </div>
          )}
        </div>

        {/* Info Area */}
        <div className="transform transition-transform duration-500 translate-y-2 group-hover:translate-y-0">
          {isActive && diffHours > 0 && !deal.is_weekly && (
            <div className="inline-flex items-center gap-1.5 bg-amber-500/20 text-amber-300 border border-amber-500/30 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider mb-3 backdrop-blur-md">
              <Clock size={12} className="animate-pulse" />
              Ends in {diffHours}h
            </div>
          )}
          {isActive && deal.is_weekly && (
            <div className="inline-flex items-center gap-1.5 bg-purple-500/20 text-purple-300 border border-purple-500/30 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider mb-3 backdrop-blur-md">
              <Flame size={12} />
              Weekly Special
            </div>
          )}
          <h3 className={`text-2xl font-extrabold mb-2 leading-tight drop-shadow-md line-clamp-2 ${isActive ? 'text-white' : 'text-slate-300'}`}>
            {deal.item_name}
          </h3>
          
          <div className={`flex items-center text-sm font-medium transition-opacity duration-300 ${isActive ? 'text-slate-300 opacity-80 group-hover:opacity-100' : 'text-slate-400'}`}>
            <div className="bg-white/10 p-1.5 rounded-full mr-2 backdrop-blur-sm border border-white/5">
              <MapPin size={14} className={isActive ? "text-rose-400" : "text-slate-400"} />
            </div>
            <span className="truncate">{deal.restaurant_name}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

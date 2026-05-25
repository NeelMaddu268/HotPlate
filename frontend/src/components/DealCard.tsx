import { Clock, Flame } from "lucide-react";
import Image from "next/image";

export interface Deal {
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

function calculateDiffHours(expires_at: string | null): number {
  if (!expires_at) return 0;
  const expires = new Date(expires_at);
  const now = new Date();
  return Math.max(0, Math.floor((expires.getTime() - now.getTime()) / (1000 * 60 * 60)));
}

export function FeaturedDealCard({ deal, priority = false }: { deal: Deal, priority?: boolean }) {
  const diffHours = calculateDiffHours(deal.expires_at);
  const isActive = deal.is_currently_active;

  return (
    <div className={`group relative bg-surface border border-border rounded-xl shadow-sm hover:shadow-md transition-all duration-300 ease-in-out hover:-translate-y-1 overflow-hidden break-inside-avoid flex flex-col ${!isActive ? 'opacity-60 grayscale-[80%]' : ''}`}>
      <div className="relative w-full h-72">
        {deal.image_url ? (
          <Image 
            src={deal.image_url} 
            alt={deal.item_name} 
            fill
            sizes="(max-width: 768px) 100vw, 50vw"
            priority={priority}
            className="object-cover transition-transform duration-700 group-hover:scale-105"
          />
        ) : (
          <div className="h-full w-full bg-stone-100 flex items-center justify-center"></div>
        )}
        
        {deal.cuisine_type && (
          <div className="absolute top-4 right-4 bg-surface/95 text-text text-[10px] font-bold px-2.5 py-1 rounded-md uppercase tracking-widest shadow-sm">
            {deal.cuisine_type}
          </div>
        )}

        <div className="absolute bottom-4 left-4 bg-surface text-text font-black px-4 py-2 rounded-lg text-lg shadow-md flex items-center gap-1">
          ${deal.price.toFixed(2)}
        </div>

        {!isActive && (
          <div className="absolute inset-0 bg-stone-900/10 z-10 flex items-center justify-center">
            <div className="bg-surface text-text px-4 py-1.5 rounded-md font-bold uppercase tracking-widest shadow-sm transform -rotate-12">
              Ended
            </div>
          </div>
        )}
      </div>

      <div className="flex flex-col p-6 flex-1">
        <h3 className="text-2xl font-display font-semibold text-text tracking-tight mb-2 line-clamp-2 leading-snug">
          {deal.item_name}
        </h3>
        
        <div className="flex items-center text-text-muted text-sm font-medium mb-5">
          <span className="truncate">{deal.restaurant_name}</span>
        </div>

        <div className="mt-auto flex items-center gap-2">
          {isActive && diffHours > 0 && !deal.is_weekly && (
            <div className="inline-flex items-center gap-1.5 text-accent bg-accent-light px-2.5 py-1 rounded-md text-[11px] font-bold uppercase tracking-wider">
              <Clock size={12} />
              Ends in {diffHours}h
            </div>
          )}
          {isActive && deal.is_weekly && (
            <div className="inline-flex items-center gap-1.5 text-accent bg-accent-light px-2.5 py-1 rounded-md text-[11px] font-bold uppercase tracking-wider">
              <Flame size={12} />
              Weekly
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export function StandardDealCard({ deal, priority = false }: { deal: Deal, priority?: boolean }) {
  const diffHours = calculateDiffHours(deal.expires_at);
  const isActive = deal.is_currently_active;

  return (
    <div className={`group relative bg-surface border border-border rounded-lg shadow-sm hover:shadow transition-all duration-200 overflow-hidden break-inside-avoid flex flex-col ${!isActive ? 'opacity-50 grayscale-[100%]' : ''}`}>
      <div className="relative w-full h-48">
        {deal.image_url ? (
          <Image 
            src={deal.image_url} 
            alt={deal.item_name} 
            fill
            sizes="(max-width: 768px) 100vw, 33vw"
            priority={priority}
            className="object-cover transition-transform duration-500 group-hover:scale-105"
          />
        ) : (
          <div className="h-full w-full bg-stone-100 flex items-center justify-center"></div>
        )}
        
        <div className="absolute bottom-3 left-3 bg-surface text-text font-bold px-2.5 py-1 rounded-md text-sm shadow-sm">
          ${deal.price.toFixed(2)}
        </div>
      </div>

      <div className="flex flex-col p-4 flex-1">
        <h3 className="text-lg font-medium text-text mb-1 line-clamp-1">
          {deal.item_name}
        </h3>
        
        <div className="text-text-muted text-sm mb-3 truncate">
          {deal.restaurant_name}
        </div>

        <div className="mt-auto">
          {isActive && diffHours > 0 && !deal.is_weekly && (
            <span className="text-accent text-xs font-semibold tracking-wide">
              {diffHours}h left
            </span>
          )}
          {!isActive && (
            <span className="text-text-muted text-xs font-medium uppercase tracking-wider">
              Expired
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

export function CompactDealCard({ deal }: { deal: Deal }) {
  const diffHours = calculateDiffHours(deal.expires_at);
  const isActive = deal.is_currently_active;

  return (
    <div className={`group flex items-center gap-4 bg-surface border border-border p-3 rounded-lg shadow-sm hover:shadow transition-all duration-200 break-inside-avoid ${!isActive ? 'opacity-50 grayscale-[100%]' : ''}`}>
      <div className="relative w-20 h-20 shrink-0 rounded-md overflow-hidden bg-stone-100">
        {deal.image_url && (
          <Image 
            src={deal.image_url} 
            alt={deal.item_name} 
            fill
            sizes="80px"
            className="object-cover transition-transform duration-300 group-hover:scale-105"
          />
        )}
      </div>

      <div className="flex flex-col flex-1 min-w-0">
        <div className="flex justify-between items-start gap-2 mb-1">
          <h3 className="text-base font-medium text-text truncate">
            {deal.item_name}
          </h3>
          <span className="font-bold text-text shrink-0">
            ${deal.price.toFixed(2)}
          </span>
        </div>
        
        <div className="text-text-muted text-sm truncate mb-1">
          {deal.restaurant_name}
        </div>

        <div>
          {isActive && diffHours > 0 && !deal.is_weekly && (
            <span className="text-accent text-xs font-medium">
              Ends in {diffHours}h
            </span>
          )}
          {!isActive && (
            <span className="text-text-muted text-xs">
              Expired
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

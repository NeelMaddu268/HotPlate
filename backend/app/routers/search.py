from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime
import json
from typing import Optional
from app.core.db import get_session
from app.services.processing import generate_embedding

router = APIRouter()

@router.get("/search")
async def search_deals(
    q: str = Query(..., min_length=1), 
    cuisine_type: Optional[str] = None,
    sort_by: str = Query("similarity", regex="^(similarity|price_asc)$"),
    mode: str = Query("active", regex="^(active|all)$"),
    session: AsyncSession = Depends(get_session)
):
    try:
        query_embedding = await generate_embedding(q)
        vector_str = json.dumps(query_embedding)
        
        query = text("""
            SELECT md.id, md.item_name, md.price, md.image_url, md.expires_at, 
                   md.start_at, md.is_weekly, md.recurrence_day, md.cuisine_type, md.is_currently_active, md.similarity,
                   r.name as restaurant_name, r.phone_number as restaurant_phone
            FROM match_deals(
                query_embedding := CAST(:embedding AS vector),
                search_text := :search_text,
                match_threshold := 0.35,
                match_count := 20,
                filter_cuisine := :filter_cuisine,
                mode := :mode,
                sort_by := :sort_by
            ) md
            JOIN restaurants r ON md.restaurant_id = r.id
        """)
        
        result = await session.execute(query, {
            "embedding": vector_str,
            "search_text": q,
            "filter_cuisine": cuisine_type if cuisine_type else "",
            "mode": mode,
            "sort_by": sort_by
        })
        rows = result.fetchall()
        
        deals = []
        for row in rows:
            deals.append({
                "id": str(row.id),
                "item_name": row.item_name,
                "price": float(row.price),
                "image_url": row.image_url,
                "expires_at": row.expires_at.isoformat() if row.expires_at else None,
                "start_at": row.start_at.isoformat() if row.start_at else None,
                "is_weekly": row.is_weekly,
                "recurrence_day": row.recurrence_day,
                "cuisine_type": row.cuisine_type,
                "is_currently_active": row.is_currently_active,
                "restaurant_name": row.restaurant_name,
                "restaurant_phone": row.restaurant_phone,
                "similarity": float(row.similarity)
            })
            
        return {"deals": deals}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/deals")
async def get_all_deals(
    cuisine_type: Optional[str] = None,
    sort_by: str = Query("similarity", regex="^(similarity|price_asc)$"),
    mode: str = Query("active", regex="^(active|all)$"),
    session: AsyncSession = Depends(get_session)
):
    try:
        query = text("""
            SELECT md.id, md.item_name, md.price, md.image_url, md.expires_at, 
                   md.start_at, md.is_weekly, md.recurrence_day, md.cuisine_type, md.is_currently_active, md.similarity,
                   r.name as restaurant_name, r.phone_number as restaurant_phone
            FROM match_deals(
                query_embedding := NULL,
                search_text := NULL,
                match_threshold := 0.0,
                match_count := 50,
                filter_cuisine := :filter_cuisine,
                mode := :mode,
                sort_by := :sort_by
            ) md
            JOIN restaurants r ON md.restaurant_id = r.id
        """)
        
        result = await session.execute(query, {
            "filter_cuisine": cuisine_type if cuisine_type else "",
            "mode": mode,
            "sort_by": sort_by
        })
        rows = result.fetchall()
        
        deals = []
        for row in rows:
            deals.append({
                "id": str(row.id),
                "item_name": row.item_name,
                "price": float(row.price),
                "image_url": row.image_url,
                "expires_at": row.expires_at.isoformat() if row.expires_at else None,
                "start_at": row.start_at.isoformat() if row.start_at else None,
                "is_weekly": row.is_weekly,
                "recurrence_day": row.recurrence_day,
                "cuisine_type": row.cuisine_type,
                "is_currently_active": row.is_currently_active,
                "restaurant_name": row.restaurant_name,
                "restaurant_phone": row.restaurant_phone,
                "similarity": 1.0
            })
            
        return {"deals": deals}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

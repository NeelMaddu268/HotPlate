import asyncio
import os
import uuid
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

load_dotenv()

from app.core.db import engine
from app.models import Restaurant, Deal
from app.services.processing import generate_embedding

MOCK_DEALS = [
    {
        "item_name": "Double Bacon Cheeseburger with Loaded Fries",
        "price": 12.00,
        "cuisine_type": "Burgers",
        "image_url": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?q=80&w=800&auto=format&fit=crop",
        # Flash deal that expired 1 hour ago
        "start_offset_hours": -3,
        "expires_offset_hours": -1,
        "is_weekly": False
    },
    {
        "item_name": "Spicy Tuna Crispy Rice",
        "price": 8.00,
        "cuisine_type": "Sushi",
        "image_url": "https://images.unsplash.com/photo-1579584425555-c3ce17fd4351?q=80&w=800&auto=format&fit=crop",
        # Active flash deal for the next 2 hours
        "start_offset_hours": -1,
        "expires_offset_hours": 2,
        "is_weekly": False
    },
    {
        "item_name": "Taco Tuesday: 3 Al Pastor Tacos + Marg",
        "price": 15.00,
        "cuisine_type": "Mexican",
        "image_url": "https://images.unsplash.com/photo-1551504734-5ee1c4a1479b?q=80&w=800&auto=format&fit=crop",
        # Weekly deal on current day of week
        "start_offset_hours": -10,
        "expires_offset_hours": 2,
        "is_weekly": True,
        "recurrence_day_offset": 0 # Today
    },
    {
        "item_name": "Handmade Truffle Pasta",
        "price": 22.00,
        "cuisine_type": "Italian",
        "image_url": "https://images.unsplash.com/photo-1473093295043-cdd812d0e601?q=80&w=800&auto=format&fit=crop",
        # Upcoming deal starting in 2 hours
        "start_offset_hours": 2,
        "expires_offset_hours": 6,
        "is_weekly": False
    },
    {
        "item_name": "Pad Thai Special",
        "price": 14.50,
        "cuisine_type": "Thai",
        "image_url": "https://images.unsplash.com/photo-1559314809-0d155014e29e?q=80&w=800&auto=format&fit=crop",
        # Weekly deal on tomorrow
        "start_offset_hours": 0,
        "expires_offset_hours": 10,
        "is_weekly": True,
        "recurrence_day_offset": 1 # Tomorrow
    },
    {
        "item_name": "Classic Margherita Pizza",
        "price": 10.00,
        "cuisine_type": "Italian",
        "image_url": "https://images.unsplash.com/photo-1574071318508-1cdbab80d002?q=80&w=800&auto=format&fit=crop",
        # All day deal
        "start_offset_hours": -5,
        "expires_offset_hours": 10,
        "is_weekly": False
    },
    {
        "item_name": "Fresh Organic Acai Bowl",
        "price": 9.50,
        "cuisine_type": "Healthy",
        "image_url": "https://images.unsplash.com/photo-1590301157890-4810ed352733?q=80&w=800&auto=format&fit=crop",
        # Expired yesterday
        "start_offset_hours": -48,
        "expires_offset_hours": -24,
        "is_weekly": False
    },
    {
        "item_name": "Spicy Chicken Sandwich",
        "price": 7.00,
        "cuisine_type": "Burgers",
        "image_url": "https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?q=80&w=800&auto=format&fit=crop",
        # Weekly deal yesterday
        "start_offset_hours": -10,
        "expires_offset_hours": 2,
        "is_weekly": True,
        "recurrence_day_offset": -1
    },
    {
        "item_name": "Dragon Roll Platter",
        "price": 28.00,
        "cuisine_type": "Sushi",
        "image_url": "https://images.unsplash.com/photo-1553621042-f6e147245754?q=80&w=800&auto=format&fit=crop",
        # Active deal
        "start_offset_hours": -1,
        "expires_offset_hours": 5,
        "is_weekly": False
    },
    {
        "item_name": "Loaded Nachos Supreme",
        "price": 11.00,
        "cuisine_type": "Mexican",
        "image_url": "https://images.unsplash.com/photo-1513456852971-30c0b8199d4d?q=80&w=800&auto=format&fit=crop",
        # Active deal
        "start_offset_hours": -2,
        "expires_offset_hours": 4,
        "is_weekly": False
    },
]

async def seed_deals():
    async with AsyncSession(engine) as session:
        # Get existing restaurant
        result = await session.execute(select(Restaurant).limit(1))
        restaurant = result.scalars().first()
        
        if not restaurant:
            print("No restaurant found. Creating one...")
            restaurant = Restaurant(
                name="Hotplate Test Kitchen",
                phone_number="+15551234567",
                zip_code="10001"
            )
            session.add(restaurant)
            await session.commit()
            
        print(f"Seeding deals for restaurant: {restaurant.name}")
        
        now = datetime.utcnow()
        current_dow = int(now.strftime("%w")) # 0=Sunday, 6=Saturday
        
        for deal_data in MOCK_DEALS:
            print(f"Generating embedding for {deal_data['item_name']}...")
            embedding = await generate_embedding(deal_data['item_name'])
            
            start_at = now + timedelta(hours=deal_data['start_offset_hours'])
            expires_at = now + timedelta(hours=deal_data['expires_offset_hours'])
            
            recurrence_day = None
            if deal_data.get('is_weekly'):
                # Calculate the DOW
                offset = deal_data.get('recurrence_day_offset', 0)
                recurrence_day = (current_dow + offset) % 7
                
            new_deal = Deal(
                id=uuid.uuid4(),
                restaurant_id=restaurant.id,
                item_name=deal_data['item_name'],
                price=deal_data['price'],
                image_url=deal_data['image_url'],
                embedding=embedding,
                start_at=start_at,
                expires_at=expires_at,
                is_weekly=deal_data['is_weekly'],
                recurrence_day=recurrence_day,
                cuisine_type=deal_data['cuisine_type']
            )
            
            session.add(new_deal)
            
        await session.commit()
        print("Successfully seeded 10 mock deals!")

if __name__ == "__main__":
    asyncio.run(seed_deals())

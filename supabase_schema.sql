-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA public;

-- Create restaurants table
CREATE TABLE IF NOT EXISTS public.restaurants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    phone_number TEXT NOT NULL UNIQUE,
    zip_code TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Create deals table
CREATE TABLE IF NOT EXISTS public.deals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    restaurant_id UUID NOT NULL REFERENCES public.restaurants(id) ON DELETE CASCADE,
    item_name TEXT NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    image_url TEXT,
    embedding vector(768),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Index on the embedding column for faster cosine distance matching
CREATE INDEX IF NOT EXISTS deals_embedding_idx ON public.deals USING hnsw (embedding vector_cosine_ops);

-- Create a PL/pgSQL function to match deals based on embedding cosine similarity
-- This returns deals ordered by similarity, optionally filtered by radius or zip if we wanted,
-- but the prompt only asked for matching deals using cosine similarity for the vectors.
CREATE OR REPLACE FUNCTION match_deals(
    query_embedding vector(768),
    match_threshold FLOAT DEFAULT 0.5,
    match_count INT DEFAULT 10
)
RETURNS TABLE (
    id UUID,
    restaurant_id UUID,
    item_name TEXT,
    price NUMERIC,
    image_url TEXT,
    expires_at TIMESTAMP WITH TIME ZONE,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        d.id,
        d.restaurant_id,
        d.item_name,
        d.price,
        d.image_url,
        d.expires_at,
        1 - (d.embedding <=> query_embedding) AS similarity
    FROM
        public.deals d
    WHERE
        1 - (d.embedding <=> query_embedding) > match_threshold
        AND d.expires_at > timezone('utc'::text, now())
    ORDER BY
        d.embedding <=> query_embedding
    LIMIT
        match_count;
END;
$$;

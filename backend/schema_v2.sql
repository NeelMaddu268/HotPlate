-- 2. Drop the old function (in case the signature changed significantly)
DROP FUNCTION IF EXISTS match_deals(vector(768), text, float, int, text, text);
DROP FUNCTION IF EXISTS match_deals(vector(768), float, int);

-- 3. Create the new match_deals function with hybrid search and visibility logic
CREATE OR REPLACE FUNCTION match_deals(
    query_embedding vector(768) DEFAULT NULL,
    search_text TEXT DEFAULT NULL,
    match_threshold FLOAT DEFAULT 0.4,
    match_count INT DEFAULT 10,
    filter_cuisine TEXT DEFAULT NULL,
    mode TEXT DEFAULT 'active',
    sort_by TEXT DEFAULT 'similarity'
)
RETURNS TABLE (
    id UUID,
    restaurant_id UUID,
    item_name TEXT,
    price NUMERIC,
    image_url TEXT,
    expires_at TIMESTAMP WITH TIME ZONE,
    start_at TIMESTAMP WITH TIME ZONE,
    is_weekly BOOLEAN,
    recurrence_day INT,
    cuisine_type TEXT,
    is_currently_active BOOLEAN,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    WITH scored_deals AS (
        SELECT
            d.id,
            d.restaurant_id,
            d.item_name,
            d.price,
            d.image_url,
            d.expires_at,
            d.start_at,
            d.is_weekly,
            d.recurrence_day,
            d.cuisine_type,
            -- Calculate if it's currently active based on timestamp and recurrence
            CASE
                WHEN d.is_weekly AND EXTRACT(DOW FROM timezone('utc'::text, now())) = d.recurrence_day THEN TRUE
                WHEN NOT d.is_weekly AND d.expires_at > timezone('utc'::text, now()) AND (d.start_at IS NULL OR d.start_at <= timezone('utc'::text, now())) THEN TRUE
                ELSE FALSE
            END AS is_currently_active,
            -- Calculate semantic similarity if embedding is provided, otherwise 1.0
            CASE
                WHEN query_embedding IS NOT NULL AND d.embedding IS NOT NULL THEN 1 - (d.embedding <=> query_embedding)
                ELSE 1.0
            END AS sim_score,
            -- Check full-text fallback
            CASE 
                WHEN search_text IS NOT NULL AND d.item_name ILIKE '%' || search_text || '%' THEN 1.0
                ELSE 0.0
            END AS text_match_score
        FROM
            public.deals d
    )
    SELECT
        sd.id,
        sd.restaurant_id,
        sd.item_name,
        sd.price,
        sd.image_url,
        sd.expires_at,
        sd.start_at,
        sd.is_weekly,
        sd.recurrence_day,
        sd.cuisine_type,
        sd.is_currently_active,
        GREATEST(sd.sim_score, sd.text_match_score) AS similarity
    FROM
        scored_deals sd
    WHERE
        -- Filter by cuisine if provided
        (filter_cuisine IS NULL OR filter_cuisine = '' OR sd.cuisine_type ILIKE filter_cuisine)
        AND
        -- Visibility logic
        (
            (mode = 'active' AND sd.is_currently_active = TRUE)
            OR
            (mode = 'all' AND (
                -- If it's weekly, it's always "upcoming" so show it
                sd.is_weekly = TRUE
                -- If it's a normal deal, only show if it expires today or in the future
                OR (sd.is_weekly = FALSE AND sd.expires_at::date >= timezone('utc'::text, now())::date)
            ))
        )
        AND
        -- Similarity threshold (only applies if we actually searched for something)
        (
            (query_embedding IS NULL AND search_text IS NULL) 
            OR 
            (GREATEST(sd.sim_score, sd.text_match_score) > match_threshold)
        )
    ORDER BY
        CASE WHEN sort_by = 'price_asc' THEN sd.price END ASC,
        CASE WHEN sort_by = 'similarity' THEN GREATEST(sd.sim_score, sd.text_match_score) END DESC
    LIMIT
        match_count;
END;
$$;

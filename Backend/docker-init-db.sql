-- Initialize PostgreSQL database with pgvector extension

-- Create pgvector extension for vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- Create trigram extension for fuzzy text search
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Optionally create PostGIS for geolocation features
-- CREATE EXTENSION IF NOT EXISTS postgis;

-- Log successful initialization
SELECT 'PostgreSQL initialized with pgvector and pg_trgm extensions' as status;

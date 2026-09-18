import psycopg
from pgvector.psycopg import register_vector
from app.config import DATABASE_URL

def get_conn():
    conn = psycopg.connect(DATABASE_URL)
    register_vector(conn)
    return conn

def init_db():
    with get_conn() as conn:
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        conn.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            source_url TEXT NOT NULL,
            organization TEXT,
            year INT,
            topic TEXT
        )
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS document_chunks (
            id SERIAL PRIMARY KEY,
            document_id INT REFERENCES documents(id) ON DELETE CASCADE,
            chunk_index INT,
            content TEXT NOT NULL,
            embedding vector(768),
            metadata JSONB DEFAULT '{}'::jsonb
        )
        """)
        conn.commit()

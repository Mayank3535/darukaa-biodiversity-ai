from pgvector.psycopg import Vector
from app.db import get_conn
from app.llm import embed

def retrieve(query: str, k: int = 5):
    vector = Vector(embed(query))
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT dc.content, d.title, d.source_url, d.organization, d.year,
                   1 - (dc.embedding <=> %s) AS similarity
            FROM document_chunks dc
            JOIN documents d ON d.id = dc.document_id
            ORDER BY dc.embedding <=> %s
            LIMIT %s
        """, (vector, vector, k)).fetchall()
    return [
        {"id": i + 1, "content": r[0], "title": r[1], "url": r[2], "organization": r[3], "year": r[4], "similarity": float(r[5])}
        for i, r in enumerate(rows)
    ]
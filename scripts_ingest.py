import json, re
from pathlib import Path
from app.db import init_db, get_conn
from app.llm import embed
from pgvector.psycopg import Vector

ROOT = Path("data/knowledge")
META_LINE = re.compile(r"^[a-zA-Z_]+:\s?.*$")

def ingest():
    init_db()
    with get_conn() as conn:
        for path in sorted(ROOT.glob("*.md")):
            meta = {}
            content = path.read_text(encoding="utf-8")
            lines = content.splitlines()

            end_of_front_matter = 0
            for i, line in enumerate(lines):
                stripped = line.strip()
                if not stripped or stripped == "---":
                    end_of_front_matter = i + 1
                    continue
                if META_LINE.match(line):
                    key, value = line.split(":", 1)
                    key, value = key.strip(), value.strip()
                    if key == "source_url":
                        meta["source_url"] = value
                    elif key == "organization":
                        meta["organization"] = value
                    elif key == "year":
                        meta["year"] = int(value)
                    elif key == "topic":
                        meta["topic"] = value
                    end_of_front_matter = i + 1
                else:
                    break

            title = path.stem.replace("_", " ").title()
            row = conn.execute("SELECT id FROM documents WHERE source_url=%s", (meta["source_url"],)).fetchone()
            if row:
                doc_id = row[0]
                conn.execute("DELETE FROM document_chunks WHERE document_id=%s", (doc_id,))
                conn.execute(
                    "UPDATE documents SET title=%s, organization=%s, year=%s, topic=%s WHERE id=%s",
                    (title, meta.get("organization"), meta.get("year"), meta.get("topic"), doc_id)
                )
            else:
                doc_id = conn.execute(
                    "INSERT INTO documents(title,source_url,organization,year,topic) VALUES(%s,%s,%s,%s,%s) RETURNING id",
                    (title, meta["source_url"], meta.get("organization"), meta.get("year"), meta.get("topic"))
                ).fetchone()[0]

            body = "\n".join(lines[end_of_front_matter:]).strip()
            print(f"{path.name}: front matter ends at line {end_of_front_matter}, body length {len(body)}")

            chunks = [body[i:i+4500] for i in range(0, len(body), 3500)]
            for idx, chunk in enumerate(chunks):
                vec = Vector(embed("document: " + chunk))
                conn.execute(
                    "INSERT INTO document_chunks(document_id,chunk_index,content,embedding,metadata) VALUES(%s,%s,%s,%s,%s)",
                    (doc_id, idx, chunk, vec, json.dumps(meta))
                )
        conn.commit()
    print("Knowledge ingestion complete.")

if __name__ == "__main__":
    ingest()
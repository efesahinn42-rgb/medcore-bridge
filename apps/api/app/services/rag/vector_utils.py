def to_pgvector_literal(embedding: list[float]) -> str:
    return "[" + ",".join(str(v) for v in embedding) + "]"

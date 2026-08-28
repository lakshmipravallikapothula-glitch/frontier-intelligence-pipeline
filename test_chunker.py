from app.extraction.chunker import chunk_text


text = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" * 1000

chunks = chunk_text(
    text,
    max_chars=12000,
    overlap=1000,
)

print("Total characters:", len(text))
print("Number of chunks:", len(chunks))

for i, chunk in enumerate(chunks, start=1):
    print(f"Chunk {i}: {len(chunk)} characters")
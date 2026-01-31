from typing import List

def chunk_text(text: str, max_chunk_size: int = 4000) -> List[str]:
    """
    Chunks text into pieces of approximately max_chunk_size.
    Attempts to split on newlines to preserve context.
    """
    if not text:
        return []

    chunks = []
    lines = text.splitlines()
    current_chunk = []
    current_size = 0

    for line in lines:
        line_size = len(line) + 1 # +1 for newline
        if current_size + line_size > max_chunk_size and current_chunk:
            chunks.append("\n".join(current_chunk))
            current_chunk = []
            current_size = 0

        current_chunk.append(line)
        current_size += line_size

        # If a single line is bigger than max_chunk_size, we just have to include it
        # or split it further if we really wanted to be strict.

    if current_chunk:
        chunks.append("\n".join(current_chunk))

    return chunks

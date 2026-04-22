"""CLI for ingesting policy PDFs into the Chroma policies collection."""

import argparse
import hashlib
import os

import chromadb
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

from chunking import split_text

EMBED_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")


def extract_pdf_text(file_path: str) -> str:
    """Extract concatenated text from a PDF file."""
    reader = PdfReader(file_path)
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)


def build_record_id(source_name: str, section: str, chunk_text: str, index: int) -> str:
    """Generate a stable Chroma record id for each chunk."""
    digest = hashlib.sha256(
        f"{source_name}|{section}|{index}|{chunk_text}".encode("utf-8")
    ).hexdigest()
    return f"{source_name}-{section}-{digest[:16]}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest a policy PDF into Chroma.")
    parser.add_argument("--file", required=True, help="Path to the source PDF file.")
    parser.add_argument(
        "--source_name",
        required=True,
        help="Logical source name to store in chunk metadata.",
    )
    parser.add_argument(
        "--section",
        required=True,
        help="Policy section label to store in chunk metadata.",
    )
    args = parser.parse_args()

    text = extract_pdf_text(args.file)
    chunks = split_text(text, chunk_size=512, overlap=0.15)

    model = SentenceTransformer(EMBED_MODEL)
    embeddings = model.encode(chunks).tolist() if chunks else []

    client = chromadb.HttpClient(
        host=os.getenv("CHROMA_HOST", "localhost"),
        port=int(os.getenv("CHROMA_PORT", "8000")),
    )
    collection = client.get_or_create_collection("policies")

    metadatas = [
        {"source": args.source_name, "section": args.section} for _ in chunks
    ]
    ids = [
        build_record_id(args.source_name, args.section, chunk, index)
        for index, chunk in enumerate(chunks)
    ]

    if chunks:
        collection.upsert(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    print(f"Ingested {len(chunks)} chunks into policies for {args.source_name}.")


if __name__ == "__main__":
    main()

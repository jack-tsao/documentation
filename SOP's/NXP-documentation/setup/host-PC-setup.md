# Host PC Setup

This guide covers setting up a host PC for generating a custom RAG database used by the eIQ GenAI Flow 2.0 demo.

---

# Overview

The host PC is responsible for:

- Installing the eIQ GenAI Flow project
- Parsing PDF documents
- Splitting documents into chunks
- Generating embeddings
- Creating the RAG database

The finished `rag_database.pkl` is then copied to the i.MX95 board.

---

# Prerequisites

- Ubuntu Linux x86
- NVIDIA GPU
- Python 3.11
- Internet connection
- Hugging Face account

---

# Install UV

UV is used instead of pip because it installs packages much faster.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
```

---

# Clone the Repository

```bash
git clone --single-branch -b release/v2.0 \
https://github.com/nxp-appcodehub/dm-eiq-genai-flow-demonstrator
```

---

# Create the Python Environment

```bash
cd dm-eiq-genai-flow-demonstrator/rag

uv venv --python 3.11

uv pip install -e .[dev]

uv pip install flash-attn --no-build-isolation
```

---

# Configure Hugging Face

Some embedding models require authentication.

Create a Hugging Face account.

Generate a **Read Access Token**.

Export it:

```bash
export HF_TOKEN="your_token_here"
```

---

# Prepare Documents

Copy all PDF files into

```
rag/src/data/input_files/
```

Example

```
input_files/
    Medical.pdf
    UserManual.pdf
```

---

# Parse PDF Files

Convert PDFs into structured text.

```bash
uv run -m document_parsing
```

---

# Generate Text Chunks

Split large documents into smaller sections.

```bash
uv run -m rag.preprocessing.generate_chunks
```

---

# Generate Embeddings

Convert every chunk into an embedding vector.

```bash
uv run -m rag.preprocessing.generate_embeddings
```

This generates

```
rag_database.pkl
```

---

# Copy Database to the Board

Copy

```
rag_database.pkl
```

to

```
dm-eiq-genai-flow-demonstrator/
    rag/
        src/
            data/
```

on the i.MX95 board.

The specifics of this process are discussed in ```imx95-board-setup.md```

---

# Workflow Summary

```
PDF

↓

document_parsing

↓

generate_chunks

↓

generate_embeddings

↓

rag_database.pkl

↓

Copy to i.MX95
```

---

# Notes

- Regenerate the database whenever PDFs are added or modified.
- The host PC is only needed for database generation.
- The i.MX95 board performs retrieval and inference using the generated database.

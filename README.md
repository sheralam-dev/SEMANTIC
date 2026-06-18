## SEMANTIC — Local Semantic Search (v1.0)

Lightweight local semantic search desktop app that indexes files, builds vector embeddings, and provides fast similarity search using an embedded SQLite vector store.

Key goals:
- Search local files by meaning, not just keywords
- Operate fully offline with a small footprint
- Easy developer-first codebase for experimentation

---

**Quick install**

```bash
pip install -r requirements.txt
```

**Run**

```bash
python run.py
```

**CLI options**

- `--reindex`    Rebuilds the SQLite index from scratch
- `--no-watch`   Disable live filesystem watcher
- `--debug`      Enable verbose logging

---

Requirements (see `requirements.txt`):

- `sqlite-vec`, `watchdog`, `numpy`, `PySide6`, `onnxruntime`

---

Configuration

- Default paths and extensions can be adjusted in `run.py` or the relevant config helpers in `app/`.
- Models are expected under the `models/` folder or loaded via the embedding adapter in `app/search/embedding_model_onnx.py`.

---

Project layout

```
run.py                 # Entry point (CLI + UI launch)
test.py                # Quick test harness
app/
  ├─ indexing/         # scanner.py (batch), watcher.py (live)
  ├─ search/           # embedding model adapter, search logic
  ├─ storage/          # db.py, repository layer
  └─ ui/               # window.py, results_view, custom elements
models/                # local model snapshots (optional)
data/                  # indexed file metadata and auxiliary data
```

---

How it works (high level)

1. Scanner discovers files and extracts metadata
2. Embedding model converts text to vector
3. Vectors and metadata are stored in SQLite (`sqlite-vec`)
4. UI sends queries → embedding → nearest-neighbor lookup

---

Development notes

- Embedding dimension and model choice are pluggable via `app/search/embedding_model_onnx.py`.
- Background scanning runs in a worker thread so the UI remains responsive.
- Use `--reindex` during development when changing indexing logic.

---

License

MIT

---
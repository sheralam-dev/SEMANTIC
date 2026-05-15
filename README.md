## SEMANTIC - A Semantic Search Desktop App (v0.1)

Local desktop application for **semantic file search** using vector embeddings and SQLite.

---

### Features

* Semantic search using `BAAI/bge-base-en-v1.5`
* SQLite-based storage (no external services)
* Background indexing (non-blocking UI)
* Optional live file watcher
* Grid + Detail views
* Fast local search (~10k files optimized)

---

### Tech Stack

* UI: PyQt
* Embeddings: `BAAI/bge-base-en-v1.5` from Beijing Academy of Artificial Intelligence
* Database: SQLite
* Language: Python

---

### Installation

```bash
pip install -r requirements.txt
```

---

### Usage

Run the app:

```bash
python run.py
```

---

### CLI Options

```bash
python run.py [options]
```

* `--reindex`
  Drops existing tables and rebuilds the index

* `--no-watch`
  Disables live file system watcher

* `--debug`
  Enables verbose logging

---

### Default Configuration

```python
default_paths = ["D:\\Videos\\AI Development"]
default_extensions = {"mp4", "pdf"}
```

Modify in `run.py` as needed.

---

### How It Works

**Startup Flow**

1. Parse CLI arguments
2. Initialize SQLite DB

   * Rebuild if `--reindex`
3. Launch UI (`SearchApp`)
4. Start background scan thread

**Indexing**

```
File → Metadata → Embedding → SQLite
```

**Search**

```
Query → Embedding → Vector similarity → Top results
```

---

### Architecture

```
run.py                # Entry point (CLI + boot)
app/
 ├── storage/
 │   └── db.py        # SQLite init
 │
 ├── indexing/
 │   ├── scanner.py   # Batch indexing
 │   └── watcher.py   # Live FS monitor
 │
 ├── repository/
 │   └── search       # Similarity queries
 │
 └── ui/
     └── window.py    # Main app (SearchApp)
```

---

### Core Components

* **ScanWorker (QThread)**

  * Loads model
  * Runs batch scan
  * Emits completion signal

* **SearchApp**

  * UI + lifecycle manager
  * Handles threading + watcher

* **SQLite DB**

  * Stores file records + embeddings (768-dim)

---

### Notes

* First run is slower (model load + indexing)
* Subsequent searches are instant
* Works fully offline
* Designed for local file systems

---

### Future Improvements

* Incremental indexing
* Hybrid search (keyword + vector)
* GPU support
* File preview panel
* Cross-platform enhancements

---

### License

MIT (or specify)

## Project Implementation — Deskripsi Implementasi (nyata)

Tujuan
- Dokumen ini menjelaskan implementasi berdasarkan kode yang ada di repo. Fokus pada arsitektur, pemetaan file, endpoint HTTP yang tersedia, variabel environment, cara menjalankan dan catatan perilaku (tanpa berandai-andai).

Ringkasan arsitektur
- Aplikasi dibangun dengan FastAPI dan terbagi menjadi: Controller (HTTP), Service (business logic), Tools, Config, Router, dan Kernel.

Pemetaan file kunci
- `main.py`: entrypoint — memanggil `uvicorn.run(app, host="0.0.0.0", port=8000)`.
- `app/Kernel.py`: factory FastAPI, lifespan startup (inisialisasi Qdrant) dan pendaftaran router.
- `app/router/api/v1.py`: definisi endpoint API (`/ask`, `/add`, `/status`).
- `app/controllers/RagWorkflowController.py`: controller untuk alur RAG (membangun graph dan mengeksekusi workflow).
- `app/controllers/DocumentStoringController.py`: controller untuk menambah dokumen & cek status storage.
- `app/services/RagWorkflowService.py`: implementasi logic node RAG (retrieve, answer).
- `app/services/EmbeddingService.py`: manager embedding (saat ini menghasilkan embedding tiruan/fake).
- `app/tools/DocumentStoringTool.py`: wrapper storage—menggunakan Qdrant bila terhubung, atau fallback in-memory.
- `app/config/setting.py`: konfigurasi aplikasi melalui `.env` (variabel yang diperlukan tercantum di bawah).
- `app/config/qdrant.py`: wrapper Qdrant (`QdrantDB`) untuk index/search.
- `app/schemas/*.py`: pydantic schema untuk request/response (mis. `QuestionRequest`, `DocumentRequest`, `AskResponse`, `AddDocumentResponse`).

Endpoint HTTP (yang tersedia sekarang)
- `POST /ask`
  - Request: `{"question": "..."}` (schema: `QuestionRequest`).
  - Response: `AskResponse` {`question`, `answer`, `context_used`, `latency_sec`}.
  - Flow: controller menjalankan graph yang didefinisikan di `RagWorkflowController` — node `retrieve` memanggil `StorageTool.search`, node `answer` memanggil generator LLM internal (saat ini _simulasi_).

- `POST /add`
  - Request: `{"text": "..."}` (schema: `DocumentRequest`).
  - Response: `AddDocumentResponse` {`id`, `status`}.
  - Flow: menambahkan dokumen ke memori lokal dan juga meng-index ke Qdrant jika koneksi Qdrant tersedia.

- `GET /status`
  - Response: status storage (dari `StorageTool.get_status`) ditambah `graph_ready` yang menunjukkan apakah workflow graph sudah siap.

Variabel environment yang wajib/berguna (ada di `app/config/setting.py`)
- `APP_NAME` — nama aplikasi.
- `APP_VERSION` — versi aplikasi.
- `QDRANT_URL` — URL Qdrant (mis. `http://qdrant:6333` atau `http://localhost:6333`).
- `QDRANT_COLLECTION_NAME` — nama koleksi vektor yang dipakai.
- `VECTOR_SIZE` — panjang vektor embedding (integer).

- Qdrant:
  - `app/config/qdrant.QdrantDB` mencoba membuat client `QdrantClient(url=settings.QDRANT_URL)` pada inisialisasi. Jika gagal, client diset `None` dan aplikasi tetap jalan menggunakan fallback memory.
  - `DocumentStoringTool` akan memanggil `qdrant_db.create_collection(..., force_recreate=True)` pada inisialisasi jika Qdrant tersedia.

- Embedding:
  - `app/services/EmbeddingService.EmbeddingManager.fake_embed` saat ini menghasilkan embedding tiruan deterministik (digunakan oleh Qdrant wrapper saat indexing/search).

- Workflow RAG:
  - `RagWorkflowController` menyusun sebuah `StateGraph` (dari `langgraph`) dengan node `retrieve` dan `answer`. Detail logic node ada di `RagWorkflowService`.
  - `RagWorkflowService.retrieve_node` memakai `StorageTool.search(query)` dan menyimpan hasil ke state `context`.
  - `RagWorkflowService.answer_node` memanggil `_call_llm_generation` yang saat ini hanya mensimulasikan respons berbasis teks pertama dari context.

- Fallback in-memory:
  - Jika Qdrant tidak tersedia, `DocumentStoringTool` menyimpan dokumen di `self.docs_memory` dan melakukan pencarian teks sederhana (`in` pada lowercase).

Cara menjalankan (lokal)
1. Buat file `.env` di root berisi variabel yang diperlukan (minimal contoh):

```
APP_NAME=technical_test
APP_VERSION=0.1.0
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION_NAME=docs
VECTOR_SIZE=128
```

2. Install dependencies (direferensikan di `requirements.txt`):

```bash
python3 -m pip install -r requirements.txt
```

3. Jalankan aplikasi:

```bash
python3 main.py
```

Atau langsung dengan uvicorn (mengambil `app` dari `app.Kernel`):

```bash
uvicorn app.Kernel:app --host 0.0.0.0 --port 8000
```

Docker
- Repo berisi `Dockerfile` dan `docker-compose.yaml` — untuk deploy cepat, jalankan:

```bash
docker-compose up --build -d
```

Catatan pengujian manual (quick checks)
- Tambah dokumen:

```bash
curl -X POST "http://localhost:8000/add" -H "Content-Type: application/json" -d '{"text":"Indonesia Merdeka"}'
```

- Tanyakan sesuatu:

```bash
curl -X POST "http://localhost:8000/ask" -H "Content-Type: application/json" -d '{"question":"Apakah Indonesia Merdeka?"}'
```

- Cek status:

```bash
curl "http://localhost:8000/status"
```

Dependencies utama
- Terlihat di `requirements.txt`: `fastapi`, `uvicorn`, `pydantic`, `langgraph`, `qdrant-client`.


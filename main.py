import uvicorn
from app.Kernel import app

if __name__ == "__main__":
    # Menjalankan server uvicorn
    # Host 0.0.0.0 agar bisa diakses dari luar container (jika didockerize)
    uvicorn.run(app, host="0.0.0.0", port=8000)
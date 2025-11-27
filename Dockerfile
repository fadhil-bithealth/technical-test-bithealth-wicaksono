# Gunakan image Python yang ringan
FROM python:3.10-slim

# Set working directory di dalam container
WORKDIR /app

# Copy requirements terlebih dahulu agar caching layer docker optimal
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy seluruh kode aplikasi ke dalam container
COPY . .

# Expose port 8000 (port default uvicorn)
EXPOSE 8000

# Perintah untuk menjalankan aplikasi saat container start
# Host 0.0.0.0 penting agar bisa diakses dari luar container
CMD ["python", "main.py"]
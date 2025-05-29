# Použití oficiálního Python image jako základu
FROM python:3.11-slim

# Nastavení pracovního adresáře v kontejneru
WORKDIR /app

# Kopírování souborů requirements a instalace závislostí
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopírování zbytku aplikace do kontejneru
COPY . .

# Expose port
EXPOSE 8004

# Spuštění aplikace při startu kontejneru
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8004"]

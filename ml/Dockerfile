FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /work
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
EXPOSE 8888
# Jupyter Lab şifresiz açılır (sadece yerel geliştirme için): http://localhost:8888
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--ServerApp.token=", "--ServerApp.password="]

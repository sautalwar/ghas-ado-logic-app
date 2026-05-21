FROM python:3.9.18-bullseye

LABEL org.opencontainers.image.title="ghas-ado-logic-app container scanning demo"
LABEL org.opencontainers.image.description="Demo image with intentionally outdated packages so GitHub code scanning can surface container findings."

WORKDIR /app

COPY container-demo/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY container-demo/index.html ./index.html

EXPOSE 8000

CMD ["python", "-m", "http.server", "8000"]

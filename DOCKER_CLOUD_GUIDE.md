# Python API - Docker & Moln Deployment Guide

## Lokal utveckling med Docker

### Starta Python API i Docker:
```powershell
.\start-python-api-docker.ps1
```

### Eller manuellt:
```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d python-service
```

### Se loggar:
```powershell
docker logs -f genassista-python-python-service-1
```

### Stoppa:
```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml down python-service
```

## Moln Deployment

### För Azure Container Instances / Azure App Service:

1. **Bygg Docker image:**
```bash
docker build -t genassista-python-api:latest .
```

2. **Push till Azure Container Registry:**
```bash
az acr login --name <your-registry>
docker tag genassista-python-api:latest <your-registry>.azurecr.io/genassista-python-api:latest
docker push <your-registry>.azurecr.io/genassista-python-api:latest
```

3. **Miljövariabler för molnet:**
- `PORT=8001` (eller den port som molntjänsten använder)
- `GROQ_API_KEY=<din-groq-key>` (sätt som secret i Azure Key Vault)
- `LLM_BASE_URL=https://api.groq.com/openai/v1`
- `LLM_MODEL=llama-3.3-70b-versatile`
- `PYTHON_API_KEY=<din-api-key>` (för autentisering)
- `DATABASE_URL=<postgres-connection-string>` (om behövs)

### För Docker Compose i molnet:

Använd `docker-compose.prod.yml` som bas och lägg till:
- Secrets management (Azure Key Vault, AWS Secrets Manager)
- Load balancer konfiguration
- Health checks
- Auto-scaling

### Viktiga punkter för moln:

1. **Secrets:** Använd alltid secrets management (inte hårdkodade API keys)
2. **Health checks:** Docker healthcheck är redan konfigurerad
3. **Port:** Använd miljövariabel `PORT` (redan implementerat)
4. **Logging:** Konfigurera centraliserad logging (Loki/Grafana redan i docker-compose.dev.yml)
5. **Monitoring:** Lägg till monitoring (Application Insights, CloudWatch, etc.)

## Felsökning

### Containern startar om hela tiden:
1. Kolla loggar: `docker logs genassista-python-python-service-1`
2. Kontrollera att alla miljövariabler är satta
3. Kontrollera att RabbitMQ är healthy (eller sätt ENABLE_SUBSCRIBER=false)

### Port-problem:
- Kontrollera att `PORT` miljövariabel är satt
- Kontrollera port-mappning i docker-compose.yml

### API key problem:
- Kontrollera att `GROQ_API_KEY` är satt
- Kontrollera att modellen `llama-3.3-70b-versatile` är korrekt

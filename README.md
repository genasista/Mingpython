# Genassista EDU Python API

**Genassista-EDU Python API** är en mikrotjänst som integrerar med backend för att hantera utbildningsdata enligt Gy11 (svensk läroplan). Tjänsten stöder ENGENG05 (Engelska 5) och följer Skolverkets krav.

## 🎯 Funktioner

### AI/ML Core Services
- **AI Analysis** - Omfattande analys av elevarbeten med AI
- **Feedback Generation** - Automatisk feedback för lärare, elever och föräldrar
- **Document Processing** - PDF, Word och bilder (OCR för handskrift)
- **Grade Suggestions** - AI-driven betygsförslag enligt Skolverkets E/C/A-kriterier
- **Quiz & Flashcard Generator** - Generera quiz och flashcards för elever
- **Adaptive Learning Paths** - Personliga lärandevägar
- **Study Recommendations** - Studie-tips baserat på elevprestanda

### Core API Integration
- **Fullständig backend-integration** via Core API (port 3001)
- **Unified endpoints** för kurser, elever, skolor, uppgifter, betyg
- **Autentisering** via X-API-KEY och JWT-tokens
- **CORS-stöd** för frontend-integration

### Event-Driven Architecture
- **RabbitMQ-subscriber** för realtidshändelser
- **Durable queues** med offline-replay
- **CorrelationId** för spårbarhet
- **Automatisk återanslutning** vid nätverksfel

### Data Management
- **ENGENG05 generator** för deterministisk testdata
- **CSV-export** med FK-validering
- **Core seeding** via API (ingen direkt DB-access)
- **Gy11-kompatibel** datastruktur

### Monitoring & Logging
- **Structured logging** med correlationId och dataMode
- **Loki integration** för centraliserad logghantering
- **Grafana dashboards** för övervakning
- **Health checks** för tjänstestatus

---

## 🚀 Snabbstart

### 1. Miljövariabler
Skapa `.env` fil:
```env
# Service Configuration
SERVICE_NAME=Genassista-EDU-pythonAPI
SERVICE_VERSION=0.1.0
LOG_LEVEL=INFO

# API Security (MÅSTE ÄNDRAS!)
PYTHON_API_KEY=your-secret-api-key-here
OPENAI_API_KEY=your-openai-api-key-here

# Backend Integration
CORE_BASE_URL=http://localhost:3001

# Storage Configuration
STORAGE_PROVIDER=local  # 'local' eller 'azure'

# Feature Flags
SANDBOX_MODE=true
ENABLE_SUBSCRIBER=false

# RabbitMQ Configuration (om ENABLE_SUBSCRIBER=true)
AMQP_URL=amqp://guest:guest@localhost:5672/
SUBSCRIBER_EXCHANGE=events
EVENT_SUBMISSION_CREATED=submission.created
SUBSCRIBER_QUEUE=submission.created

# Legacy/Deprecated
API_KEY=ADD-X-API-KEY
ADMIN_TOKEN=

# CORS Configuration
CORS_ORIGIN=http://localhost:3000
```

**Viktigt:** Ändra `PYTHON_API_KEY` till ett säkert värde! Detta är nyckeln som backend använder för att anropa Python API.

### 2. Starta systemet
```bash
# Dev-stack: Python API + RabbitMQ + Loki/Grafana
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build

# Prod-lik stack (extern observability, secrets via ./secrets/*)
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Kontrollera status
docker compose ps
```

### 3. Verifiera funktionalitet
```bash
# Health check
curl http://localhost:8000/api/version1/health

# Swagger UI
open http://localhost:8000/docs
```

### 4. Konfigurera port för lokal utveckling
När flera utvecklare jobbar samtidigt kan ni använda olika portar för att undvika konflikter:

```bash
# Använd port 8001 för din lokala utveckling (kollegan använder 8000)
export PORT=8001
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# API:n är nu tillgänglig på:
curl http://localhost:8001/api/version1/health
open http://localhost:8001/docs
```

**Notera:**
- `docker-compose.dev.yml` sätter default PORT till `8001` för lokal utveckling
- `docker-compose.yml` använder `8000` som default (för prod-lik miljö)
- Du kan override med miljövariabeln `PORT` innan du kör `docker compose up`
- **Viktigt för backend-integration:** Backend måste konfigurera `PYTHON_API_URL` i sin `.env` för att matcha porten:
  ```env
  # Om du använder port 8001 (dev-compose):
  PYTHON_API_URL=http://localhost:8001/api/version1
  
  # Om du använder port 8000 (standard):
  PYTHON_API_URL=http://localhost:8000/api/version1
  ```
- Se `INTEGRATION_GUIDE.md` för detaljerad integration-dokumentation

---

## 🔐 Secrets & miljöhantering

- `docker-compose.yml` håller gemensamma tjänster (FastAPI + RabbitMQ). Lägg till:
  - `docker-compose.dev.yml` för lokalt arbete med Loki/Grafana och `.env`.
  - `docker-compose.prod.yml` för prod-lik miljö där hemligheter injiceras via Docker secrets och port-forwarding stängs av.
- Lägg känsliga värden i filer under `./secrets` (mappen är ignored):
  ```
  secrets/
  ├── python_api_key     # PYTHON_API_KEY
  ├── openai_api_key     # OPENAI_API_KEY
  ├── admin_token        # ADMIN_TOKEN
  └── api_key            # API_KEY (legacy)
  ```
- Entrypoint-scriptet `docker/entrypoint.sh` läser automatiskt in filerna ovan (om de finns) och exporterar miljövariablerna innan `uvicorn` startas. Dev-miljön fortsätter använda `.env`.

---

## 📦 Låsta beroenden & multi-stage build

- `requirements.lock` är källan för Docker-builds (`pip-compile requirements.txt --generate-hashes --output-file requirements.lock`).
- Builder-steget installerar allt i `/opt/venv` och återanvänder pip-cache per layer (BuildKit). Runtime-staget återanvänder bara venv + app-koden ⇒ mindre image och inga dev-verktyg i produktion.
- Uppdatera beroenden:
  ```bash
  pip-compile requirements.txt --generate-hashes --output-file requirements.lock
  docker compose build python-service
  ```
- Prod-compose använder `expose` i stället för `ports` så att lastbalanserare/molntjänster kan terminera trafik utan att exponera port 8000 på värden.

---

## 📊 API Endpoints

### Health & Status
| Endpoint | Beskrivning |
|----------|-------------|
| `GET /api/version1/health` | Hälsokontroll för API |

### Assignment Processing (`/api/version1/assignments/process/`)
| Endpoint | Beskrivning |
|----------|-------------|
| `POST /submit` | Ladda upp uppgift (Word, PDF, bild) |
| `POST /analyze` | Analysera elevuppgift med AI |
| `POST /batch-analyze` | Batch-analys av flera uppgifter |
| `POST /generate-exercise` | Generera individuell övning |
| `POST /generate-quiz` | Generera quiz |
| `POST /generate-flashcards` | Generera flashcards |
| `POST /generate-learning-path` | Generera adaptiv lärandeväg |
| `POST /generate-study-recommendations` | Generera studie-tips |
| `POST /generate-template` | Generera uppgiftsmall |

### Handwriting Processing (`/api/version1/handwriting/`)
| Endpoint | Beskrivning |
|----------|-------------|
| `POST /process` | OCR och AI-analys av handskrift |
| `POST /simple` | Enkel OCR (endast text) |

### Exam Processing (`/api/version1/exams/`)
| Endpoint | Beskrivning |
|----------|-------------|
| `POST /analyze-submission` | Analysera provinlämning |
| `POST /generate-questions` | Generera provfrågor |

### Teaching Materials (`/api/version1/teaching/`)
| Endpoint | Beskrivning |
|----------|-------------|
| `POST /generate-lesson` | Generera lektionsplan |
| `POST /generate-materials` | Generera undervisningsmaterial |
| `POST /process-document` | Bearbeta undervisningsdokument |

### Materials Management (`/api/version1/materials/`)
| Endpoint | Beskrivning |
|----------|-------------|
| `POST /process` | Bearbeta uppladdat material |
| `GET /{material_id}/preview` | Förhandsvisning av material |

### Feedback (`/api/version1/feedback/`)
| Endpoint | Beskrivning |
|----------|-------------|
| `POST /generate` | Generera feedback för lärare/elev/förälder |

### Student Services (`/api/version1/student/`)
| Endpoint | Beskrivning |
|----------|-------------|
| `POST /{student_id}/progress` | Generera progress tracking data |

### RAG System (`/api/version1/rag/`)
| Endpoint | Beskrivning |
|----------|-------------|
| `POST /documents/upload` | Ladda upp dokument |
| `POST /documents/analyze` | Analysera dokument |
| `POST /documents/analyze-text` | Analysera text direkt |
| `GET /documents/search` | Sök dokument |
| `GET /knowledge/search` | Sök kunskapsbas |
| `GET /documents/stats` | Databasstatistik |

### Studera.ai Integration (`/api/version1/studera-ai/`)
| Endpoint | Beskrivning |
|----------|-------------|
| `GET /images` | Hämta bilder från studera.ai |
| `GET /images/{image_id}` | Hämta specifik bild |

**Autentisering:** Alla endpoints kräver `X-API-KEY` header (utom `/health`)

---

## 🏗️ Sprint 3: ENGENG05 Data Generator

### Generera testdata
```bash
# Skapa ENGENG05 dataset (≥2 kommuner, ≥6 skolor, ≥20 klasser)
python script/generate_engeng05.py --seed 42 --output script/output \
  --municipalities 2 --schools 6 --class-groups 20 --teachers 8 --students 200

# Ladda data till backend via Core API
python script/load_seed_via_core.py script/output
```

### Validering
- **FK-validering** säkerställer dataintegritet
- **Deterministisk** output med samma seed
- **Gy11-kompatibel** struktur för ENGENG05
- **Körningstid** < 5 minuter

---

## 📝 Sprint 4: Synthetic Essay Library (SCRUM-23)

### Generera 200 ENG5-uppsatser
```bash
# Skapa syntetiska essays med Skolverkets kriterier
python script/generate_eng5_essays.py --num-essays 200 --output script/output/essays

# Utvärdera baseline-metoder
python script/baseline_evaluation.py --method heuristic --detailed
python script/baseline_evaluation.py --method advanced --detailed
```

### Essay Library Features
- **200 syntetiska ENG5-uppsatser** med metadata
- **Gold E/C/A-taggar** baserat på Skolverkets kriterier
- **Feedback-system** som hjälper elever förbättra
- **Baseline evaluation** för AI-modellutveckling

### API Endpoints för Essays
| Endpoint | Beskrivning |
|----------|-------------|
| `GET /api/version1/feedback/essays` | Lista essays med filtering |
| `GET /api/version1/feedback/essays/{id}` | Hämta specifik essay |
| `GET /api/version1/feedback/essays/{id}/feedback` | Hämta feedback |
| `POST /api/version1/feedback/essays/evaluate` | Utvärdera custom essay |
| `GET /api/version1/feedback/essays/stats` | Statistik över biblioteket |

---

## 🧠 RAG System (Retrieval-Augmented Generation)

### Dokumenthantering
- **PDF/Word/OCR** - Ladda upp och bearbeta olika filformat
- **Handskrift** - OCR för handskrivna uppgifter
- **Vector Database** - ChromaDB för semantisk sökning
- **Embeddings** - OpenAI text-embedding-ada-002

### Skolverket Knowledge Base
```bash
# Ladda Skolverkets kunskapsbas (47 kunskapsbaser)
python script/load_skolverket_knowledge.py

# Testa kunskapsbasen (utan ChromaDB)
python script/test_knowledge.py
python script/test_skolverket_standalone.py

# Testa RAG-systemet
python script/test_rag_system.py
```

### RAG API Endpoints
Se "RAG System" ovan för komplett lista.

---

## 🤖 AI Analysis System

### Komplett AI-analys
- **Omfattande analys** av elevarbeten med AI
- **Skolverkets kriterier** - E/C/A bedömning enligt Gy11
- **Språklig analys** - Ordförråd, grammatik, stil
- **Kritiskt tänkande** - Analys av argumentation och logik
- **Kreativitet** - Bedömning av originalitet och uttryck

### Feedback-system
- **Lärare-feedback** - Professionell pedagogisk analys
- **Elev-feedback** - Uppmuntrande och konstruktiv återkoppling
- **Föräldra-feedback** - Informativ och stödjande
- **Peer-feedback** - Riktlinjer för kamratbedömning
- **Självreflektion** - Frågor för egen utveckling

### AI API Endpoints
Se "Assignment Processing", "Exam Processing", "Teaching Materials" och "Feedback" ovan för komplett lista.

---

## 🐰 RabbitMQ Events

### Skicka testmeddelande
```bash
# Via RabbitMQ Management UI (http://localhost:15672)
# Exchange: events, Routing Key: submission.created

# Eller via curl
curl -X POST http://localhost:15672/api/exchanges/%2F/events/publish \
  -H "Content-Type: application/json" \
  -d '{
    "routing_key": "submission.created",
    "payload": "{\"submissionId\":\"demo-1\",\"eventId\":\"evt-1\"}",
    "properties": {}
  }'
```

### Testa offline-replay
```bash
# Stoppa tjänsten
docker compose stop python-service

# Skicka meddelanden medan den är nere
# (via RabbitMQ UI eller curl)

# Starta tjänsten igen
docker compose start python-service

# Meddelanden levereras automatiskt
```

---

## 📈 Monitoring

### Grafana (http://localhost:3002)
- **Logga in:** admin/admin
- **Explore → Loki**
- **Query:** `{service="Genassista-EDU-pythonAPI"} | logfmt`

### Loggformat
```
timestamp service correlationId dataMode method path status duration_ms
```

### Viktiga loggar
- `received submissionId=... acked` - Lyckad event-hantering
- `CORE /admin/seed failed` - Backend-integration fel
- `RabbitMQ connect failed` - Event-koppling problem

---

## 🏗️ Systemarkitektur

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │  Python API     │    │   Backend       │
│   (Port 3000)   │◄──►│  (Port 8000)    │◄──►│  (Port 3001)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   RabbitMQ      │
                       │  (Port 5672)    │
                       └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  Loki + Grafana │
                       │ (3100 + 3002)   │
                       └─────────────────┘
```

---

## 🛠️ Utveckling

### Projektstruktur
```
app/
├── api/version1/endpoints/    # API endpoints
├── core/                      # Konfiguration & middleware
├── schemas/                   # Pydantic schemas
├── entities/                  # Datamodeller
└── servies/                   # Business logic

script/
├── generate_engeng05.py       # Data generator
├── generate_eng5_essays.py    # Essay library generator
├── baseline_evaluation.py     # Evaluation tool
├── load_seed_via_core.py      # Core loader
├── load_skolverket_knowledge.py  # Skolverket knowledge base
├── test_knowledge.py          # Test knowledge base
├── test_skolverket_standalone.py  # Standalone test
├── test_rag_system.py         # RAG system test
└── test_complete_system.py    # Complete system test
```

### Lokal utveckling
```bash
# Installera dependencies
pip install -r requirements.txt

# Kör lokalt (utan Docker)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🧪 Testning

### API-tester
```bash
# Health check (ingen API key behövs)
curl http://localhost:8000/api/version1/health

# Analysera elevuppgift (kräver API key)
curl -X POST http://localhost:8000/api/version1/assignments/process/analyze \
  -H "X-API-KEY: your-secret-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "This is a test essay about literature...",
    "assignment_id": "test_123",
    "student_id": "student_456",
    "subject": "engelska",
    "level": "5"
  }'

# Testa handskrift OCR
curl -X POST http://localhost:8000/api/version1/handwriting/process \
  -H "X-API-KEY: your-secret-api-key-here" \
  -F "file=@handwriting_image.jpg" \
  -F "assignment_id=test_123" \
  -F "student_id=student_456"
```

### Event-tester
```bash
# Skicka event
python -c "
import asyncio
from app.subscriber import Subscriber
async def test():
    sub = Subscriber()
    await sub.run()
asyncio.run(test())
"
```

---

## 🚨 Felsökning

### Vanliga problem

**Backend inte tillgänglig:**
```bash
# Kontrollera att backend körs på port 3001
curl http://localhost:3001/health
```

**RabbitMQ-koppling misslyckas:**
```bash
# Kontrollera RabbitMQ status
docker compose logs rabbit
```

**CSV-generering fungerar inte:**
```bash
# Kontrollera Python-script
python script/generate_engeng05.py --help
```

### Loggar
```bash
# Visa alla loggar
docker compose logs python-service

# Följ loggar i realtid
docker compose logs -f python-service
```

---

## 📋 Snabbkommandon

| Beskrivning | Kommando |
|-------------|----------|
| Starta allt | `docker compose up -d --build` |
| Status | `docker compose ps` |
| Loggar | `docker compose logs python-service` |
| Stoppa allt | `docker compose down` |
| Swagger UI | http://localhost:8000/docs |
| Grafana | http://localhost:3002 |
| RabbitMQ UI | http://localhost:15672 |

---

## ✅ Acceptance Criteria

### Sprint 1-2 (Klar)
- ✅ FastAPI med health endpoint
- ✅ RabbitMQ-subscriber med durable queues
- ✅ Loki/Grafana integration
- ✅ Offline-replay fungerar

### Sprint 3 (Klar)
- ✅ ENGENG05 generator (≥2 kommuner, ≥6 skolor, ≥20 klasser)
- ✅ CSV-export med FK-validering
- ✅ Core seeding via API (ingen direkt DB)
- ✅ Deterministisk körning < 5 min

### Backend Integration (Klar)
- ✅ Fullständig API-proxy till backend
- ✅ X-API-KEY autentisering
- ✅ CORS-stöd för frontend
- ✅ Structured logging med correlationId

---

## 🎓 Gy11 Compliance

Systemet följer Skolverkets Gy11 för:
- **Engelska 5** (ENGENG05) kursstruktur
- **Kunskapskrav** och centralt innehåll
- **Bedömningskriterier** för gymnasiet
- **Läroplanens mål** och progression

---

*Genassista EDU Python API v0.1.0 - Byggd för svensk utbildning enligt Gy11*
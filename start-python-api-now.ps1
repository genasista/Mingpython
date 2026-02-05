cd "C:\Users\Admin\Desktop\Genassista EDU\PythonAPI"
$env:KMP_DUPLICATE_LIB_OK = "TRUE"
$env:PORT = "8001"
$env:GROQ_API_KEY = "your_api_key_here"
$env:LLM_BASE_URL = "https://api.groq.com/openai/v1"
$env:LLM_MODEL = "llama-3.1-70b-versatile"
Write-Host "=== PYTHON API STARTAR ===" -ForegroundColor Green
Write-Host "Port: $env:PORT" -ForegroundColor Cyan
Write-Host "Groq API: Konfigurerad" -ForegroundColor Cyan
Write-Host "LLM Base URL: $env:LLM_BASE_URL" -ForegroundColor Cyan
Write-Host "LLM Model: $env:LLM_MODEL" -ForegroundColor Cyan
Write-Host ""
Write-Host "Vänta på 'Application startup complete'..." -ForegroundColor Yellow
Write-Host ""
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001

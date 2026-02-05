# 📋 Detaljerad Sprint Plan - Sprint 4-6

## 🎯 **Översikt: Mycket Detaljerad Plan, Enkel Implementation**

### **Mål:**
- ✅ **Mycket detaljerad plan** - Varje uppgift har tydliga steg och acceptance criteria
- ✅ **Lätt att använda** - Varje uppgift är enkel att implementera (low code)
- ✅ **Tydlig prioritering** - Vad ska göras först, vad kan vänta

---

## 🚀 **SPRINT 4: Backend Foundation + Teacher Portal (Backend)**

### **Datum:** 10 november - 21 november (2 veckor)

### **Totalt:** 9 uppgifter

---

### **BACKEND UPPGIFTER (5 uppgifter)**

#### **SCRUM-26: Backend - Assignment Management (CRUD)**

**Beskrivning:** Som backend vill jag ha CRUD-endpoints för assignments.

**Varför:** Lärare behöver kunna skapa, läsa, uppdatera och ta bort uppgifter.

**Detaljerade Steg:**
1. **Skapa databas-schema** (30 min)
   - Tabell: `assignments`
   - Fält: `id`, `title`, `description`, `type`, `deadline`, `teacher_id`, `course_id`, `class_id`, `created_at`, `updated_at`, `deleted_at`
   - Index: `teacher_id`, `class_id`, `course_id`, `deadline`

2. **Implementera POST /api/assignments** (1 timme)
   - Validera input (title, description, deadline)
   - Validera att lärare finns
   - Spara i databas
   - Returnera 201 med assignment object

3. **Implementera GET /api/assignments** (1 timme)
   - Filtrera per `teacher_id` (required)
   - Filtrera per `class_id` (optional)
   - Filtrera per `type` (optional)
   - Paginering (page, limit)
   - Returnera 200 med lista

4. **Implementera GET /api/assignments/:id** (30 min)
   - Validera att assignment finns
   - Validera att lärare har tillgång
   - Returnera 200 med assignment object

5. **Implementera PUT /api/assignments/:id** (1 timme)
   - Validera att assignment finns
   - Validera att lärare har tillgång
   - Uppdatera i databas
   - Returnera 200 med uppdaterad assignment

6. **Implementera DELETE /api/assignments/:id** (30 min)
   - Validera att assignment finns
   - Validera att lärare har tillgång
   - Soft delete (sätt `deleted_at`)
   - Returnera 200 med bekräftelse

7. **Testa alla endpoints** (1 timme)
   - Unit tests för varje endpoint
   - Integration tests för workflow

**Acceptance:**
- [ ] `POST /api/assignments` - Skapa uppgift
- [ ] `GET /api/assignments` - Lista alla uppgifter för lärare
- [ ] `GET /api/assignments/:id` - Hämta specifik uppgift
- [ ] `PUT /api/assignments/:id` - Uppdatera uppgift
- [ ] `DELETE /api/assignments/:id` - Ta bort uppgift
- [ ] **Databas-schema** - Assignments table
- [ ] **RBAC** - Endast lärare kan skapa/uppdatera/radera uppgifter
- [ ] **Validering** - Input validering fungerar
- [ ] **Error handling** - Fel hanteras korrekt

**Low Code Approach:**
- Använd Express.js eller NestJS (enklare routing)
- Använd Prisma eller TypeORM (enklare ORM)
- Använd Joi eller Zod (enklare validering)

**Tidsestimat:** 5-6 timmar

---

#### **SCRUM-27: Backend - Submission Workflow API**

**Beskrivning:** Som backend vill jag ha endpoints för submission workflow.

**Varför:** Elever ska kunna lämna in, lärare ska kunna se inlämningar.

**Detaljerade Steg:**
1. **Skapa databas-schema** (30 min)
   - Tabell: `submissions`
   - Fält: `id`, `assignment_id`, `student_id`, `storage_path`, `file_type`, `file_name`, `file_size`, `status`, `ai_analysis`, `teacher_feedback`, `grade_suggestion`, `final_grade`, `submitted_at`, `created_at`, `updated_at`, `deleted_at`
   - Index: `assignment_id`, `student_id`, `status`

2. **Implementera POST /api/assignments/:id/submit** (2 timmar)
   - Validera att assignment finns
   - Validera att elev finns
   - Validera fil (Word/PDF/bild, max 10MB)
   - Ladda upp fil till storage (lokalt eller Azure)
   - Spara submission i databas med status `submitted`
   - Returnera 201 med submission object

3. **Implementera GET /api/assignments/:id/submissions** (1 timme)
   - Validera att assignment finns
   - Validera att användare är lärare eller elev
   - Filtrera per `status` (optional)
   - Filtrera per `student_id` (optional)
   - Returnera 200 med lista

4. **Implementera GET /api/assignments/:id/submissions/:submissionId** (30 min)
   - Validera att submission finns
   - Validera att användare har tillgång
   - Returnera 200 med submission object

5. **Testa alla endpoints** (1 timme)
   - Unit tests för varje endpoint
   - Integration tests för workflow

**Acceptance:**
- [ ] `POST /api/assignments/:id/submit` - Elev lämnar in uppgift
- [ ] `GET /api/assignments/:id/submissions` - Lärare ser alla inlämningar
- [ ] `GET /api/assignments/:id/submissions/:submissionId` - Hämta specifik inlämning
- [ ] **Workflow status:** `pending` → `submitted` → `ai_analyzed` → `pending_approval` → `approved` → `published_to_student`
- [ ] **Databas-schema** - Submissions table
- [ ] **RBAC** - Elever ser endast sina inlämningar, lärare ser alla i klassen
- [ ] **File upload** - Word/PDF/bilder fungerar
- [ ] **Error handling** - Fel hanteras korrekt

**Low Code Approach:**
- Använd Multer för file upload (enklare)
- Använd StorageService abstraction (enklare switch mellan lokalt/Azure)
- Använd status enum (enklare workflow)

**Tidsestimat:** 5-6 timmar

---

#### **SCRUM-28: Backend - AI Analysis Integration**

**Beskrivning:** Som backend vill jag kunna anropa Python API för AI-analys.

**Varför:** Backend måste kunna anropa Python API när elev lämnar in.

**Detaljerade Steg:**
1. **Skapa AI Service class** (1 timme)
   - Metod: `analyzeSubmission(submissionId, assignmentId, studentId, content)`
   - Anropa Python API `POST /api/version1/assignments/process/analyze`
   - Hantera timeout (30 sekunder)
   - Hantera fel

2. **Implementera POST /api/ai/analyze** (1 timme)
   - Validera input (submission_id, assignment_id, student_id, content)
   - Anropa AI Service
   - Uppdatera submission status till `ai_analyzed`
   - Spara AI-analys resultat i databas
   - Uppdatera submission status till `pending_approval`
   - Returnera 200 med AI-analys resultat

3. **Error handling** (1 timme)
   - Timeout handling (504 Gateway Timeout)
   - Python API fel handling (500 Internal Server Error)
   - Retry logic (3 försök)

4. **Testa integration** (1 timme)
   - Testa med Python API running
   - Testa med Python API down
   - Testa timeout scenario

**Acceptance:**
- [ ] `POST /api/ai/analyze` - Proxy till Python API
- [ ] **Integration** - Anropa Python API `/api/version1/assignments/process/analyze`
- [ ] **Error handling** - Hantera fel från Python API
- [ ] **Timeout** - Timeout för AI-anrop (30 sekunder)
- [ ] **Status tracking** - Uppdatera submission status efter AI-analys
- [ ] **Retry logic** - 3 försök om AI-anrop misslyckas

**Low Code Approach:**
- Använd HTTPX eller Axios (enklare HTTP client)
- Använd try-catch för error handling (enklare)
- Använd environment variables för Python API URL (enklare config)

**Tidsestimat:** 4-5 timmar

---

#### **SCRUM-29: Backend - Approval Workflow API**

**Beskrivning:** Som backend vill jag ha endpoints för lärare godkännande.

**Varför:** Lärare måste kunna godkänna AI-betygsförslag innan elev ser.

**Detaljerade Steg:**
1. **Implementera POST /api/submissions/:id/approve** (1 timme)
   - Validera att submission finns
   - Validera att status är `pending_approval`
   - Validera att användare är lärare
   - Uppdatera submission status till `approved`
   - Uppdatera submission status till `published_to_student`
   - Spara `approved_at` timestamp
   - Returnera 200 med uppdaterad submission

2. **Implementera POST /api/submissions/:id/reject** (1 timme)
   - Validera att submission finns
   - Validera att status är `pending_approval`
   - Validera att användare är lärare
   - Uppdatera submission status till `rejected`
   - Spara `rejection_reason`
   - Spara `rejected_at` timestamp
   - Returnera 200 med uppdaterad submission

3. **Implementera PUT /api/submissions/:id/feedback** (1 timme)
   - Validera att submission finns
   - Validera att användare är lärare
   - Uppdatera `teacher_feedback` i databas
   - Returnera 200 med uppdaterad submission

4. **Implementera PUT /api/submissions/:id/grade** (1 timme)
   - Validera att submission finns
   - Validera att användare är lärare
   - Validera att grade är giltig (E, D, C, B, A)
   - Uppdatera `final_grade` i databas
   - Spara `grade_adjustment_reason`
   - Returnera 200 med uppdaterad submission

5. **Testa alla endpoints** (1 timme)
   - Unit tests för varje endpoint
   - Integration tests för workflow

**Acceptance:**
- [ ] `POST /api/submissions/:id/approve` - Lärare godkänner betygsförslag
- [ ] `POST /api/submissions/:id/reject` - Lärare nekar betygsförslag
- [ ] `PUT /api/submissions/:id/feedback` - Lärare redigerar feedback
- [ ] `PUT /api/submissions/:id/grade` - Lärare justerar betyg
- [ ] **Workflow:** `pending_approval` → `approved` → `published_to_student`
- [ ] **Databas-schema** - Approval status tracking
- [ ] **RBAC** - Endast lärare kan godkänna
- [ ] **Validering** - Grade validering fungerar
- [ ] **Error handling** - Fel hanteras korrekt

**Low Code Approach:**
- Använd status enum (enklare workflow)
- Använd middleware för RBAC (enklare auth)
- Använd transactions för databas (enklare data integrity)

**Tidsestimat:** 5-6 timmar

---

#### **SCRUM-30: Backend - Student Management API**

**Beskrivning:** Som backend vill jag ha endpoints för att hämta elever.

**Varför:** Lärare behöver se alla elever i sina klasser.

**Detaljerade Steg:**
1. **Skapa databas-schema** (om inte redan finns) (30 min)
   - Tabell: `students`
   - Tabell: `classes`
   - Tabell: `enrollments`

2. **Implementera GET /api/students/:id** (30 min)
   - Validera att elev finns
   - Validera att användare har tillgång (lärare eller elev själv)
   - Returnera 200 med student object

3. **Implementera GET /api/classes/:classId/students** (30 min)
   - Validera att klass finns
   - Validera att användare är lärare för klassen
   - Hämta alla elever i klassen
   - Returnera 200 med lista

4. **Testa alla endpoints** (30 min)
   - Unit tests för varje endpoint
   - Integration tests för RBAC

**Acceptance:**
- [ ] `GET /api/students/:id` - Hämta specifik elev
- [ ] `GET /api/classes/:classId/students` - Lista elever i klass
- [ ] **Databas-schema** - Students, Classes, Enrollments tables (om inte redan finns)
- [ ] **RBAC** - Lärare ser endast sina klasser
- [ ] **Error handling** - Fel hanteras korrekt

**Low Code Approach:**
- Använd JOIN queries (enklare databashämtning)
- Använd middleware för RBAC (enklare auth)

**Tidsestimat:** 2-3 timmar

---

#### **SCRUM-31: Backend - Material Management API**

**Beskrivning:** Som backend vill jag ha endpoints för material management.

**Varför:** Lärare behöver kunna ladda upp material (Word, PDF, bilder) för att skapa uppgifter.

**Detaljerade Steg:**
1. **Skapa databas-schema** (30 min)
   - Tabell: `materials`
   - Fält: `id`, `title`, `description`, `file_type`, `storage_path`, `file_name`, `file_size`, `teacher_id`, `course_id`, `created_at`, `updated_at`, `deleted_at`
   - Index: `teacher_id`, `course_id`

2. **Implementera POST /api/materials** (1 timme)
   - Validera att lärare finns
   - Validera fil (Word/PDF/bild, max 10MB)
   - Ladda upp fil till storage (lokalt eller Azure)
   - Spara material i databas
   - Returnera 201 med material object

3. **Implementera GET /api/materials** (30 min)
   - Filtrera per `teacher_id` (required)
   - Filtrera per `course_id` (optional)
   - Paginering (page, limit)
   - Returnera 200 med lista

4. **Implementera GET /api/materials/:id** (30 min)
   - Validera att material finns
   - Validera att lärare har tillgång
   - Returnera 200 med material object

5. **Implementera DELETE /api/materials/:id** (30 min)
   - Validera att material finns
   - Validera att lärare har tillgång
   - Soft delete (sätt `deleted_at`)
   - Ta bort fil från storage
   - Returnera 200 med bekräftelse

6. **Testa alla endpoints** (1 timme)
   - Unit tests för varje endpoint
   - Integration tests för workflow

**Acceptance:**
- [ ] `POST /api/materials` - Lärare laddar upp material
- [ ] `GET /api/materials` - Lista material
- [ ] `GET /api/materials/:id` - Hämta specifik material
- [ ] `DELETE /api/materials/:id` - Ta bort material
- [ ] **Databas-schema** - Materials table
- [ ] **RBAC** - Endast lärare kan skapa/radera material
- [ ] **File upload** - Word/PDF/bilder fungerar
- [ ] **Error handling** - Fel hanteras korrekt

**Low Code Approach:**
- Använd Multer för file upload (enklare)
- Använd StorageService abstraction (enklare switch mellan lokalt/Azure)
- Använd middleware för RBAC (enklare auth)

**Tidsestimat:** 4-5 timmar

---

#### **SCRUM-32: Backend - Exam Management API (CRUD)**

**Beskrivning:** Som backend vill jag ha CRUD-endpoints för exams.

**Varför:** Lärare behöver kunna skapa, läsa, uppdatera och ta bort prov.

**Detaljerade Steg:**
1. **Skapa databas-schema** (30 min)
   - Tabell: `exams`
   - Fält: `id`, `title`, `description`, `subject`, `level`, `duration_minutes`, `teacher_id`, `course_id`, `class_id`, `questions`, `generated_at`, `created_at`, `updated_at`, `deleted_at`
   - Index: `teacher_id`, `class_id`, `course_id`

2. **Implementera POST /api/exams** (1 timme)
   - Validera input (title, description, subject, level)
   - Validera att lärare finns
   - Spara i databas
   - Returnera 201 med exam object

3. **Implementera POST /api/exams/:id/generate-questions** (1 timme)
   - Validera att exam finns
   - Anropa Python API `POST /api/version1/exams/generate-questions`
   - Spara questions i databas
   - Returnera 200 med questions

4. **Implementera GET /api/exams** (1 timme)
   - Filtrera per `teacher_id` (required)
   - Filtrera per `class_id` (optional)
   - Filtrera per `subject` (optional)
   - Paginering (page, limit)
   - Returnera 200 med lista

5. **Implementera GET /api/exams/:id** (30 min)
   - Validera att exam finns
   - Validera att lärare har tillgång
   - Returnera 200 med exam object

6. **Implementera PUT /api/exams/:id** (1 timme)
   - Validera att exam finns
   - Validera att lärare har tillgång
   - Uppdatera i databas
   - Returnera 200 med uppdaterad exam

7. **Implementera DELETE /api/exams/:id** (30 min)
   - Validera att exam finns
   - Validera att lärare har tillgång
   - Soft delete (sätt `deleted_at`)
   - Returnera 200 med bekräftelse

8. **Testa alla endpoints** (1 timme)
   - Unit tests för varje endpoint
   - Integration tests för workflow

**Acceptance:**
- [ ] `POST /api/exams` - Skapa prov
- [ ] `POST /api/exams/:id/generate-questions` - Generera provfrågor med AI
- [ ] `GET /api/exams` - Lista alla prov för lärare
- [ ] `GET /api/exams/:id` - Hämta specifik prov
- [ ] `PUT /api/exams/:id` - Uppdatera prov
- [ ] `DELETE /api/exams/:id` - Ta bort prov
- [ ] **Databas-schema** - Exams table
- [ ] **RBAC** - Endast lärare kan skapa/uppdatera/radera prov
- [ ] **Integration** - Anropa Python API för att generera provfrågor
- [ ] **Error handling** - Fel hanteras korrekt

**Low Code Approach:**
- Använd Express.js eller NestJS (enklare routing)
- Använd Prisma eller TypeORM (enklare ORM)
- Använd Joi eller Zod (enklare validering)
- Använd HTTPX eller Axios (enklare HTTP client)

**Tidsestimat:** 6-7 timmar

---

#### **SCRUM-33: Backend - Teaching Materials Management API (CRUD)**

**Beskrivning:** Som backend vill jag ha CRUD-endpoints för teaching materials.

**Varför:** Lärare behöver kunna skapa, läsa, uppdatera och ta bort undervisningsmaterial.

**Detaljerade Steg:**
1. **Skapa databas-schema** (30 min)
   - Tabell: `teaching_materials`
   - Fält: `id`, `title`, `description`, `content`, `type`, `subject`, `level`, `teacher_id`, `course_id`, `generated_at`, `created_at`, `updated_at`, `deleted_at`
   - Index: `teacher_id`, `course_id`, `subject`

2. **Implementera POST /api/teaching-materials** (1 timme)
   - Validera input (title, description, subject, level)
   - Validera att lärare finns
   - Spara i databas
   - Returnera 201 med teaching material object

3. **Implementera POST /api/teaching-materials/generate** (1 timme)
   - Validera input (topic, subject, level)
   - Anropa Python API `POST /api/version1/teaching/generate-materials`
   - Spara generated content i databas
   - Returnera 200 med teaching material object

4. **Implementera GET /api/teaching-materials** (30 min)
   - Filtrera per `teacher_id` (required)
   - Filtrera per `course_id` (optional)
   - Filtrera per `subject` (optional)
   - Paginering (page, limit)
   - Returnera 200 med lista

5. **Implementera GET /api/teaching-materials/:id** (30 min)
   - Validera att teaching material finns
   - Validera att lärare har tillgång
   - Returnera 200 med teaching material object

6. **Implementera PUT /api/teaching-materials/:id** (1 timme)
   - Validera att teaching material finns
   - Validera att lärare har tillgång
   - Uppdatera i databas
   - Returnera 200 med uppdaterad teaching material

7. **Implementera DELETE /api/teaching-materials/:id** (30 min)
   - Validera att teaching material finns
   - Validera att lärare har tillgång
   - Soft delete (sätt `deleted_at`)
   - Returnera 200 med bekräftelse

8. **Testa alla endpoints** (1 timme)
   - Unit tests för varje endpoint
   - Integration tests för workflow

**Acceptance:**
- [ ] `POST /api/teaching-materials` - Skapa undervisningsmaterial
- [ ] `POST /api/teaching-materials/generate` - Generera undervisningsmaterial med AI
- [ ] `GET /api/teaching-materials` - Lista alla undervisningsmaterial för lärare
- [ ] `GET /api/teaching-materials/:id` - Hämta specifik undervisningsmaterial
- [ ] `PUT /api/teaching-materials/:id` - Uppdatera undervisningsmaterial
- [ ] `DELETE /api/teaching-materials/:id` - Ta bort undervisningsmaterial
- [ ] **Databas-schema** - Teaching Materials table
- [ ] **RBAC** - Endast lärare kan skapa/uppdatera/radera undervisningsmaterial
- [ ] **Integration** - Anropa Python API för att generera undervisningsmaterial
- [ ] **Error handling** - Fel hanteras korrekt

**Low Code Approach:**
- Använd Express.js eller NestJS (enklare routing)
- Använd Prisma eller TypeORM (enklare ORM)
- Använd Joi eller Zod (enklare validering)
- Använd HTTPX eller Axios (enklare HTTP client)

**Tidsestimat:** 6-7 timmar

---

### **FRONTEND UPPGIFTER (4 uppgifter)**

#### **SCRUM-34: Teacher - Dashboard (Frontend)**

**Beskrivning:** Som lärare vill jag se en översikt över alla mina elever och uppgifter.

**Varför:** Lärare behöver snabb överblick över klassen och progression.

**Detaljerade Steg:**
1. **Skapa Teacher Dashboard Page** (2 timmar)
   - Layout: Header, Sidebar, Main Content
   - Komponenter: Dashboard Stats, Recent Assignments, Recent Submissions

2. **Implementera Dashboard Stats** (1 timme)
   - Totalt antal elever
   - Totalt antal uppgifter
   - Totalt antal inlämningar
   - Antal uppgifter som väntar på godkännande
   - Anropa Backend API `GET /api/assignments?teacher_id=...`

3. **Implementera Recent Assignments** (1 timme)
   - Lista över 5 senaste uppgifterna
   - Visa titel, deadline, antal inlämningar
   - Anropa Backend API `GET /api/assignments?teacher_id=...&limit=5`

4. **Implementera Recent Submissions** (1 timme)
   - Lista över 5 senaste inlämningarna
   - Visa elev, uppgift, status
   - Anropa Backend API `GET /api/assignments/:id/submissions`

5. **Implementera Loading & Error States** (1 timme)
   - Loading spinner
   - Error message
   - Empty state

6. **Testa UI** (1 timme)
   - Testa med riktiga data
   - Testa med tom data
   - Testa med fel

**Acceptance:**
- [ ] **UI: Teacher Dashboard Page** - Översikt över alla elever och uppgifter
- [ ] **UI: Dashboard Stats** - Totalt antal elever, uppgifter, inlämningar, väntande godkännande
- [ ] **UI: Recent Assignments** - Lista över 5 senaste uppgifterna
- [ ] **UI: Recent Submissions** - Lista över 5 senaste inlämningarna
- [ ] **UI: Loading State** - Loading spinner
- [ ] **UI: Error State** - Error message
- [ ] **UI: Empty State** - Empty state när inga data finns
- [ ] **Integration** - Anropa Backend API
- [ ] **Responsive design** - Fungerar på mobil och desktop

**Low Code Approach:**
- Använd React + Tailwind CSS (enklare styling)
- Använd React Query eller SWR (enklare data fetching)
- Använd Reusable components (enklare maintenance)

**Tidsestimat:** 7-8 timmar

---

#### **SCRUM-35: Teacher - Assignment Management (Frontend)**

**Beskrivning:** Som lärare vill jag kunna skapa, läsa, uppdatera och ta bort uppgifter i UI.

**Varför:** Lärare behöver hantera uppgifter.

**Detaljerade Steg:**
1. **Skapa Assignments List Page** (1 timme)
   - Layout: Lista med assignment cards
   - Komponenter: Assignment Card, Filter, Search

2. **Implementera Assignment Card** (1 timme)
   - Visa titel, deadline, status
   - Visa antal inlämningar
   - Anropa Backend API `GET /api/assignments?teacher_id=...`

3. **Implementera Create Assignment Form** (2 timmar)
   - Formulär: Titel, Beskrivning, Typ, Deadline, Klass
   - Validering: Alla fält required
   - Anropa Backend API `POST /api/assignments`

4. **Implementera Edit Assignment Form** (1 timme)
   - Pre-fyll formulär med befintlig data
   - Anropa Backend API `PUT /api/assignments/:id`

5. **Implementera Delete Assignment** (30 min)
   - Bekräftelse dialog
   - Anropa Backend API `DELETE /api/assignments/:id`

6. **Implementera Filter & Search** (1 timme)
   - Filtrera per klass, typ, status
   - Sök efter titel

7. **Testa UI** (1 timme)
   - Testa create
   - Testa edit
   - Testa delete
   - Testa filter & search

**Acceptance:**
- [ ] **UI: Assignments List** - Lista alla uppgifter
- [ ] **UI: Create Assignment** - Formulär för att skapa uppgift
- [ ] **UI: Edit Assignment** - Formulär för att uppdatera uppgift
- [ ] **UI: Delete Assignment** - Ta bort uppgift med bekräftelse
- [ ] **UI: Assignment Card** - Visa uppgiftens titel, deadline, status
- [ ] **UI: Filter** - Filtrera per klass, kurs, typ
- [ ] **UI: Search** - Sök efter uppgifter
- [ ] **UI: Loading State** - Loading spinner
- [ ] **UI: Error State** - Error message
- [ ] **Integration** - Anropa Backend API CRUD endpoints

**Low Code Approach:**
- Använd React Hook Form (enklare form handling)
- Använd Zod eller Yup (enklare validering)
- Använd Reusable components (enklare maintenance)

**Tidsestimat:** 7-8 timmar

---

#### **SCRUM-36: Teacher - Material Upload UI (Frontend)**

**Beskrivning:** Som lärare vill jag kunna ladda upp material (Word, PDF, bilder) i UI.

**Varför:** Lärare behöver kunna ladda upp material för att skapa uppgifter.

**Detaljerade Steg:**
1. **Skapa Material Upload Form** (2 timmar)
   - Formulär: Titel, Beskrivning, Fil
   - Validering: Fil required, filtyp (Word/PDF/bild)
   - Anropa Backend API `POST /api/materials`

2. **Implementera File Upload** (1 timme)
   - File input för Word/PDF/bilder
   - Drag & drop för filer
   - File preview (för bilder)
   - Progress bar för upload

3. **Implementera Material List** (1 timme)
   - Lista alla material
   - Visa titel, filtyp, datum
   - Anropa Backend API `GET /api/materials`

4. **Implementera Delete Material** (30 min)
   - Bekräftelse dialog
   - Anropa Backend API `DELETE /api/materials/:id`

5. **Testa UI** (1 timme)
   - Testa upload
   - Testa list
   - Testa delete

**Acceptance:**
- [ ] **UI: Material Upload Form** - Formulär för att ladda upp material
- [ ] **UI: File Upload** - Upload Word/PDF/bilder
- [ ] **UI: Drag & Drop** - Drag & drop för filer
- [ ] **UI: File Preview** - Förhandsvisning av filer (bilder)
- [ ] **UI: Progress Bar** - Visa uppladdningsframsteg
- [ ] **UI: Material List** - Lista alla material
- [ ] **UI: Delete Material** - Ta bort material med bekräftelse
- [ ] **UI: Loading State** - Loading spinner
- [ ] **UI: Error State** - Error message
- [ ] **Integration** - Anropa Backend API Material Management endpoints

**Low Code Approach:**
- Använd React Hook Form (enklare form handling)
- Använd react-dropzone (enklare drag & drop)
- Använd Reusable components (enklare maintenance)

**Tidsestimat:** 5.5-6 timmar

---

#### **SCRUM-37: Teacher - Exam Management UI (Frontend)**

**Beskrivning:** Som lärare vill jag kunna skapa och hantera prov i UI.

**Varför:** Lärare behöver kunna skapa och hantera prov.

**Detaljerade Steg:**
1. **Skapa Exam List Page** (1 timme)
   - Lista alla prov
   - Visa titel, ämne, nivå, status
   - Anropa Backend API `GET /api/exams?teacher_id=...`

2. **Implementera Create Exam Form** (2 timmar)
   - Formulär: Titel, Beskrivning, Ämne, Nivå, Varaktighet
   - Validering: Alla fält required
   - Anropa Backend API `POST /api/exams`

3. **Implementera Generate Exam Questions** (1 timme)
   - Knapp för att generera provfrågor med AI
   - Anropa Backend API `POST /api/exams/:id/generate-questions`
   - Visa loading state
   - Visa genererade frågor

4. **Implementera Edit Exam Form** (1 timme)
   - Pre-fyll formulär med befintlig data
   - Anropa Backend API `PUT /api/exams/:id`

5. **Implementera Delete Exam** (30 min)
   - Bekräftelse dialog
   - Anropa Backend API `DELETE /api/exams/:id`

6. **Testa UI** (1 timme)
   - Testa create
   - Testa generate questions
   - Testa edit
   - Testa delete

**Acceptance:**
- [ ] **UI: Exam List** - Lista alla prov
- [ ] **UI: Create Exam** - Formulär för att skapa prov
- [ ] **UI: Generate Exam Questions** - Generera provfrågor med AI
- [ ] **UI: Edit Exam** - Formulär för att uppdatera prov
- [ ] **UI: Delete Exam** - Ta bort prov med bekräftelse
- [ ] **UI: Loading State** - Loading spinner
- [ ] **UI: Error State** - Error message
- [ ] **Integration** - Anropa Backend API Exam endpoints

**Low Code Approach:**
- Använd React Hook Form (enklare form handling)
- Använd Zod eller Yup (enklare validering)
- Använd Reusable components (enklare maintenance)

**Tidsestimat:** 6.5-7 timmar

---

#### **SCRUM-38: Teacher - Teaching Materials UI (Frontend)**

**Beskrivning:** Som lärare vill jag kunna skapa och hantera undervisningsmaterial i UI.

**Varför:** Lärare behöver kunna skapa och hantera undervisningsmaterial.

**Detaljerade Steg:**
1. **Skapa Teaching Materials List Page** (1 timme)
   - Lista alla undervisningsmaterial
   - Visa titel, ämne, typ, datum
   - Anropa Backend API `GET /api/teaching-materials?teacher_id=...`

2. **Implementera Create Teaching Material Form** (1 timme)
   - Formulär: Titel, Beskrivning, Ämne, Nivå
   - Validering: Alla fält required
   - Anropa Backend API `POST /api/teaching-materials`

3. **Implementera Generate Teaching Material** (1 timme)
   - Formulär: Topic, Ämne, Nivå
   - Knapp för att generera material med AI
   - Anropa Backend API `POST /api/teaching-materials/generate`
   - Visa loading state
   - Visa genererat material

4. **Implementera Edit Teaching Material Form** (1 timme)
   - Pre-fyll formulär med befintlig data
   - Anropa Backend API `PUT /api/teaching-materials/:id`

5. **Implementera Delete Teaching Material** (30 min)
   - Bekräftelse dialog
   - Anropa Backend API `DELETE /api/teaching-materials/:id`

6. **Testa UI** (1 timme)
   - Testa create
   - Testa generate
   - Testa edit
   - Testa delete

**Acceptance:**
- [ ] **UI: Teaching Materials List** - Lista alla undervisningsmaterial
- [ ] **UI: Create Teaching Material** - Formulär för att skapa undervisningsmaterial
- [ ] **UI: Generate Teaching Material** - Generera undervisningsmaterial med AI
- [ ] **UI: Edit Teaching Material** - Formulär för att uppdatera undervisningsmaterial
- [ ] **UI: Delete Teaching Material** - Ta bort undervisningsmaterial med bekräftelse
- [ ] **UI: Loading State** - Loading spinner
- [ ] **UI: Error State** - Error message
- [ ] **Integration** - Anropa Backend API Teaching Materials endpoints

**Low Code Approach:**
- Använd React Hook Form (enklare form handling)
- Använd Zod eller Yup (enklare validering)
- Använd Reusable components (enklare maintenance)

**Tidsestimat:** 5.5-6 timmar

---

### **PYTHON API UPPGIFTER (5 uppgifter)**

#### **SCRUM-39: Python API - Förbättra AI Analysis Endpoint**

**Beskrivning:** Som Python API vill jag förbättra AI Analysis endpoint som backend anropar.

**Varför:** Backend anropar Python API för AI-analys, måste vara pålitlig och snabb.

**Detaljerade Steg:**
1. **Förbättra validering** (1 timme)
   - Validera input (content, assignment_id, student_id)
   - Validera att content inte är tom
   - Validera att content är minst 10 tecken

2. **Förbättra error handling** (1 timme)
   - Hantera timeout (30 sekunder)
   - Hantera OpenAI API fel
   - Hantera ChromaDB fel
   - Returnera tydliga felmeddelanden

3. **Standardisera response format** (1 timme)
   - Standardiserat JSON format
   - Inkludera `success`, `assignment_id`, `student_id`, `analysis`, `feedback`, `processed_at`

4. **Förbättra logging** (30 min)
   - Logga alla AI-anrop
   - Logga fel
   - Logga prestanda

5. **Förbättra prestanda** (1 timme)
   - Caching för liknande uppgifter
   - Async processing
   - Optimera LLM prompts

6. **Testa endpoint** (1 timme)
   - Testa med riktiga data
   - Testa med fel data
   - Testa timeout scenario

**Acceptance:**
- [ ] **Förbättra endpoint:** `POST /api/version1/assignments/process/analyze`
- [ ] **Error handling** - Bättre felhantering och loggning
- [ ] **Timeout** - Hantera timeout korrekt (max 30 sekunder)
- [ ] **Response format** - Standardiserat response format
- [ ] **Logging** - Logga alla AI-anrop för debugging
- [ ] **Validation** - Validera input (content, assignment_id, student_id)
- [ ] **Performance** - Förbättra prestanda (caching, async)

**Low Code Approach:**
- Använd Pydantic för validering (enklare)
- Använd try-catch för error handling (enklare)
- Använd async/await för prestanda (enklare)

**Tidsestimat:** 5-6 timmar

---

#### **SCRUM-40: Python API - API Key Middleware**

**Beskrivning:** Som Python API vill jag validera att requests kommer från backend.

**Varför:** Säkerhet - endast backend ska kunna anropa Python API.

**Detaljerade Steg:**
1. **Skapa API Key Middleware** (1 timme)
   - Middleware: Validera X-API-KEY header
   - Skip health checks
   - Returnera 403 om API key saknas eller är ogiltig

2. **Konfigurera API Key** (30 min)
   - Environment variable: `PYTHON_API_KEY`
   - Default value: `CHANGE-ME-IN-PRODUCTION`

3. **Implementera logging** (30 min)
   - Logga alla försök utan giltig API key
   - Logga IP-adress

4. **Testa middleware** (30 min)
   - Testa med giltig API key
   - Testa med ogiltig API key
   - Testa utan API key
   - Testa health checks

**Acceptance:**
- [ ] **API Key Middleware** - Validera X-API-KEY header
- [ ] **Error Response** - Returnera 403 om API key saknas eller är ogiltig
- [ ] **Logging** - Logga alla försök utan giltig API key
- [ ] **Configuration** - API key från environment variable
- [ ] **Health checks** - Skip API key för health checks

**Low Code Approach:**
- Använd FastAPI middleware (enklare)
- Använd environment variables (enklare config)

**Tidsestimat:** 2-3 timmar

---

#### **SCRUM-41: Python API - Material Processing API**

**Beskrivning:** Som Python API vill jag kunna bearbeta material som lärare laddar upp.

**Varför:** Backend behöver kunna bearbeta material (Word, PDF) för att använda i uppgifter.

**Detaljerade Steg:**
1. **Implementera POST /api/version1/materials/process** (2 timmar)
   - Input: `material_id`, `storage_path`, `file_type`
   - Bearbeta material (Word/PDF)
   - Extrahera text och metadata
   - Returnera bearbetad data

2. **Implementera GET /api/version1/materials/:id/preview** (1 timme)
   - Input: `material_id`
   - Hämta material från storage
   - Generera preview (för bilder) eller text-extraktion (för Word/PDF)
   - Returnera preview data

3. **Testa endpoints** (1 timme)
   - Testa med Word-filer
   - Testa med PDF-filer
   - Testa med bilder

**Acceptance:**
- [ ] **Endpoint:** `POST /api/version1/materials/process` - Bearbeta material
- [ ] **Endpoint:** `GET /api/version1/materials/:id/preview` - Förhandsvisning av material
- [ ] **Word Processing** - Bearbeta Word-filer
- [ ] **PDF Processing** - Bearbeta PDF-filer
- [ ] **Image Processing** - Bearbeta bilder
- [ ] **Error handling** - Fel hanteras korrekt

**Low Code Approach:**
- Använd befintlig DocumentProcessor (enklare)
- Använd Pydantic för validering (enklare)

**Tidsestimat:** 4-5 timmar

---

#### **SCRUM-42: Python API - Material Generation**

**Beskrivning:** Som Python API vill jag kunna generera undervisningsmaterial med AI.

**Varför:** Lärare behöver AI-hjälp för att generera undervisningsmaterial.

**Detaljerade Steg:**
1. **Implementera POST /api/version1/teaching/generate-materials** (2 timmar)
   - Input: `topic`, `subject`, `level`, `material_type`, `duration_minutes`
   - Validera input
   - Generera undervisningsmaterial med LLM
   - Returnera material med innehåll, instruktioner, övningar

2. **Förbättra LLM prompt för material generation** (1 timme)
   - Anpassa prompt för ämne och nivå
   - Inkludera material_type (worksheet, presentation, handout, etc.)
   - Generera strukturerat innehåll
   - Inkludera övningar och exempel

3. **Testa endpoint** (1 timme)
   - Testa med riktiga data
   - Testa med olika ämnen
   - Testa med olika material_types

**Acceptance:**
- [ ] **Endpoint:** `POST /api/version1/teaching/generate-materials`
- [ ] **Input:** Topic, subject, level, material_type, duration_minutes
- [ ] **Output:** Undervisningsmaterial med innehåll, instruktioner, övningar
- [ ] **Olika typer** - Worksheet, presentation, handout, etc.
- [ ] **Strukturerat** - Strukturerat innehåll med övningar
- [ ] **Error handling** - Fel hanteras korrekt

**Low Code Approach:**
- Använd LLM prompt engineering (enklare)
- Använd Pydantic för validering (enklare)

**Tidsestimat:** 4-5 timmar

---

#### **SCRUM-43: Python API - Assignment Template Generator**

**Beskrivning:** Som Python API vill jag kunna generera uppgiftsmallar med AI.

**Varför:** Lärare behöver AI-hjälp för att skapa uppgiftsmallar.

**Detaljerade Steg:**
1. **Implementera POST /api/version1/assignments/process/generate-template** (2 timmar)
   - Input: `assignment_type`, `subject`, `level`, `topic`, `duration_minutes`
   - Validera input
   - Generera uppgiftsmall med LLM
   - Returnera template med instruktioner, kriterier, exempel

2. **Förbättra LLM prompt för template generation** (1 timme)
   - Anpassa prompt för assignment_type (dag/vecka/prov/individuell)
   - Inkludera Gy11-kriterier
   - Generera strukturerad mall
   - Inkludera bedömningskriterier

3. **Testa endpoint** (1 timme)
   - Testa med riktiga data
   - Testa med olika assignment_types
   - Testa med olika ämnen

**Acceptance:**
- [ ] **Endpoint:** `POST /api/version1/assignments/process/generate-template`
- [ ] **Input:** Assignment type, subject, level, topic, duration_minutes
- [ ] **Output:** Uppgiftsmall med instruktioner, kriterier, exempel
- [ ] **Olika typer** - Dag/vecka/prov/individuell
- [ ] **Gy11-kriterier** - Inkludera Gy11-kriterier i mallen
- [ ] **Error handling** - Fel hanteras korrekt

**Low Code Approach:**
- Använd LLM prompt engineering (enklare)
- Använd Pydantic för validering (enklare)

**Tidsestimat:** 4-5 timmar

---

## 📊 **SPRINT 4 SAMMANFATTNING**

### **Totalt: 17 uppgifter** (12 ursprungliga + 5 nya)
- **Backend:** 8 uppgifter (37-45 timmar) - **+2 nya**
- **Frontend:** 5 uppgifter (31.5-35 timmar) - **+2 nya**
- **Python API:** 5 uppgifter (19-24 timmar) - **+2 nya**

### **Total tid:** 87.5-104 timmar (ca 11-13 dagar per person) - **+32-37 timmar**

---

## 🚀 **SPRINT 5: Student Portal Start**

### **Datum:** 17 november - 28 november (2 veckor)

### **Totalt:** 12 uppgifter

---

### **BACKEND UPPGIFTER (2 uppgifter)**

#### **SCRUM-44: Backend - Student Assignments API**

**Beskrivning:** Som backend vill jag ha endpoints för att hämta uppgifter för elev.

**Varför:** Elever behöver se alla sina uppgifter.

**Detaljerade Steg:**
1. **Implementera GET /api/students/:id/assignments** (1 timme)
   - Validera att elev finns
   - Validera att användare är elev själv
   - Hämta alla uppgifter för elev (via enrollments)
   - Filtrera per `status` (optional)
   - Returnera 200 med lista

2. **Testa endpoint** (30 min)
   - Unit tests
   - Integration tests för RBAC

**Acceptance:**
- [ ] `GET /api/students/:id/assignments` - Lista uppgifter för elev
- [ ] **RBAC** - Elever ser endast sina uppgifter
- [ ] **Filter** - Filtrera per status (optional)
- [ ] **Error handling** - Fel hanteras korrekt

**Low Code Approach:**
- Använd JOIN queries (enklare databashämtning)
- Använd middleware för RBAC (enklare auth)

**Tidsestimat:** 1.5-2 timmar

---

#### **SCRUM-45: Backend - Student Progress API**

**Beskrivning:** Som backend vill jag ha endpoints för att hämta progress data för elev.

**Varför:** Elever behöver se sin utveckling över tid.

**Detaljerade Steg:**
1. **Implementera GET /api/students/:id/progress** (2 timmar)
   - Validera att elev finns
   - Validera att användare är elev själv
   - Hämta alla submissions för elev
   - Beräkna progress data (utveckling över tid, styrkor, förbättringsområden)
   - Returnera 200 med progress data

2. **Testa endpoint** (1 timme)
   - Unit tests
   - Integration tests för RBAC

**Acceptance:**
- [ ] `GET /api/students/:id/progress` - Progress tracking data
- [ ] **Progress data** - Utveckling över tid, styrkor, förbättringsområden
- [ ] **RBAC** - Elever ser endast sin egen progress
- [ ] **Error handling** - Fel hanteras korrekt

**Low Code Approach:**
- Använd SQL queries för beräkning (enklare)
- Använd middleware för RBAC (enklare auth)

**Tidsestimat:** 3-4 timmar

---

### **FRONTEND UPPGIFTER (2 uppgifter)**

#### **SCRUM-46: Student - Login & Dashboard (Frontend)**

**Beskrivning:** Som elev vill jag logga in och se min dashboard.

**Varför:** Elev behöver en central plats för att se alla uppgifter.

**Detaljerade Steg:**
1. **Skapa Student Login Page** (1 timme)
   - Formulär: Email, Password
   - Validering: Email format, Password required
   - SSO-stub (mock för MVP)

2. **Skapa Student Dashboard Page** (2 timmar)
   - Layout: Header, Sidebar, Main Content
   - Komponenter: Dashboard Stats, Recent Assignments, Recent Feedback

3. **Implementera Dashboard Stats** (1 timme)
   - Totalt antal uppgifter
   - Antal uppgifter som väntar på inlämning
   - Antal uppgifter som är bedömda
   - Anropa Backend API `GET /api/students/:id/assignments`

4. **Implementera Recent Assignments** (1 timme)
   - Lista över 5 senaste uppgifterna
   - Visa titel, deadline, status
   - Anropa Backend API `GET /api/students/:id/assignments?limit=5`

5. **Implementera Recent Feedback** (1 timme)
   - Lista över 5 senaste feedback
   - Visa uppgift, betygsförslag, feedback
   - Anropa Backend API `GET /api/students/:id/submissions?status=published_to_student&limit=5`

6. **Implementera Loading & Error States** (1 timme)
   - Loading spinner
   - Error message
   - Empty state

7. **Testa UI** (1 timme)
   - Testa med riktiga data
   - Testa med tom data
   - Testa med fel

**Acceptance:**
- [ ] **UI: Login Page** - SSO-stub för elev (mock för MVP)
- [ ] **UI: Dashboard** - Översikt över uppgifter, feedback, utveckling
- [ ] **UI: Navigation** - Meny för att navigera mellan sidor
- [ ] **UI: Dashboard Stats** - Totalt antal uppgifter, väntande inlämning, bedömda
- [ ] **UI: Recent Assignments** - Lista över 5 senaste uppgifterna
- [ ] **UI: Recent Feedback** - Lista över 5 senaste feedback
- [ ] **UI: Empty State** - Om inga uppgifter finns
- [ ] **UI: Loading State** - Visa laddning
- [ ] **UI: Error State** - Visa fel om något går snett
- [ ] **Integration** - Anropa Backend API

**Low Code Approach:**
- Använd React + Tailwind CSS (enklare styling)
- Använd React Query eller SWR (enklare data fetching)
- Använd Reusable components (enklare maintenance)

**Tidsestimat:** 8-9 timmar

---

#### **SCRUM-47: Student - Assignments List (Frontend)**

**Beskrivning:** Som elev vill jag se alla mina uppgifter i UI.

**Varför:** Elev behöver se vilka uppgifter som finns.

**Detaljerade Steg:**
1. **Skapa Assignments List Page** (1 timme)
   - Layout: Lista med assignment cards
   - Komponenter: Assignment Card, Filter, Search

2. **Implementera Assignment Card** (1 timme)
   - Visa titel, deadline, status
   - Visa deadline warning (om närmar sig)
   - Anropa Backend API `GET /api/students/:id/assignments`

3. **Implementera Filter & Search** (1 timme)
   - Filtrera per status (pending, in_progress, submitted, graded)
   - Sök efter titel

4. **Implementera Deadline Warning** (30 min)
   - Visa varning om deadline närmar sig (3 dagar)
   - Visa varning om deadline har passerat

5. **Testa UI** (1 timme)
   - Testa filter
   - Testa search
   - Testa deadline warning

**Acceptance:**
- [ ] **UI: Assignments List** - Lista alla uppgifter för elev
- [ ] **UI: Assignment Card** - Visa uppgiftens titel, deadline, status
- [ ] **UI: Filter** - Filtrera per status (pending, in_progress, submitted, graded)
- [ ] **UI: Status Badge** - Visa status med färg
- [ ] **UI: Deadline Warning** - Varning om deadline närmar sig
- [ ] **UI: Loading State** - Loading spinner
- [ ] **UI: Error State** - Error message
- [ ] **Integration** - Anropa Backend API `GET /api/students/:id/assignments`

**Low Code Approach:**
- Använd React Query eller SWR (enklare data fetching)
- Använd Reusable components (enklare maintenance)

**Tidsestimat:** 4.5-5 timmar

---

#### **SCRUM-48: Student - Submit Assignment (Frontend) - Förbättring**

**Beskrivning:** Som elev vill jag kunna lämna in uppgifter i Word, PDF, bilder eller direkt text i UI.

**Varför:** Elev behöver kunna lämna in i olika format, inklusive direkt text input.

**Detaljerade Steg:**
1. **Förbättra Submit Form** (1 timme)
   - Lägg till direkt text input (utöver Word/PDF/bilder)
   - Toggle mellan file upload och text input
   - Validering för båda typer

2. **Implementera Text Input** (1 timme)
   - Textarea för direkt text
   - Word count
   - Auto-save (localStorage)

3. **Testa UI** (30 min)
   - Testa file upload
   - Testa text input
   - Testa toggle

**Acceptance:**
- [ ] **UI: Submit Form** - Formulär för att lämna in uppgift
- [ ] **UI: File Upload** - Upload Word/PDF/bilder
- [ ] **UI: Text Input** - Direkt text input (textarea)
- [ ] **UI: Toggle** - Växla mellan file upload och text input
- [ ] **UI: Drag & Drop** - Drag & drop för filer
- [ ] **UI: File Preview** - Förhandsvisning av filer
- [ ] **UI: Progress Bar** - Visa uppladdningsframsteg
- [ ] **UI: Success Message** - Bekräftelse när uppgift är inlämnad
- [ ] **Integration** - Anropa Backend API `POST /api/assignments/:id/submit`

**Low Code Approach:**
- Använd React Hook Form (enklare form handling)
- Använd react-dropzone (enklare drag & drop)
- Använd localStorage (enklare auto-save)

**Tidsestimat:** 2.5-3 timmar

---

### **PYTHON API UPPGIFTER (1 uppgift)**

#### **SCRUM-49: Python API - Individual Exercise Generator**

**Beskrivning:** Som Python API vill jag kunna generera individuella övningar för elever.

**Varför:** Elever behöver individuella övningar baserat på sin nivå.

**Detaljerade Steg:**
1. **Implementera POST /api/version1/assignments/process/generate-exercise** (2 timmar)
   - Input: `student_id`, `student_level`, `improvement_areas`, `subject`, `level`
   - Validera input
   - Generera övning med LLM
   - Returnera övning med instruktioner, frågor, exempel

2. **Förbättra LLM prompt** (1 timme)
   - Anpassa prompt för elevens nivå
   - Inkludera förbättringsområden
   - Generera konkreta frågor och exempel

3. **Testa endpoint** (1 timme)
   - Testa med riktiga data
   - Testa med olika nivåer
   - Testa med olika förbättringsområden

**Acceptance:**
- [ ] **Endpoint:** `POST /api/version1/assignments/process/generate-exercise`
- [ ] **Input:** Elevens nivå (E/C/A), förbättringsområden, ämne
- [ ] **Output:** Individuell övning med instruktioner, frågor, exempel
- [ ] **Nivåbaserad** - Generera övningar baserat på elevens nivå
- [ ] **Anpassad** - Anpassa övningar till elevens förbättringsområden
- [ ] **Error handling** - Fel hanteras korrekt

**Low Code Approach:**
- Använd LLM prompt engineering (enklare)
- Använd Pydantic för validering (enklare)

**Tidsestimat:** 4-5 timmar

---

#### **SCRUM-50: Backend - Quiz Generator API**

**Beskrivning:** Som backend vill jag ha API för att generera quiz för elever.

**Varför:** Elever behöver quiz för att träna och förbättra sig.

**Detaljerade Steg:**
1. **Skapa databas-schema** (30 min)
   - Tabell: `quizzes`
   - Fält: `id`, `student_id`, `title`, `questions`, `difficulty`, `subject`, `level`, `generated_at`, `completed_at`, `score`, `created_at`, `updated_at`

2. **Implementera POST /api/students/:id/quizzes/generate** (2 timmar)
   - Validera att elev finns
   - Anropa Python API `POST /api/version1/assignments/process/generate-quiz`
   - Spara quiz i databas
   - Returnera 201 med quiz object

3. **Implementera POST /api/quizzes/:id/submit** (1 timme)
   - Validera att quiz finns
   - Räkna score
   - Spara svar och score
   - Returnera 200 med resultat

4. **Implementera GET /api/students/:id/quizzes** (30 min)
   - Validera att elev finns
   - Filtrera per `status` (pending, in_progress, completed)
   - Returnera 200 med lista

5. **Testa endpoints** (1 timme)

**Acceptance:**
- [ ] `POST /api/students/:id/quizzes/generate` - Generera quiz för elev
- [ ] `POST /api/quizzes/:id/submit` - Submit quiz answers och få score
- [ ] `GET /api/students/:id/quizzes` - Lista quiz för elev
- [ ] **Databas-schema** - Quizzes table
- [ ] **RBAC** - Elever ser endast sina quiz
- [ ] **Integration** - Anropa Python API för att generera quiz
- [ ] **Scoring** - Automatisk scoring av quiz

**Tidsestimat:** 5-6 timmar

---

#### **SCRUM-51: Backend - Flashcard Generator API**

**Beskrivning:** Som backend vill jag ha API för att generera flashcards för elever.

**Varför:** Elever behöver flashcards för att memorera och förbättra sig.

**Detaljerade Steg:**
1. **Skapa databas-schema** (30 min)
   - Tabell: `flashcards`
   - Tabell: `flashcard_progress`
   - Fält: `id`, `student_id`, `title`, `cards`, `subject`, `level`, `difficulty`, `generated_at`, `created_at`, `updated_at`

2. **Implementera POST /api/students/:id/flashcards/generate** (2 timmar)
   - Validera att elev finns
   - Anropa Python API `POST /api/version1/assignments/process/generate-flashcards`
   - Spara flashcards i databas
   - Returnera 201 med flashcard set object

3. **Implementera POST /api/flashcards/:id/study** (1 timme)
   - Uppdatera progress (rätt/fel)
   - Returnera 200 med progress data

4. **Implementera GET /api/students/:id/flashcards** (30 min)
   - Validera att elev finns
   - Returnera 200 med lista

5. **Testa endpoints** (1 timme)

**Acceptance:**
- [ ] `POST /api/students/:id/flashcards/generate` - Generera flashcards för elev
- [ ] `POST /api/flashcards/:id/study` - Uppdatera progress när elev studerar
- [ ] `GET /api/students/:id/flashcards` - Lista flashcards för elev
- [ ] **Databas-schema** - Flashcards och Flashcard Progress tables
- [ ] **Progress Tracking** - Spåra elevens progress med flashcards

**Tidsestimat:** 5-6 timmar

---

#### **SCRUM-52: Student - Quiz Generator UI (Frontend)**

**Beskrivning:** Som elev vill jag kunna generera och göra quiz i UI.

**Varför:** Elever behöver quiz för att träna och förbättra sig.

**Detaljerade Steg:**
1. **Skapa Quiz List Page** (1 timme)
   - Lista alla quiz för elev
   - Visa titel, svårighet, status, score
   - Anropa Backend API `GET /api/students/:id/quizzes`

2. **Implementera Generate Quiz** (1 timme)
   - Formulär: Ämne, Svårighet, Antal frågor
   - Anropa Backend API `POST /api/students/:id/quizzes/generate`

3. **Implementera Quiz View** (2 timmar)
   - Visa quiz med frågor och svar-alternativ
   - Radio buttons för multiple choice
   - Submit button
   - Anropa Backend API `POST /api/quizzes/:id/submit`

4. **Implementera Quiz Results** (1 timme)
   - Visa score och feedback
   - Visa rätt/fel svar
   - Visa förbättringsförslag

5. **Testa UI** (1 timme)

**Acceptance:**
- [ ] **UI: Quiz List** - Lista alla quiz för elev
- [ ] **UI: Generate Quiz** - Generera ny quiz
- [ ] **UI: Quiz View** - Visa quiz med frågor och svar
- [ ] **UI: Quiz Results** - Visa score och feedback
- [ ] **Integration** - Anropa Backend API Quiz endpoints

**Tidsestimat:** 6-7 timmar

---

#### **SCRUM-53: Student - Flashcard Generator UI (Frontend)**

**Beskrivning:** Som elev vill jag kunna generera och studera flashcards i UI.

**Varför:** Elever behöver flashcards för att memorera och förbättra sig.

**Detaljerade Steg:**
1. **Skapa Flashcard List Page** (1 timme)
   - Lista alla flashcard sets för elev
   - Visa titel, ämne, progress
   - Anropa Backend API `GET /api/students/:id/flashcards`

2. **Implementera Generate Flashcards** (1 timme)
   - Formulär: Ämne, Antal cards, Svårighet
   - Anropa Backend API `POST /api/students/:id/flashcards/generate`

3. **Implementera Flashcard Study View** (2 timmar)
   - Visa kort med fråga (dölj svar)
   - Flip button för att visa svar
   - Rätta/Fel buttons för att spåra progress
   - Progress bar
   - Anropa Backend API `POST /api/flashcards/:id/study`

4. **Testa UI** (1 timme)

**Acceptance:**
- [ ] **UI: Flashcard List** - Lista alla flashcard sets för elev
- [ ] **UI: Generate Flashcards** - Generera ny flashcard set
- [ ] **UI: Flashcard Study View** - Visa kort med flip-funktion
- [ ] **UI: Flashcard Progress** - Visa progress över tid
- [ ] **Integration** - Anropa Backend API Flashcard endpoints

**Tidsestimat:** 6-7 timmar

---

#### **SCRUM-54: Python API - Quiz Generator**

**Beskrivning:** Som Python API vill jag kunna generera quiz för elever.

**Varför:** Elever behöver quiz för att träna och förbättra sig.

**Detaljerade Steg:**
1. **Implementera POST /api/version1/assignments/process/generate-quiz** (2 timmar)
   - Input: `student_id`, `student_level`, `improvement_areas`, `subject`, `level`, `num_questions`, `difficulty`
   - Generera quiz med LLM
   - Returnera quiz med frågor, svar, korrekta svar

2. **Förbättra LLM prompt för quiz** (1 timme)
   - Anpassa prompt för elevens nivå
   - Generera olika typer av frågor (multiple choice, true/false, open-ended)
   - Inkludera korrekta svar och förklaringar

3. **Testa endpoint** (1 timme)

**Acceptance:**
- [ ] **Endpoint:** `POST /api/version1/assignments/process/generate-quiz`
- [ ] **Input:** Elevens nivå (E/C/A), förbättringsområden, ämne, antal frågor, svårighet
- [ ] **Output:** Quiz med frågor, svar, korrekta svar, förklaringar
- [ ] **Nivåbaserad** - Generera quiz baserat på elevens nivå
- [ ] **Olika typer** - Multiple choice, true/false, open-ended

**Tidsestimat:** 4-5 timmar

---

#### **SCRUM-55: Python API - Flashcard Generator**

**Beskrivning:** Som Python API vill jag kunna generera flashcards för elever.

**Varför:** Elever behöver flashcards för att memorera och förbättra sig.

**Detaljerade Steg:**
1. **Implementera POST /api/version1/assignments/process/generate-flashcards** (2 timmar)
   - Input: `student_id`, `student_level`, `improvement_areas`, `subject`, `level`, `num_cards`, `topic`
   - Generera flashcards med LLM
   - Returnera flashcard set med frågor och svar

2. **Förbättra LLM prompt för flashcards** (1 timme)
   - Anpassa prompt för elevens nivå
   - Generera kortfattade frågor och svar
   - Inkludera exempel och förklaringar

3. **Testa endpoint** (1 timme)

**Acceptance:**
- [ ] **Endpoint:** `POST /api/version1/assignments/process/generate-flashcards`
- [ ] **Input:** Elevens nivå (E/C/A), förbättringsområden, ämne, antal cards, topic
- [ ] **Output:** Flashcard set med frågor och svar
- [ ] **Nivåbaserad** - Generera flashcards baserat på elevens nivå
- [ ] **Kortfattad** - Kortfattade frågor och svar för memorering

**Tidsestimat:** 4-5 timmar

---

## 📊 **SPRINT 5 SAMMANFATTNING**

### **Totalt: 19 uppgifter** (13 ursprungliga + 6 nya)
- **Azure DevOps:** 7 uppgifter (behåll)
- **Backend:** 4 uppgifter (14.5-18 timmar) - **+2 nya**
- **Frontend:** 5 uppgifter (21-24 timmar) - **+2 nya**
- **Python API:** 3 uppgifter (12-15 timmar) - **+2 nya**

### **Total tid:** 47.5-57 timmar (ca 6-7 dagar per person) - **+24-29 timmar**

---

## 🚀 **SPRINT 6: Student Portal + Parent Portal Start**

### **Datum:** 1 december - 5 december (1 vecka)

### **Totalt: 11 uppgifter**

---

### **BACKEND UPPGIFTER (2 uppgifter)**

#### **SCRUM-56: Backend - Parent API**

**Beskrivning:** Som backend vill jag ha endpoints för föräldrar att se sina barns data.

**Varför:** Föräldrar behöver insyn i barnets utveckling.

**Detaljerade Steg:**
1. **Skapa databas-schema** (om inte redan finns) (30 min)
   - Tabell: `parents`
   - Tabell: `parent_student_relationships`

2. **Implementera GET /api/parents/:id/children** (1 timme)
   - Validera att förälder finns
   - Validera att användare är förälder
   - Hämta alla barn för förälder
   - Returnera 200 med lista

3. **Implementera GET /api/parents/:id/children/:childId/progress** (1 timme)
   - Validera att förälder finns
   - Validera att barn finns
   - Validera att förälder har tillgång till barn
   - Hämta progress data för barn
   - Returnera 200 med progress data

4. **Implementera Consent Check** (1 timme)
   - Kontrollera om elev är över 18 år
   - Kontrollera om elev har gett samtycke
   - Returnera 403 om inget samtycke

5. **Testa endpoints** (1 timme)
   - Unit tests
   - Integration tests för RBAC
   - Integration tests för consent

**Acceptance:**
- [ ] `GET /api/parents/:id/children` - Lista barn för förälder
- [ ] `GET /api/parents/:id/children/:childId/progress` - Progress för barn
- [ ] **Databas-schema** - Parents, Parent-Student Relationships tables
- [ ] **RBAC** - Föräldrar ser endast sina barn
- [ ] **Consent check** - Kontrollera om elev är över 18 år och har gett samtycke
- [ ] **Error handling** - Fel hanteras korrekt

**Low Code Approach:**
- Använd JOIN queries (enklare databashämtning)
- Använd middleware för RBAC (enklare auth)
- Använd middleware för consent check (enklare)

**Tidsestimat:** 4.5-5 timmar

---

#### **SCRUM-57: Backend - Consent API**

**Beskrivning:** Som backend vill jag ha endpoints för 18+ elever att ge samtycke.

**Varför:** Elever över 18 år måste ge samtycke innan föräldrar kan se data.

**Detaljerade Steg:**
1. **Skapa databas-schema** (30 min)
   - Tabell: `consents`
   - Fält: `id`, `student_id`, `parent_id`, `consent_given`, `consent_date`, `created_at`, `updated_at`

2. **Implementera POST /api/students/:id/consent** (1 timme)
   - Validera att elev finns
   - Validera att elev är över 18 år
   - Validera att användare är elev själv
   - Spara consent i databas
   - Skicka email till elev för bekräftelse
   - Returnera 200 med consent object

3. **Implementera GET /api/students/:id/consent** (30 min)
   - Validera att elev finns
   - Validera att användare är elev själv eller förälder
   - Hämta consent status
   - Returnera 200 med consent status

4. **Testa endpoints** (1 timme)
   - Unit tests
   - Integration tests för RBAC
   - Integration tests för email

**Acceptance:**
- [ ] `POST /api/students/:id/consent` - Consent för 18+ elever
- [ ] `GET /api/students/:id/consent` - Hämta consent status
- [ ] **Databas-schema** - Consents table
- [ ] **Consent check** - Kontrollera om elev är över 18 år
- [ ] **Email** - Skicka email till elev för bekräftelse
- [ ] **RBAC** - Elever kan ge samtycke, föräldrar kan se status
- [ ] **Error handling** - Fel hanteras korrekt

**Low Code Approach:**
- Använd email service (t.ex. SendGrid, Mailgun) (enklare)
- Använd middleware för RBAC (enklare auth)

**Tidsestimat:** 3-4 timmar

---

### **FRONTEND UPPGIFTER (2 uppgifter)**

#### **SCRUM-58: Student - Feedback View (Frontend)**

**Beskrivning:** Som elev vill jag se feedback efter lärare godkänt i UI.

**Varför:** Elev behöver se vad lärare tycker och hur man kan förbättras.

**Detaljerade Steg:**
1. **Skapa Feedback View Page** (2 timmar)
   - Layout: Header, Main Content
   - Komponenter: Feedback Card, Grade Suggestion, Progress Visualization, Improvement Areas, Strengths

2. **Implementera Feedback Card** (1 timme)
   - Visa feedback text
   - Visa betygsförslag (ej direkt betyg)
   - Anropa Backend API `GET /api/submissions/:id/feedback`

3. **Implementera Grade Suggestion** (1 timme)
   - Visa betygsförslag (t.ex. "C/D")
   - Visa förklaring
   - Visa förbättringsförslag

4. **Implementera Progress Visualization** (1 timme)
   - Progress bars
   - Charts (utveckling över tid)
   - Anropa Backend API `GET /api/students/:id/progress`

5. **Implementera Improvement Areas & Strengths** (1 timme)
   - Lista över förbättringsområden
   - Lista över styrkor

6. **Testa UI** (1 timme)
   - Testa med riktiga data
   - Testa med tom data
   - Testa med fel

**Acceptance:**
- [ ] **UI: Feedback View** - Se feedback efter lärare godkänt
- [ ] **UI: Grade Suggestion** - Se betygsförslag (ej direkt betyg)
- [ ] **UI: Progress Visualization** - Visualisering av utveckling (progress bars, charts)
- [ ] **UI: Improvement Areas** - Se förbättringsområden
- [ ] **UI: Strengths** - Se styrkor
- [ ] **UI: Loading State** - Loading spinner
- [ ] **UI: Error State** - Error message
- [ ] **Integration** - Anropa Backend API `GET /api/submissions/:id/feedback`

**Low Code Approach:**
- Använd Chart.js eller Recharts (enklare charts)
- Använd Reusable components (enklare maintenance)

**Tidsestimat:** 7-8 timmar

---

#### **SCRUM-59: Parent Portal - Start (Frontend)**

**Beskrivning:** Som förälder vill jag ha en portal där jag kan se mitt barns utveckling.

**Varför:** Föräldrar behöver insyn i barnets lärande.

**Detaljerade Steg:**
1. **Skapa Parent Login Page** (1 timme)
   - Formulär: Email, Password
   - Validering: Email format, Password required
   - SSO-stub (mock för MVP)

2. **Skapa Parent Dashboard Page** (2 timmar)
   - Layout: Header, Sidebar, Main Content
   - Komponenter: Child Selection, Child Progress Overview, Recent Assignments, Recent Feedback

3. **Implementera Child Selection** (1 timme)
   - Dropdown för att välja barn (om flera barn)
   - Anropa Backend API `GET /api/parents/:id/children`

4. **Implementera Child Progress Overview** (1 timme)
   - Översikt över barnets utveckling
   - Stats: Totalt antal uppgifter, Antal bedömda uppgifter
   - Anropa Backend API `GET /api/parents/:id/children/:childId/progress`

5. **Implementera Recent Assignments & Feedback** (1 timme)
   - Lista över 5 senaste uppgifterna
   - Lista över 5 senaste feedback
   - Anropa Backend API `GET /api/parents/:id/children/:childId/assignments`

6. **Implementera Consent Check** (1 timme)
   - Kontrollera om elev är över 18 år
   - Visa meddelande om inget samtycke
   - Länk till consent form

7. **Testa UI** (1 timme)
   - Testa med riktiga data
   - Testa med tom data
   - Testa med fel
   - Testa consent check

**Acceptance:**
- [ ] **UI: Parent Login** - SSO-stub för förälder (mock för MVP)
- [ ] **UI: Parent Dashboard** - Översikt över barnets utveckling
- [ ] **UI: Child Selection** - Välja barn (om flera barn)
- [ ] **UI: Child Progress Overview** - Stats: Totalt antal uppgifter, bedömda uppgifter
- [ ] **UI: Recent Assignments** - Lista över 5 senaste uppgifterna
- [ ] **UI: Recent Feedback** - Lista över 5 senaste feedback
- [ ] **UI: Consent Check** - Visa meddelande om inget samtycke (18+ elever)
- [ ] **UI: Loading State** - Loading spinner
- [ ] **UI: Error State** - Error message
- [ ] **Integration** - Anropa Backend API `GET /api/parents/:id/children`

**Low Code Approach:**
- Använd React + Tailwind CSS (enklare styling)
- Använd React Query eller SWR (enklare data fetching)
- Använd Reusable components (enklare maintenance)

**Tidsestimat:** 8-9 timmar

---

#### **SCRUM-60: Parent - Consent UI (Frontend)**

**Beskrivning:** Som elev över 18 år vill jag kunna ge samtycke för att föräldrar kan se min utveckling.

**Varför:** Elever över 18 år måste ge samtycke innan föräldrar kan se deras data.

**Detaljerade Steg:**
1. **Skapa Consent Form** (1 timme)
   - Formulär: Samtycke checkbox, Email bekräftelse
   - Validering: Checkbox required
   - Anropa Backend API `POST /api/students/:id/consent`

2. **Implementera Consent Status** (30 min)
   - Visa om elev har gett samtycke
   - Visa datum för samtycke
   - Anropa Backend API `GET /api/students/:id/consent`

3. **Implementera Email Bekräftelse** (30 min)
   - Visa meddelande om email skickas
   - Visa bekräftelse när samtycke är givet

4. **Testa UI** (30 min)
   - Testa consent form
   - Testa consent status
   - Testa email bekräftelse

**Acceptance:**
- [ ] **UI: Consent Form** - Formulär för att ge samtycke
- [ ] **UI: Consent Checkbox** - Checkbox för att ge samtycke
- [ ] **UI: Consent Status** - Visa om samtycke är givet
- [ ] **UI: Email Bekräftelse** - Visa meddelande om email
- [ ] **UI: Loading State** - Loading spinner
- [ ] **UI: Error State** - Error message
- [ ] **Integration** - Anropa Backend API Consent endpoints

**Low Code Approach:**
- Använd React Hook Form (enklare form handling)
- Använd Reusable components (enklare maintenance)

**Tidsestimat:** 2.5-3 timmar

---

#### **SCRUM-61: Backend - Adaptive Learning Paths API**

**Beskrivning:** Som backend vill jag ha API för anpassade lärandevägar baserat på elevens svagheter.

**Varför:** Elever behöver anpassade lärandevägar för att förbättra sig effektivt.

**Detaljerade Steg:**
1. **Skapa databas-schema** (30 min)
   - Tabell: `learning_paths`
   - Fält: `id`, `student_id`, `path_name`, `steps`, `current_step`, `difficulty`, `subject`, `generated_at`, `completed_at`, `created_at`, `updated_at`

2. **Implementera POST /api/students/:id/learning-paths/generate** (2 timmar)
   - Validera att elev finns
   - Analysera elevens svagheter från submissions
   - Anropa Python API `POST /api/version1/assignments/process/generate-learning-path`
   - Spara learning path i databas
   - Returnera 201 med learning path object

3. **Implementera GET /api/students/:id/learning-paths** (30 min)
   - Validera att elev finns
   - Filtrera per `status` (active, completed)
   - Returnera 200 med lista

4. **Implementera PUT /api/learning-paths/:id/progress** (1 timme)
   - Validera att learning path finns
   - Uppdatera current_step när elev slutför steg
   - Returnera 200 med uppdaterad learning path

5. **Testa endpoints** (1 timme)

**Acceptance:**
- [ ] `POST /api/students/:id/learning-paths/generate` - Generera learning path för elev
- [ ] `GET /api/students/:id/learning-paths` - Lista learning paths för elev
- [ ] `PUT /api/learning-paths/:id/progress` - Uppdatera progress
- [ ] **Databas-schema** - Learning Paths table
- [ ] **RBAC** - Elever ser endast sina learning paths
- [ ] **Integration** - Anropa Python API för att generera learning paths

**Tidsestimat:** 5-6 timmar

---

#### **SCRUM-62: Backend - Study Recommendations API**

**Beskrivning:** Som backend vill jag ha API för studietips baserat på elevens resultat.

**Varför:** Elever behöver konkreta studietips för att förbättra sig.

**Detaljerade Steg:**
1. **Implementera POST /api/students/:id/study-recommendations** (2 timmar)
   - Validera att elev finns
   - Analysera elevens resultat från submissions
   - Anropa Python API `POST /api/version1/assignments/process/generate-study-recommendations`
   - Returnera 200 med study recommendations

2. **Implementera GET /api/students/:id/study-recommendations** (30 min)
   - Validera att elev finns
   - Hämta senaste recommendations
   - Returnera 200 med lista

3. **Testa endpoints** (1 timme)

**Acceptance:**
- [ ] `POST /api/students/:id/study-recommendations` - Generera study recommendations
- [ ] `GET /api/students/:id/study-recommendations` - Hämta study recommendations
- [ ] **RBAC** - Elever ser endast sina recommendations
- [ ] **Integration** - Anropa Python API för att generera recommendations

**Tidsestimat:** 3.5-4 timmar

---

#### **SCRUM-63: Student - Adaptive Learning Paths UI (Frontend)**

**Beskrivning:** Som elev vill jag kunna se och följa anpassade lärandevägar i UI.

**Varför:** Elever behöver anpassade lärandevägar för att förbättra sig effektivt.

**Detaljerade Steg:**
1. **Skapa Learning Paths List Page** (1 timme)
   - Lista alla learning paths för elev
   - Visa path name, progress, status
   - Anropa Backend API `GET /api/students/:id/learning-paths`

2. **Implementera Generate Learning Path** (1 timme)
   - Knapp för att generera ny learning path
   - Anropa Backend API `POST /api/students/:id/learning-paths/generate`

3. **Implementera Learning Path View** (2 timmar)
   - Visa learning path med steg
   - Visa current step
   - Visa progress bar
   - Markera completed steps
   - Anropa Backend API `PUT /api/learning-paths/:id/progress`

4. **Testa UI** (1 timme)

**Acceptance:**
- [ ] **UI: Learning Paths List** - Lista alla learning paths för elev
- [ ] **UI: Generate Learning Path** - Generera ny learning path
- [ ] **UI: Learning Path View** - Visa learning path med steg och progress
- [ ] **UI: Progress Tracking** - Visa progress över tid
- [ ] **Integration** - Anropa Backend API Learning Paths endpoints

**Tidsestimat:** 5-6 timmar

---

#### **SCRUM-64: Student - Study Recommendations UI (Frontend)**

**Beskrivning:** Som elev vill jag kunna se studietips baserat på mina resultat i UI.

**Varför:** Elever behöver konkreta studietips för att förbättra sig.

**Detaljerade Steg:**
1. **Implementera Study Recommendations View** (1 timme)
   - Visa study recommendations
   - Visa tips kategoriserade (t.ex. "Grammar", "Vocabulary", "Writing")
   - Anropa Backend API `GET /api/students/:id/study-recommendations`

2. **Implementera Generate Recommendations** (1 timme)
   - Knapp för att generera nya recommendations
   - Anropa Backend API `POST /api/students/:id/study-recommendations`

3. **Testa UI** (30 min)

**Acceptance:**
- [ ] **UI: Study Recommendations View** - Visa studietips
- [ ] **UI: Generate Recommendations** - Generera nya recommendations
- [ ] **UI: Categorization** - Kategorisera tips (Grammar, Vocabulary, Writing)
- [ ] **Integration** - Anropa Backend API Study Recommendations endpoints

**Tidsestimat:** 2.5-3 timmar

---

### **PYTHON API UPPGIFTER (3 uppgifter)**

#### **SCRUM-65: Python API - Progress Tracking Data**

**Beskrivning:** Som Python API vill jag kunna generera progress tracking data för elever.

**Varför:** Elever behöver se sin utveckling över tid.

**Detaljerade Steg:**
1. **Implementera POST /api/version1/students/:id/progress** (2 timmar)
   - Input: `student_id`, `submissions` (lista av submissions med analyser)
   - Analysera submissions över tid
   - Beräkna progress data (utveckling över tid, styrkor, förbättringsområden)
   - Identifiera trender
   - Returnera progress data

2. **Förbättra trend analysis** (1 timme)
   - Identifiera om elevens nivå förbättras
   - Identifiera om elevens nivå är stabil
   - Identifiera om elevens nivå behöver uppmärksamhet

3. **Testa endpoint** (1 timme)
   - Testa med riktiga data
   - Testa med olika trender
   - Testa med tom data

**Acceptance:**
- [ ] **Endpoint:** `POST /api/version1/students/:id/progress`
- [ ] **Input:** Lista av submissions med analyser
- [ ] **Output:** Progress data (utveckling över tid, styrkor, förbättringsområden)
- [ ] **Visualization Data** - Data för charts och visualiseringar
- [ ] **Trends** - Identifiera trender i elevens utveckling
- [ ] **Error handling** - Fel hanteras korrekt

**Low Code Approach:**
- Använd Python collections.Counter (enklare statistik)
- Använd Pydantic för validering (enklare)

**Tidsestimat:** 4-5 timmar

---

#### **SCRUM-66: Python API - Adaptive Learning Path Generator**

**Beskrivning:** Som Python API vill jag kunna generera anpassade lärandevägar för elever.

**Varför:** Elever behöver anpassade lärandevägar för att förbättra sig effektivt.

**Detaljerade Steg:**
1. **Implementera POST /api/version1/assignments/process/generate-learning-path** (2 timmar)
   - Input: `student_id`, `student_level`, `weaknesses`, `subject`, `level`
   - Analysera svagheter
   - Generera learning path med steg
   - Returnera learning path med steg, övningar, quiz, flashcards

2. **Förbättra LLM prompt för learning paths** (1 timme)
   - Anpassa prompt för elevens nivå
   - Inkludera svagheter
   - Generera konkreta steg med övningar
   - Inkludera progression (från enkel till svår)

3. **Testa endpoint** (1 timme)

**Acceptance:**
- [ ] **Endpoint:** `POST /api/version1/assignments/process/generate-learning-path`
- [ ] **Input:** Elevens nivå (E/C/A), svagheter, ämne
- [ ] **Output:** Learning path med steg, övningar, quiz, flashcards
- [ ] **Anpassad** - Anpassa learning path till elevens svagheter
- [ ] **Progression** - Progression från enkel till svår

**Tidsestimat:** 4-5 timmar

---

#### **SCRUM-67: Python API - Study Recommendations Generator**

**Beskrivning:** Som Python API vill jag kunna generera studietips baserat på elevens resultat.

**Varför:** Elever behöver konkreta studietips för att förbättra sig.

**Detaljerade Steg:**
1. **Implementera POST /api/version1/assignments/process/generate-study-recommendations** (2 timmar)
   - Input: `student_id`, `submissions`, `analysis_results`
   - Analysera elevens resultat
   - Identifiera svagheter och styrkor
   - Generera konkreta studietips
   - Returnera recommendations kategoriserade

2. **Förbättra LLM prompt för recommendations** (1 timme)
   - Anpassa prompt för elevens nivå
   - Inkludera resultat från submissions
   - Generera konkreta, actionable tips
   - Kategorisera tips (Grammar, Vocabulary, Writing, etc.)

3. **Testa endpoint** (1 timme)

**Acceptance:**
- [ ] **Endpoint:** `POST /api/version1/assignments/process/generate-study-recommendations`
- [ ] **Input:** Elevens resultat från submissions och analyser
- [ ] **Output:** Studietips kategoriserade (Grammar, Vocabulary, Writing, etc.)
- [ ] **Konkreta tips** - Actionable, konkreta studietips
- [ ] **Kategorisering** - Kategorisera tips per område

**Tidsestimat:** 4-5 timmar

---

## 📊 **SPRINT 6 SAMMANFATTNING**

### **Totalt: 18 uppgifter** (12 ursprungliga + 6 nya)
- **Azure DevOps:** 6 uppgifter (behåll)
- **Backend:** 4 uppgifter (16-19 timmar) - **+2 nya**
- **Frontend:** 5 uppgifter (25-29 timmar) - **+2 nya**
- **Python API:** 3 uppgifter (12-15 timmar) - **+2 nya**

### **Total tid:** 53-63 timmar (ca 6.5-8 dagar per person) - **+24-29 timmar**

---

## 📊 **TOTALT SAMMANFATTNING**

### **Sprint 4: 17 uppgifter (87.5-104 timmar)** - **+5 nya (Exam, Teaching Materials, Material Generation, Assignment Template)**
- Backend: 8 uppgifter (6 ursprungliga + 2 nya)
- Frontend: 5 uppgifter (3 ursprungliga + 2 nya)
- Python API: 5 uppgifter (3 ursprungliga + 2 nya)

### **Sprint 5: 19 uppgifter (47.5-57 timmar)** - **+6 nya (Quiz & Flashcard)**
- Azure DevOps: 7 uppgifter
- Backend: 4 uppgifter (2 ursprungliga + 2 nya)
- Frontend: 5 uppgifter (3 ursprungliga + 2 nya)
- Python API: 3 uppgifter (1 ursprunglig + 2 nya)

### **Sprint 6: 18 uppgifter (53-63 timmar)** - **+6 nya (Adaptive Learning & Study Recommendations)**
- Azure DevOps: 6 uppgifter
- Backend: 4 uppgifter (2 ursprungliga + 2 nya)
- Frontend: 5 uppgifter (3 ursprungliga + 2 nya)
- Python API: 3 uppgifter (1 ursprunglig + 2 nya)

### **Totalt: 54 uppgifter (199-231 timmar)** - **+17 nya uppgifter**

---

## ✅ **LOW CODE APPROACH SAMMANFATTNING**

### **Backend:**
- ✅ Express.js eller NestJS (enklare routing)
- ✅ Prisma eller TypeORM (enklare ORM)
- ✅ Joi eller Zod (enklare validering)
- ✅ Multer (enklare file upload)
- ✅ HTTPX eller Axios (enklare HTTP client)

### **Frontend:**
- ✅ React + Tailwind CSS (enklare styling)
- ✅ React Query eller SWR (enklare data fetching)
- ✅ React Hook Form (enklare form handling)
- ✅ Chart.js eller Recharts (enklare charts)
- ✅ Reusable components (enklare maintenance)

### **Python API:**
- ✅ Pydantic (enklare validering)
- ✅ FastAPI middleware (enklare middleware)
- ✅ Async/await (enklare async)
- ✅ Python collections.Counter (enklare statistik)

---

**Rekommendation: Denna plan är mycket detaljerad och lätt att använda!** 🚀


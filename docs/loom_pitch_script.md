# Quilora AI — Loom Pitch Script
**Format:** Product pitch / investor demo  
**Target length:** 60–90 seconds  
**Audience:** Investors, recruiters, portfolio viewers

---

## Pre-Recording Checklist

Do these steps *before* you hit record.

- [ ] Backend is running: `uv run python -m uvicorn src.api.main:app --reload`
- [ ] Qdrant is running: `docker run -p 6333:6333 qdrant/qdrant`
- [ ] Frontend is running: `cd frontend && node_modules/.bin/vite --port 3000`
- [ ] Open browser at `http://localhost:3000` — confirm the green health dot is visible
- [ ] The smog document is uploaded and visible in the sidebar
  - If not: drag `docs/` → upload the `.docx` file on screen
- [ ] Run the demo query once privately (cache the embedding so the live take is fast):
  ```
  What problem does this system solve and why do existing approaches fail?
  ```
- [ ] Clear the chat (refresh the page) so it starts blank for the recording
- [ ] Open Admin Panel once, click Analytics tab — confirm it loads cleanly, then go back to chat
- [ ] Set browser zoom to 100%, hide bookmarks bar, use a clean browser profile
- [ ] Loom: set to record browser tab only (not full screen), 1080p

---

## Shot-by-Shot Script

### [0–5s] — Opening hook
**Screen:** Chat window, empty state (the centered icon + example pills visible)  
**Action:** No clicks — just let the UI sit while you speak.

> *"Most organizations are drowning in documents. Finding a specific answer still means reading everything yourself."*

---

### [5–15s] — Upload
**Screen:** Sidebar, Upload Zone  
**Action:** Drag the smog paper `.docx` file onto the upload zone. Watch the filename appear in the sidebar.

> *"With Quilora, you upload any document — PDF, Word, Excel, PowerPoint, 14 formats supported — and it's instantly ready to query."*

*(Don't rush this. The upload animation looks good — let it play.)*

---

### [15–45s] — First query: streaming with inline citations
**Screen:** Chat input  
**Action:** Click the textarea, type the query below, press Enter.

**Query to type:**
```
What problem does this system solve and why do existing approaches fail?
```

**While it streams:**
> *"I'll ask it a question an executive or investor would actually care about."*

*(pause, let the answer stream — point at the screen)*

> *"Watch the inline citations — every claim is tagged [1], [2], [3], traceable directly back to the source passage."*

**Expected answer (for reference — do NOT read this aloud):**
```
The proposed system addresses smog management in South Asia... [1][5]

Existing approaches fail for several reasons:

1. Lack of Mechanisms for Source Attribution: Current systems do not 
   have a reliable way to trace smog episodes... [2][5]

2. Reactive and Isolated Interventions: Most existing strategies are 
   implemented as isolated measures... costly, disruptive... [5]

3. Inadequate Scenario Testing: Decision-makers lack a unified 
   framework for "what-if" scenario testing... [2][5]
...
```
*(The [1][5] badges render as small indigo superscripts — point to them)*

---

### [45–62s] — Expand a source card
**Screen:** Bottom of the AI message, Sources section  
**Action:** The "5 sources" label is already visible. Click **Show more** on Source 1.

> *"Every source is right there. Click any one to read the exact passage the AI used — no hallucinations, full transparency."*

*(Let the expanded content sit for 2–3 seconds so viewers can see it)*

---

### [62–78s] — Admin panel flash
**Screen:** Bottom of sidebar  
**Action:** Click the **⚙ Admin Panel** gear button.  
→ Click the **Analytics** tab (shows 1 query, response time).  
→ Click the **Health** tab (shows provider cards with green dot).

> *"For teams, there's a full admin panel — live provider health, query analytics, and RAG configuration. Production-ready out of the box."*

*(Don't linger — 8 seconds total on admin)*

---

### [78–90s] — Close
**Screen:** Click "Back to Chat" — land on the clean chat UI  
**Action:** No more clicks. Let the UI sit.

> *"Quilora. Document intelligence that cites its sources. Multi-provider LLM routing, real-time streaming, and support for 14 file formats."*

*(optional: end on the chat UI with the answer still visible and source cards open)*

---

## Backup Query

If the first query gives a poor response, use this instead:

```
What are the three most innovative technical contributions of this system?
```

This tends to produce a clean numbered list with strong citations.

---

## Voiceover Timing Guide

| Timestamp | Action | Words |
|-----------|--------|-------|
| 0–5s | Hook | "Most organizations are drowning in documents…" |
| 5–15s | Upload | "With Quilora, you upload any document…" |
| 15–20s | Typing query | "I'll ask it a question an executive would care about." |
| 20–45s | Streaming | "Watch the inline citations — every claim is tagged…" |
| 45–62s | Source expand | "Every source is right there. Click any one…" |
| 62–78s | Admin panel | "For teams, there's a full admin panel…" |
| 78–90s | Close | "Quilora. Document intelligence that cites its sources." |

---

## Tech Stack Callouts (use in description, not voiceover)

- **Backend:** FastAPI + Haystack 2.x RAG pipeline
- **Vector DB:** Qdrant (semantic search)
- **LLM Routing:** aisuite — OpenAI / Anthropic / Groq with automatic fallback
- **Streaming:** Server-Sent Events (SSE), token-by-token
- **Frontend:** React + Vite + Tailwind CSS
- **File formats:** PDF, DOCX, XLSX, PPTX, CSV, JSON, YAML, HTML, MD, TXT, RST + more

---

## Loom Video Description (paste this when uploading)

```
Quilora AI — Document Intelligence Platform

Ask any question about any document and get an accurate, cited answer in seconds.

Built with:
→ FastAPI + Haystack 2.x RAG pipeline
→ Qdrant vector database for semantic search
→ Multi-provider LLM routing (OpenAI / Anthropic / Groq) with automatic fallback
→ Real-time token streaming via SSE
→ React + Vite + Tailwind CSS frontend
→ 14 document formats supported (PDF, DOCX, XLSX, PPTX, CSV, JSON, YAML, HTML...)
→ Admin panel: provider health, usage analytics, live RAG configuration

Every answer includes inline source citations [1][2] with expandable source cards 
showing the exact retrieved passage and relevance score.
```

---

## Tips

- **Speak slowly.** 90 seconds feels short but viewers need time to read the answer as it streams.
- **Don't explain the tech.** Show it working. The citations and streaming do the talking.
- **Do 2–3 takes.** The best one is usually take 2 — you know the flow but haven't lost energy.
- **Trim in Loom.** Cut any hesitation before the first word and after the last.
- **Add captions in Loom** — most people watch without sound on LinkedIn.

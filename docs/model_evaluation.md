# LLM Model Evaluation Report

**28 models · Alpaca / Ollama · Ubuntu, RTX 4080, 64 GB DDR5**
**Date:** March 9, 2026

---

## Methodology

| Parameter | Description |
|-----------|-------------|
| **Total Questions** | 9 (D1–D3, T1–T3, P1–P3) |
| **Score Range** | 1–10 per question |
| **Language (45%)** | D1: TR→DE translation · D2: DE article→TR summary · D3: EN technical article |
| **System / Network (35%)** | T1: Linux port conflict / TR · T2: iptables / EN · T3: Server analysis / DE |
| **Programming (20%)** | P1: Mock/Stub/Fake + code / EN · P2: Hermes pub/sub / TR · P3: Code review / EN |
| **Formula** | `Total = (Lang × 0.45) + (Sys × 0.35) + (Prog × 0.20)` |

### Scoring Criteria

| Score | Meaning |
|-------|---------|
| 9–10 | Reference quality — technical accuracy + language fluency + complete content |
| 7–8  | Good — minor gaps, core questions answered correctly |
| 5–6  | Average — notable gaps or minor technical errors |
| 3–4  | Weak — errors in fundamental concepts or wrong language used |
| 1–2  | Critical failure — wrong language / completely incorrect technical answer |

> **Language rule:** The response language specified in each question is mandatory. Using the wrong language is a critical error.
> **Reference baseline:** Claude's own answers were used as the scoring benchmark.

---

## Overall Ranking

| Rank | Model | Grp | Lang | Sys | Prog | **Total** |
|------|-------|-----|-----:|----:|-----:|----------:|
| 🥇 1 | **ministral-3:latest** | B | 9.67 | 9.67 | 7.33 | **9.20** |
| 🥈 2 | **qwen3:8b** | B | 9.00 | 8.67 | 8.00 | **8.68** |
| 🥉 3 | **deepseek-r1:8b** | B | 8.33 | 9.33 | 8.33 | **8.68** |
| 4 | qwen3-vl:8b | B | 9.00 | 8.33 | 7.67 | **8.50** |
| 5 | qwen3:latest | B | 9.00 | 7.33 | 7.33 | **8.08** |
| 6 | wizardlm2:7b | B | 8.00 | 7.67 | 8.00 | **7.88** |
| 7 | qwen3.5:9b | C | 6.67 | 9.33 | 5.67 | **7.40** |
| 8 | cogito:8b | B | 7.67 | 7.00 | 7.00 | **7.30** |
| 9 | aya:8b | B | 8.00 | 6.67 | 4.67 | **6.87** |
| 10 | granite3-dense:8b | B | 6.33 | 6.67 | 7.33 | **6.65** |
| 11 | granite3.1-dense:8b | B | 4.67 | 8.00 | 7.67 | **6.44** |
| 12 | lfm2:latest | C | 5.33 | 8.00 | 6.00 | **6.40** |
| 13 | codegeex4:9b | C | 5.00 | 6.67 | 7.67 | **6.12** |
| 14 | granite3.3:8b | B | 5.33 | 6.67 | 6.67 | **6.07** |
| 15 | qwen2.5vl:7b | B | 7.33 | 5.00 | 5.00 | **6.05** |
| 16 | deepseek-v2:16b | C | 4.67 | 7.00 | 6.00 | **5.75** |
| 17 | phi4-mini:3.8b | A | 3.67 | 7.00 | 7.00 | **5.50** |
| 18 | granite4:3b | A | 3.33 | 7.00 | 7.00 | **5.35** |
| 19 | llama3.1:latest | B | 3.33 | 7.00 | 6.33 | **5.21** |
| 20 | qwen2:7b | B | 5.67 | 4.67 | 4.67 | **5.12** |
| 21 | granite3.2:8b | B | 4.00 | 5.00 | 6.67 | **4.88** |
| 22 | granite4:latest | A | 3.33 | 5.00 | 6.00 | **4.45** |
| 23 | llama3.2:latest | A | 3.33 | 5.33 | 5.33 | **4.43** |
| 24 | yi:6b | B | 3.33 | 4.33 | 5.33 | **4.08** |
| 25 | granite3.1-moe:3b | A | 3.67 | 3.00 | 5.00 | **3.70** |
| 26 | minicpm-v:8b | B | 3.33 | 2.67 | 3.33 | **3.10** |
| 27 | deepscaler:latest | A | 2.67 | 1.33 | 1.67 | **2.00** |
| 28 | phi4-reasoning:latest | C | 3.00 | 1.00 | 1.33 | **1.97** |
| — | *Claude (Reference)* | REF | 10.00 | 10.00 | 10.00 | **10.00** |

---

## Score Table — All Questions

> D1=TR→DE · D2=DE→TR · D3=EN Article · T1=Nginx/TR · T2=iptables/EN · T3=Server/DE · P1=Mock/EN · P2=Hermes/TR · P3=CodeRev/EN

| Model | Grp | D1 | D2 | D3 | T1 | T2 | T3 | P1 | P2 | P3 | Lang | Sys | Prog | **Total** | Time |
|-------|-----|----|----|----|----|----|----|----|----|-----|------|-----|------|-----------|------|
| **ministral-3:latest** | B | 10 | 9 | 10 | 9 | 10 | 10 | 9 | 3 | 10 | 9.67 | 9.67 | 7.33 | **9.20** | ~4-51s |
| **qwen3:8b** | B | 9 | 9 | 9 | 9 | 8 | 9 | 8 | 8 | 8 | 9.00 | 8.67 | 8.00 | **8.68** | ~354s |
| **deepseek-r1:8b** | B | 9 | 7 | 9 | 9 | 10 | 9 | 9 | 7 | 9 | 8.33 | 9.33 | 8.33 | **8.68** | ~39s |
| qwen3-vl:8b | B | 9 | 9 | 9 | 8 | 9 | 8 | 8 | 7 | 8 | 9.00 | 8.33 | 7.67 | **8.50** | ~631s |
| qwen3:latest | B | 9 | 9 | 9 | 8 | 5 | 9 | 7 | 6 | 9 | 9.00 | 7.33 | 7.33 | **8.08** | ~16-62s |
| wizardlm2:7b | B | 7 | 8 | 9 | 7 | 8 | 8 | 9 | 7 | 8 | 8.00 | 7.67 | 8.00 | **7.88** | ~19s |
| qwen3.5:9b | C | 1 | 9 | 10 | 9 | 9 | 10 | 7 | 1 | 9 | 6.67 | 9.33 | 5.67 | **7.40** | ~90s |
| cogito:8b | B | 7 | 8 | 8 | 6 | 8 | 7 | 8 | 5 | 8 | 7.67 | 7.00 | 7.00 | **7.30** | ~83s |
| aya:8b | B | 8 | 8 | 8 | 6 | 8 | 6 | 5 | 7 | 2 | 8.00 | 6.67 | 4.67 | **6.87** | ~12s |
| granite3-dense:8b | B | 7 | 5 | 7 | 5 | 8 | 7 | 8 | 6 | 8 | 6.33 | 6.67 | 7.33 | **6.65** | ~8s |
| granite3.1-dense:8b | B | 1 | 5 | 8 | 7 | 9 | 8 | 9 | 6 | 8 | 4.67 | 8.00 | 7.67 | **6.44** | ~12s |
| lfm2:latest | C | 1 | 7 | 8 | 8 | 7 | 9 | 3 | 6 | 9 | 5.33 | 8.00 | 6.00 | **6.40** | ~26s |
| codegeex4:9b | C | 1 | 6 | 8 | 5 | 7 | 8 | 8 | 7 | 8 | 5.00 | 6.67 | 7.67 | **6.12** | ~14s |
| granite3.3:8b | B | 1 | 7 | 8 | 7 | 7 | 6 | 7 | 6 | 7 | 5.33 | 6.67 | 6.67 | **6.07** | ~130s |
| qwen2.5vl:7b | B | 8 | 7 | 7 | 6 | 5 | 4 | 6 | 7 | 2 | 7.33 | 5.00 | 5.00 | **6.05** | ~57s |
| deepseek-v2:16b | C | 1 | 5 | 8 | 7 | 8 | 6 | 8 | 6 | 4 | 4.67 | 7.00 | 6.00 | **5.75** | ~145s |
| phi4-mini:3.8b | A | 1 | 3 | 7 | 8 | 7 | 6 | 7 | 7 | 7 | 3.67 | 7.00 | 7.00 | **5.50** | ~44s |
| granite4:3b | A | 1 | 2 | 7 | 7 | 7 | 7 | 7 | 7 | 7 | 3.33 | 7.00 | 7.00 | **5.35** | ~56s |
| llama3.1:latest | B | 1 | 1 | 8 | 8 | 6 | 7 | 7 | 4 | 8 | 3.33 | 7.00 | 6.33 | **5.21** | ~9s |
| qwen2:7b | B | 7 | 3 | 7 | 3 | 4 | 7 | 7 | 5 | 2 | 5.67 | 4.67 | 4.67 | **5.12** | ~10s |
| granite3.2:8b | B | 1 | 3 | 8 | 1 | 8 | 6 | 7 | 6 | 7 | 4.00 | 5.00 | 6.67 | **4.88** | ~110s |
| granite4:latest | A | 1 | 1 | 8 | 5 | 4 | 6 | 8 | 4 | 6 | 3.33 | 5.00 | 6.00 | **4.45** | ~7s |
| llama3.2:latest | A | 1 | 2 | 7 | 5 | 5 | 6 | 7 | 4 | 5 | 3.33 | 5.33 | 5.33 | **4.43** | ~5s |
| yi:6b | B | 1 | 2 | 7 | 3 | 5 | 5 | 6 | 5 | 5 | 3.33 | 4.33 | 5.33 | **4.08** | ~17s |
| granite3.1-moe:3b | A | 2 | 2 | 7 | 2 | 3 | 4 | 5 | 3 | 7 | 3.67 | 3.00 | 5.00 | **3.70** | ~26s |
| minicpm-v:8b | B | 1 | 2 | 7 | 2 | 4 | 2 | 2 | 3 | 5 | 3.33 | 2.67 | 3.33 | **3.10** | ~4s |
| deepscaler:latest | A | 1 | 1 | 6 | 1 | 1 | 2 | 2 | 1 | 2 | 2.67 | 1.33 | 1.67 | **2.00** | ~14s |
| phi4-reasoning:latest | C | 4 | 4 | 1 | 1 | 1 | 1 | 1 | 2 | 1 | 3.00 | 1.00 | 1.33 | **1.97** | ~120s |
| *Claude (Reference)* | REF | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 10.00 | 10.00 | 10.00 | **10.00** | — |

---

## Group Rankings

### Group A — Small (1.9B–4B)

| Rank | Model | Lang | Sys | Prog | Total |
|------|-------|-----:|----:|-----:|------:|
| A1 | phi4-mini:3.8b | 3.67 | 7.00 | 7.00 | **5.50** |
| A2 | granite4:3b | 3.33 | 7.00 | 7.00 | **5.35** |
| A3 | granite4:latest | 3.33 | 5.00 | 6.00 | **4.45** |
| A4 | llama3.2:latest | 3.33 | 5.33 | 5.33 | **4.43** |
| A5 | granite3.1-moe:3b | 3.67 | 3.00 | 5.00 | **3.70** |
| A6 | deepscaler:latest | 2.67 | 1.33 | 1.67 | **2.00** |

### Group B — Medium (4.5B–8B)

| Rank | Model | Lang | Sys | Prog | Total |
|------|-------|-----:|----:|-----:|------:|
| B1 | ministral-3:latest | 9.67 | 9.67 | 7.33 | **9.20** |
| B2 | qwen3:8b | 9.00 | 8.67 | 8.00 | **8.68** |
| B3 | deepseek-r1:8b | 8.33 | 9.33 | 8.33 | **8.68** |
| B4 | qwen3-vl:8b | 9.00 | 8.33 | 7.67 | **8.50** |
| B5 | qwen3:latest | 9.00 | 7.33 | 7.33 | **8.08** |
| B6 | wizardlm2:7b | 8.00 | 7.67 | 8.00 | **7.88** |
| B7 | cogito:8b | 7.67 | 7.00 | 7.00 | **7.30** |
| B8 | aya:8b | 8.00 | 6.67 | 4.67 | **6.87** |
| B9 | granite3-dense:8b | 6.33 | 6.67 | 7.33 | **6.65** |
| B10 | granite3.1-dense:8b | 4.67 | 8.00 | 7.67 | **6.44** |
| B11 | granite3.3:8b | 5.33 | 6.67 | 6.67 | **6.07** |
| B12 | qwen2.5vl:7b | 7.33 | 5.00 | 5.00 | **6.05** |
| B13 | llama3.1:latest | 3.33 | 7.00 | 6.33 | **5.21** |
| B14 | qwen2:7b | 5.67 | 4.67 | 4.67 | **5.12** |
| B15 | granite3.2:8b | 4.00 | 5.00 | 6.67 | **4.88** |
| B16 | yi:6b | 3.33 | 4.33 | 5.33 | **4.08** |
| B17 | minicpm-v:8b | 3.33 | 2.67 | 3.33 | **3.10** |

### Group C — Large (9B–16B)

| Rank | Model | Lang | Sys | Prog | Total |
|------|-------|-----:|----:|-----:|------:|
| C1 | qwen3.5:9b | 6.67 | 9.33 | 5.67 | **7.40** |
| C2 | lfm2:latest | 5.33 | 8.00 | 6.00 | **6.40** |
| C3 | codegeex4:9b | 5.00 | 6.67 | 7.67 | **6.12** |
| C4 | deepseek-v2:16b | 4.67 | 7.00 | 6.00 | **5.75** |
| C5 | phi4-reasoning:latest | 3.00 | 1.00 | 1.33 | **1.97** |

---

## Notable Findings

### Critical Errors

| Model | Question | Score | Error |
|-------|----------|-------|-------|
| deepscaler:latest | T1 | 1 | Morse code output — completely irrelevant |
| deepscaler:latest | T2 | 1 | Nonexistent flags; infinite 0.0.0.0... repetition |
| phi4-reasoning:latest | All | 1–4 | Think block hit 120s timeout on every question, no answers produced |
| granite3.2:8b | T1 | 1 | Suggested adding `IncludeOptional nginx.conf` inside Apache config — dangerous nonsense |
| qwen2:7b | T1 | 3 | No commands provided, only commentary |
| qwen2:7b | P3 | 2 | `replace("'","''")` as SQL injection fix — injection still possible |
| aya:8b | P3 | 2 | Did not fix f-string SQL injection |
| qwen2.5vl:7b | T2 | 5 | `OUTPUT DROP` kills all outgoing traffic; ESTABLISHED rule missing |
| lfm2:latest | P1 | 3 | `from unittest.mock import Stub` — Stub does not exist, causes ImportError |
| ministral-3:latest | P2 | 3 | Wrote C++ code — question asked for Python |
| qwen3:latest | T2 | 5 | FORWARD ACCEPT security hole; ESTABLISHED rule missing |
| qwen3.5:9b | D1 | 1 | 120s timeout, no response |
| qwen3.5:9b | P2 | 1 | 120s timeout, no response |

### Highlights

| Model | Question | Score | Note |
|-------|----------|-------|------|
| ministral-3:latest | D1 | 10 | Provided two alternative German translations |
| ministral-3:latest | D3 | 10 | Most comprehensive — includes multi-model DB (Couchbase) |
| ministral-3:latest | T2 | 10 | loopback + ESTABLISHED + SSH + HTTP/HTTPS + netfilter + ufw alternative |
| ministral-3:latest | T3 | 10 | Table + cron script + netdata + vmstat + iostat — outstanding German |
| ministral-3:latest | P3 | 10 | type hints + docstring + timeout + explicit columns + validation |
| deepseek-r1:8b | T2 | 10 | Most comprehensive iptables answer in the entire test series |
| qwen3.5:9b | D3 | 10 | CAP theorem + polyglot persistence — best D3 answer |
| qwen3.5:9b | T3 | 10 | German: du + dmesg + SMART + journalctl + LVM — very comprehensive |
| granite3.1-dense:8b | T2 | 9 | Best iptables-persistent Ubuntu-compatible answer in its series |

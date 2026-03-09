# Which Model to Choose and When?

**28 models · Alpaca / Ollama · Ubuntu, RTX 4080, 64 GB DDR5 · March 9, 2026**
**Scoring weights: Language 45% · System 35% · Programming 20%**

---

## 🌐 All-Round Assistant — Turkish · German · English + Technical

> Best choice when you need multilingual fluency **and** technical depth in the same session.

| Model | Score | Best Used For | Watch Out |
|-------|------:|---------------|-----------|
| **ministral-3:latest** | **9.20** | Top score in both language and system categories. German translation, iptables, log analysis, code review — all consistent. Very natural Turkish output. | Wrote C++ instead of Python for P2. Hermes API unknown. |
| **qwen3:latest** | **8.08** | Larger version of qwen3:8b; seamless language switching, strong technical articles. Versatile everyday assistant. | FORWARD ACCEPT security hole in T2. Marginal gain over qwen3:8b. |
| **deepseek-r1:8b** | **8.68** | Technical problems requiring step-by-step reasoning. Highest iptables score (10/10). Debugging and architecture decisions. | Slow responses. Heavy for casual chat. Turkish output slightly stiff. |
| **wizardlm2:7b** | **7.88** | Explanatory tasks: SQL/NoSQL differences, testing strategy, code explanation. Balanced and reliable. | ESTABLISHED rule missing (T2). Limited on large codebases. |

---

## 🔧 English Technical Support — Code · Linux · Networking

> Use when the task is purely technical and response language is always English.

| Model | Score | Best Used For | Watch Out |
|-------|------:|---------------|-----------|
| **qwen3:8b** | **8.68** | Linux troubleshooting, iptables, nginx errors, Python code review. Reliable and fast technical answers. | Weak Turkish/German. Do not use for multilingual tasks. |
| **qwen3-vl:8b** | **8.50** | Technical tasks and visual (vision) tasks. Strong on English code and system questions. Close to qwen3:8b. | Weak Turkish. Prefer qwen3:8b for non-vision tasks. |
| **codegeex4:9b** | **6.12** | Code review, SQLite issues, Python best practices. Consistent on programming-focused tasks. | Translated to English for D1. Not suitable for any language tasks. |
| **granite3-dense:8b** | **6.65** | IBM-based, enterprise Linux environments. Correct iptables-save usage. Tasks where technical accuracy is priority. | Weak language category (6.33). No Turkish/German expected. |

---

## 🇹🇷 Turkish-Primary Chat & General Use

> Best when the primary interface language is Turkish.

| Model | Score | Best Used For | Watch Out |
|-------|------:|---------------|-----------|
| **ministral-3:latest** | **9.20** | Most natural Turkish output in the test. Excellent at explaining technical topics in Turkish. Conversational tone is fluid. | See All-Round category. Same model, ranks first in both. |
| **qwen3:latest** | **8.08** | Turkish technical explanations and troubleshooting. Emoji and heading use makes responses easy to scan. | See All-Round. FORWARD ACCEPT security issue in T2. |
| **aya:8b** | **6.87** | Designed for multilingual use including Turkish. Adequate for basic conversation and general questions. | Did not fix SQL injection (P3=2). Do not use for critical technical tasks. |
| **cogito:8b** | **7.30** | Natural conversational tone, balanced general assistant. Acceptable Turkish technical explanations. | Used RabbitMQ instead of Hermes (P2). Limited library knowledge. |

---

## ⚡ Low System Resources — CPU-Only Environments

> When GPU is unavailable or RAM is constrained (< 8 GB).

| Model | Score | Best Used For | Watch Out |
|-------|------:|---------------|-----------|
| **phi4-mini:3.8b** | **5.50** | Most balanced small model at 3.8B parameters. Reasonable answers on technical issues (T1, T2). Runs without GPU. | German translation failed (D1=1). No language tasks expected. |
| **granite4:3b** | **5.35** | IBM-based small model. Technical score close to phi4-mini. Adequate for simple enterprise tasks without GPU. | D1/D2 completely wrong language. Language capability near zero. |

---

## 🚫 Do Not Use — Based on Test Results

| Model | Score | Reason |
|-------|------:|--------|
| **phi4-reasoning:latest** | **1.97** | Every question hit the 120s timeout. Think block exhausted before generating any answer. Completely unsuitable for production use. |
| **deepscaler:latest** | **2.00** | Morse code output for T1. Nonexistent flags in T2. Lowest technical score across all categories. |
| **qwen2.5vl:7b** | **6.05** | Vision model, not optimized for text tasks. OUTPUT DROP in T2 kills all outgoing traffic. Use qwen3 for text-only work. |

---

## ⚡ Quick Selection Guide

| Situation / Scenario | Recommended Model |
|----------------------|-------------------|
| Turkish technical question + German translation at the same time | **ministral-3:latest** |
| Linux troubleshooting, iptables, nginx | **qwen3:8b** or **deepseek-r1:8b** |
| Step-by-step debugging (reasoning required) | **deepseek-r1:8b** |
| Python code review + security analysis | **ministral-3:latest** or **qwen3:latest** |
| Turkish everyday chat assistant | **qwen3:latest** or **cogito:8b** |
| English technical article / explanation | **wizardlm2:7b** |
| No GPU, low RAM (< 8 GB) | **phi4-mini:3.8b** |
| Image + text analysis combined | **qwen3-vl:8b** or minicpm-v:8b* |
| Speed-first, simple Q&A | **granite4:3b** or **phi4-mini:3.8b** |

> \* minicpm-v:8b scored low overall (3.10) but was not separately evaluated on vision-specific tasks.

---

## Category Summary by Score

```
All-Round        ministral-3 (9.20) > deepseek-r1 (8.68) > qwen3 (8.68) > wizardlm2 (7.88)
EN Technical     qwen3:8b (8.68) > qwen3-vl (8.50) > granite3-dense (6.65) > codegeex4 (6.12)
Turkish-Primary  ministral-3 (9.20) > qwen3:latest (8.08) > cogito (7.30) > aya (6.87)
Low Resource     phi4-mini (5.50) > granite4:3b (5.35)
Do Not Use       phi4-reasoning (1.97) · deepscaler (2.00) · qwen2.5vl* (6.05)
```

---

*Full per-question scores and detailed error notes: see `model_evaluation.md`*

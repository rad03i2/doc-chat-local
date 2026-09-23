# Doc Chat Local

Private, deterministic document search and extractive Q&A that runs on your computer and cites the source passage.

## English

### Overview
Doc Chat Local indexes local **TXT, Markdown and text-based PDF** files, ranks relevant passages with a lightweight TF-IDF/cosine engine, and returns cited extracts. It exists for people who need useful document retrieval without uploading private files or requiring an API key, cloud account, vector database, or model download.

### Features
- Recursive folder ingestion for `.txt`, `.md`, `.pdf`.
- Unicode tokenization including Arabic and English.
- Configurable overlapping chunks.
- Deterministic TF-IDF/cosine ranking.
- Extractive `ask` mode with source path, chunk number and relevance score.
- Portable UTF-8 JSON indexes; build once, search repeatedly.
- CLI and Python API; no network calls or telemetry.
- Clear validation and non-zero CLI exit code on operational errors.

### Preview
```text
$ doc-chat ask doc-index.json "How is privacy protected?"
Most relevant passages (extractive answer):

[1] Documents are processed locally and are never uploaded...
Source: docs/privacy.md#chunk-0 (score 0.412)
```
This is terminal software; screenshots are optional. A terminal capture showing `build`, `search`, and `ask` is the most useful project preview.

### Requirements & installation
Python 3.10+. PDF extraction uses `pypdf`.
```bash
git clone https://github.com/rad03i2/doc-chat-local.git
cd doc-chat-local
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -e .
```

### Usage
```bash
doc-chat build ./docs -o doc-index.json
doc-chat search doc-index.json "backup policy" -n 5
doc-chat ask doc-index.json "Where are backups stored?" -n 3
python -m doc_chat_local --version
```
Tune ingestion when needed:
```bash
doc-chat build report.pdf notes.md --chunk-size 1200 --overlap 180 -o work.json
```

Python API:
```python
from pathlib import Path
from doc_chat_local import DocumentIndex
index = DocumentIndex.from_paths([Path("notes.md")])
print(index.answer("What are the main findings?"))
```

### Configuration
There are no environment variables or secrets. `--chunk-size` defaults to 900 characters and `--overlap` to 120. Search/ask `--limit` controls returned passages.

### Project structure
```text
src/doc_chat_local/core.py   indexing, persistence, retrieval
src/doc_chat_local/cli.py    command-line interface
tests/test_core.py           functional/unit tests
.github/workflows/ci.yml     cross-platform CI
```

### Testing
```bash
python -m pip install -e '.[dev]'
python -m compileall -q src
pytest -q
```
CI runs these checks on supported Python versions.

### Security & privacy
Processing is local; the application makes no network requests. The JSON index contains document text, so protect it like the original documents and do not commit private indexes. See `SECURITY.md`.

### Limitations
This is retrieval and **extractive Q&A**, not a generative LLM: it returns relevant source passages rather than inventing synthesized answers. Scanned/image-only PDFs require OCR before indexing. PDF extraction quality depends on the PDF text layer. Ranking is lexical, so semantic paraphrases without shared terms can be missed. Very large corpora are held in memory during search.

### Optional roadmap
Optional future work may include BM25 ranking, incremental indexes, OCR adapters, and an opt-in local-model synthesis layer that preserves citations.

### Contributing
See `CONTRIBUTING.md`. Keep changes local-first, tested, and free of secrets.

### License
MIT License — see `LICENSE`.

### Author
**Radwan Abdulhadi Ahmed**  
**رضوان عبدالهادي أحمد**  
GitHub: **@rad03i2**

---

## العربية

### نظرة عامة
**Doc Chat Local** أداة محلية لفهرسة ملفات TXT وMarkdown وملفات PDF النصية، ثم البحث داخلها والإجابة الاستخراجية عبر إرجاع المقاطع الأكثر صلة مع ذكر المصدر ورقم المقطع. صُممت لمن يريد البحث في مستنداته الخاصة من دون رفعها إلى خدمة سحابية أو استخدام مفتاح API أو قاعدة بيانات متجهات.

### لماذا المشروع؟
البحث اليدوي داخل مجموعة مستندات بطيء، بينما إرسال الملفات الخاصة إلى خدمات خارجية قد لا يكون مناسبًا. يقدم المشروع طبقة استرجاع خفيفة وحتمية تعمل بالكامل على الجهاز.

### الميزات
- قراءة المجلدات بشكل متكرر ودعم TXT وMD وPDF النصي.
- دعم Unicode والعربية والإنجليزية.
- تقسيم متداخل قابل للضبط.
- ترتيب TF-IDF مع cosine similarity.
- وضعي `search` و`ask` مع المصدر والدرجة ورقم المقطع.
- حفظ الفهرس بصيغة JSON محمولة UTF-8.
- CLI وPython API بلا اتصالات شبكة أو تتبع.
- تحقق واضح من المدخلات وأكواد خروج مناسبة للأخطاء.

### التثبيت والمتطلبات
يتطلب Python 3.10 أو أحدث:
```bash
git clone https://github.com/rad03i2/doc-chat-local.git
cd doc-chat-local
python -m venv .venv
python -m pip install -e .
```

### الاستخدام
```bash
doc-chat build ./docs -o doc-index.json
doc-chat search doc-index.json "سياسة النسخ الاحتياطي" -n 5
doc-chat ask doc-index.json "أين تحفظ النسخ الاحتياطية؟" -n 3
```
ومن Python يمكن إنشاء `DocumentIndex` عبر `from_paths()` ثم استخدام `search()` أو `answer()`.

### الإعداد
لا توجد متغيرات بيئة أو أسرار. حجم المقطع الافتراضي 900 حرف والتداخل 120 حرفًا، ويمكن تغييرهما أثناء `build`، كما يحدد `--limit` عدد النتائج.

### بنية المشروع والاختبارات
المحرك في `src/doc_chat_local/core.py`، والواجهة في `cli.py`، والاختبارات في `tests/`. للتأكد محليًا:
```bash
python -m pip install -e '.[dev]'
python -m compileall -q src
pytest -q
```

### الأمان والخصوصية
المعالجة محلية ولا تنفذ الأداة أي طلب شبكي. يحتوي ملف الفهرس على نصوص من المستندات، لذلك يجب حمايته مثل الملفات الأصلية وعدم رفع فهارس خاصة إلى Git. راجع `SECURITY.md`.

### القيود
الأداة ليست نموذجًا لغويًا توليديًا؛ الإجابة استخراجية ومسنودة بمقاطع المصدر. ملفات PDF الممسوحة كصور تحتاج OCR مسبقًا، وجودة الاستخراج تعتمد على طبقة النص. البحث معجمي وقد لا يلتقط إعادة الصياغة التي لا تشترك في كلمات، كما أن الفهارس الكبيرة تُحمّل إلى الذاكرة أثناء البحث.

### التطوير الاختياري
يمكن مستقبلًا إضافة BM25، فهرسة تدريجية، محولات OCR، أو طبقة نموذج محلي اختيارية مع الحفاظ على الاستشهادات.

### المساهمة والترخيص
راجع `CONTRIBUTING.md`. المشروع مرخص وفق MIT في `LICENSE`.

### المؤلف
**Radwan Abdulhadi Ahmed**  
**رضوان عبدالهادي أحمد**  
GitHub: **@rad03i2**

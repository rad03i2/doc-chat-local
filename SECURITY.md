# Security Policy

## Supported version
The latest `main` branch and latest release are supported.

## Privacy model
Doc Chat Local does not intentionally make network requests. Index files contain extracted source text and may therefore be sensitive. Store them with permissions appropriate for the original documents, never commit confidential indexes, and delete obsolete indexes when no longer needed.

PDF parsing handles untrusted structured input. Keep `pypdf` updated and process untrusted files with normal OS-level isolation when the risk warrants it. This project does not provide malware scanning, OCR sandboxing, encryption, or access control.

## Reporting
Please report security issues privately through GitHub's security reporting features when available. Do not publish sensitive document samples, credentials, or exploit details in public issues.

## سياسة الأمان
الأداة تعمل محليًا، لكن ملفات الفهرس تحتوي نصوصًا مستخرجة وقد تكون حساسة. لا ترفع فهارس خاصة إلى المستودع، وحدّث `pypdf` بانتظام، واستخدم عزل النظام عند معالجة ملفات غير موثوقة عالية الخطورة.

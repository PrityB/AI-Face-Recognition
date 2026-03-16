# ADR 001: Machine Learning Architecture for KYC

## Status
Accepted

## Context
We need to design a scalable and accurate ML architecture for an identity verification platform. The core requirements include face recognition (1:1 matching), liveness detection (anti-spoofing), document OCR, and fraud risk scoring. The system must process images quickly to provide real-time feedback to mobile users while remaining secure against sophisticated spoofing attacks (e.g., printed photos, high-res iPads).

## Decision

We have decided to decompose the ML pipeline into **Specialized Micro-Models** orchestrated by a FastAPI inference server, rather than relying on a single monolithic model or external SaaS APis.

### 1. Face Recognition (FaceNet + MTCNN)
- **Why**: PyTorch `facenet-pytorch` provides production-ready implementations of MTCNN (for precise face alignment and cropping) and InceptionResnetV1 (for 512D embeddings).
- **Scale**: Embeddings are fixed-size vectors, allowing for incredibly fast cosine-similarity computing ($O(N)$) without needing GPU acceleration for the matching phase itself.

### 2. Liveness Detection (Custom CNN + Heuristics)
- **Why**: Liveness is highly vulnerable to domain shift. We use a hybrid approach:
  1. A fast **Texture Analyzer** (Laplacian variance) to instantly reject blurry or obviously printed photos.
  2. A **MobileNetV2** CNN trained on anti-spoofing datasets (like CelebA-Spoof) to detect subtle screen moiré patterns or depth irregularities.
- **Why MobileNetV2**: MobileNet is lightweight enough to run rapidly on CPU or GPU instances in ECS Fargate without requiring expensive dedicated instances.

### 3. Document Processing (Resizing + Tesseract)
- **Why**: While cloud OCR (AWS Textract/Google Vision) is powerful, it introduces data privacy concerns for PII (Personally Identifiable Information). By building our own OpenCV + Tesseract pipeline, PII never leaves our controlled ECS containers.

### 4. Fraud Risk Scoring (Gradient Boosting + Isolation Forest)
- **Why**: Fraud patterns change constantly. A rule-based system is too brittle.
- **Decision**: We use an Isolation Forest to detect unknown/novel anomalies (unsupervised) and Gradient Boosting for known fraud patterns (supervised).

## Consequences

### Positive
- **Data Privacy**: Complete ownership of the biometric and PII data flow. No third-party API exposure.
- **Modularity**: We can swap out the Liveness CNN for a better one later without touching the Face Recognition code.
- **Cost**: Open-source models running on our own infrastructure are vastly cheaper at scale than paying per-API-call to managed ML providers.

### Negative
- **Maintenance**: We are responsible for fine-tuning the models when accuracy drops (e.g. lighting conditions change).
- **GPU Requirements**: Training the Liveness and FaceNet models requires heavy GPU usage, hence the need for the AWS SageMaker terraform modules.

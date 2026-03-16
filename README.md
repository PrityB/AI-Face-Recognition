![AI Identity Verification Platform Banner](assets/banner.png)

# AI-Powered Identity Verification & Compliance Platform

An end-to-end, cloud-native AI platform for real-time identity verification, fraud detection, and KYC compliance.

![Platform Overview](https://img.shields.io/badge/Status-In%20Development-yellow)
![Tech Stack](https://img.shields.io/badge/Python-FastAPI%20%7C%20PyTorch-blue)
![Tech Stack](https://img.shields.io/badge/Android-Kotlin%20%7C%20Compose-green)
![Tech Stack](https://img.shields.io/badge/Infrastructure-AWS%20%7C%20Terraform-orange)

## Features

- **Face Recognition**: Accurate 1:1 facial matching using FaceNet/dlib embeddings.
- **Liveness Detection**: Anti-spoofing CNN to detect print attacks and 2D spoofing.
- **Document OCR**: Automated extraction of text from ID cards and passports (Tesseract).
- **Fraud Risk Scoring**: Real-time risk assessment using ML anomaly detection.
- **Mobile SDK**: Android native app for secure image/video capture using ML Kit.
- **Cloud Infrastructure**: Scalable AWS backend provisioned with Terraform (ECS Fargate, SageMaker).

## Architecture

This platform consists of 4 main components:

1. **AI/ML Engine (`ai-engine/`)**: PyTorch models, inference pipeline, and distributed training scripts.
2. **Backend API (`backend/`)**: FastAPI service Orchestrating KYC workflows and connecting to the DB.
3. **Android App (`android-app/`)**: Native Kotlin app guiding the user through the verification flow.
4. **Cloud Infrastructure (`infrastructure/`)**: Terraform modules for a complete AWS deployment.

## Getting Started (Local Development)

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local AI engine testing)

### Running the Backend & AI Engine

```bash
# Start the full local stack (Backend + AI Engine + DB)
docker-compose up -d

# Check API documentation
# Backend: http://localhost:8000/docs
# AI Engine: http://localhost:8001/docs
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

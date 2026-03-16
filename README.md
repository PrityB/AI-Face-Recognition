![AI Identity Verification Platform Banner](assets/banner.png)

# 🛡️ AI-Powered Identity Verification & KYC Compliance Platform

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://python.org)
[![Kotlin](https://img.shields.io/badge/Kotlin-1.9.22-purple.svg)](https://kotlinlang.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.2-green.svg)](https://fastapi.tiangolo.com)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.2.0-ee4c2c.svg)](https://pytorch.org)
[![AWS](https://img.shields.io/badge/AWS-Terraform-orange.svg)](https://aws.amazon.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ed.svg)](https://docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An end-to-end, cloud-native AI platform designed for real-time identity verification, biometric fraud detection, and automated KYC (Know Your Customer) compliance. 

Built with scalability, security, and edge-to-cloud ML architectures in mind, this project demonstrates a complete product lifecycle—from a **Jetpack Compose Android app**, through a **FastAPI microservices backend**, to heavy **PyTorch deep learning models**, all orchestrated beautifully on **AWS via Terraform** Infrastructure-as-Code.

---

## ✨ Core Capabilities & Features

* 📱 **Edge-Optimized Native Android App**: A modern Kotlin/Jetpack Compose frontend utilizing **CameraX** and **Google ML Kit** for instantaneous on-device pre-screening (ensuring face presence/quality) before hitting the network.
* 🧠 **State-of-the-Art Biometrics & Liveness**: 
  * **Face Recognition (1:1 Matching)**: Utilizes PyTorch `MTCNN` for pristine face alignment and `InceptionResnetV1` (FaceNet) for projecting faces into a 512-dimensional embedding space, calculating cosine-similarity for sub-second verification.
  * **Anti-Spoofing & Liveness**: A hybrid approach combining traditional computer vision (Laplacian variance texture analysis to reject printed photos) with a specialized `MobileNetV2` deep CNN to detect screen moiré and depth irregularities.
* 📄 **Privacy-First Document OCR**: Completely in-house optical character recognition via OpenCV preprocessing and Tesseract. PII (Personally Identifiable Information) is extracted securely inside isolated containers without ever relying on 3rd-party SaaS APIs.
* 🕵️ **Dynamic Fraud Risk Scoring**: An advanced hybrid ML pipeline using **Isolation Forests** (unsupervised anomaly detection) and **Gradient Boosting** (supervised learning) to evaluate transactional metadata and flag suspicious onboarding attempts.
* 🌩️ **Enterprise-Grade Cloud Infrastructure**: 100% declarative **Terraform** configurations provisioning an AWS VPC, serverless **ECS Fargate** clusters, secure locked-down **S3** buckets (AES256 encrypted), **RDS PostgreSQL**, and custom **SageMaker** ML training instances.
* 🚀 **Automated CI/CD**: Full containerization via Docker matched with GitHub Actions to test, build, and deploy the entire stack automatically.

---

## 🏗️ System Architecture

![Architecture](https://img.shields.io/badge/Architecture-Overview-black.svg)

1. **Android Client (Mobile Edge)**: User captures ID and a live selfie. ML Kit confirms face quality via edge CPU.
2. **Backend Gateway (FastAPI)**: Validates incoming payloads, checks database state (PostgreSQL), and coordinates ML inference.
3. **AI/ML Inference Engine (FastAPI/PyTorch)**: A specialized GPU-ready container that unpacks images in memory, runs the heavy deep learning models, and responds with match confidence and liveness scores.
4. *(See `docs/architecture/ADR-001-ml-architecture.md` for deeper technical ML decisions).*

---

## 📁 Repository Structure

```text
├── ai-engine/               # Core Machine Learning & API Inference Layer
│   ├── models/              # PyTorch Face, Liveness, OCR, and Risk prediction modules
│   ├── training/            # PyTorch DistributedDataParallel & Optuna tuning scripts
│   └── inference/           # FastAPI application serving the ML models
├── backend/                 # API Gateway & Business Logic
│   ├── app/                 # FastAPI Service, SQLAlchemy DB Models, Routers
│   └── requirements.txt
├── android-app/             # Native Kotlin Frontend
│   ├── app/src/             # Jetpack Compose UI, CameraX workflows, Retrofit APIs
│   └── build.gradle.kts
├── infrastructure/          # AWS Cloud Infrastructure (IaC)
│   ├── modules/             # Terraform components: VPC, ECS, RDS, S3, SageMaker
│   └── main.tf
├── docker/                  # Dockerfiles for all microservices
└── docs/                    # Architecture Decision Records (ADRs) and Deployment guides
```

---

## 🚀 Getting Started (Run Locally)

You can spin up the entire cloud-native backend instantly using Docker. No AWS account required for local testing!

### Prerequisites:
* Docker & Docker Compose
* Android Studio (to run the mobile app)

### Run the Backend Services:
```bash
git clone https://github.com/PrityB/AI-Face-Recognition.git
cd AI-Face-Recognition

# Spin up the FastAPI Backend, AI Inference Engine, and PostgreSQL Database
docker-compose up -d --build
```

You can now explore the interactive, auto-generated Swagger documentation:
- **Backend API**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **AI Inference Engine**: [http://localhost:8001/docs](http://localhost:8001/docs)

### Run the Mobile App:
1. Open **Android Studio**.
2. Select **Open** and target the `android-app/` directory.
3. Allow Gradle to sync dependencies.
4. Press **Run** to deploy to your physical Android device or Emulator.

---

## 🌩️ Production Deployment (AWS)

This repository includes battle-tested, production-ready Terraform to deploy the infrastructure securely to AWS. For full deployment instructions, reference the [DEPLOYMENT.md](docs/DEPLOYMENT.md) guide.

```bash
cd infrastructure
terraform init
terraform apply
```

---

## 🛠️ Tech Stack Matrix

| Domain | Technologies |
| :--- | :--- |
| **Frontend Mobile** | Kotlin, Jetpack Compose, CameraX, Google ML Kit, Retrofit, Coroutines |
| **Backend API** | Python 3.11, FastAPI, SQLAlchemy, Pydantic, PostgreSQL |
| **Machine Learning** | PyTorch, Torchvision, OpenCV, Scikit-Learn, Optuna, Tesseract OCR |
| **Infrastructure** | Terraform, AWS (VPC, ECS Fargate, S3, RDS, SageMaker) |
| **DevOps** | Docker, Docker Compose, GitHub Actions |

---
*Disclaimer: This repository is intended as a technical portfolio project demonstrating end-to-end full-stack AI platform engineering. While the architectures reflect industry best practices, the ML models require production fine-tuning on diverse, proprietary datasets before processing live PII.*

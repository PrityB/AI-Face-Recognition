import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from inference.pipeline import VerificationPipeline
from utils.image_processing import read_image_from_bytes, resize_image_if_needed
import uvicorn

app = FastAPI(title="AI Identity Verification Engine", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global pipeline instance
pipeline = VerificationPipeline()

@app.get("/health")
def health_check():
    return {"status": "healthy", "gpu_available": pipeline.face_recognizer.device.type == 'cuda'}

@app.post("/predict/face")
async def verify_face(image1: UploadFile = File(...), image2: UploadFile = File(...)):
    """Compare two faces to see if they are the same person."""
    try:
        img1_bytes = await image1.read()
        img2_bytes = await image2.read()
        
        img1 = resize_image_if_needed(read_image_from_bytes(img1_bytes))
        img2 = resize_image_if_needed(read_image_from_bytes(img2_bytes))
        
        result = pipeline.run_face_comparison(img1, img2)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/liveness")
async def check_liveness(image: UploadFile = File(...)):
    """Check if the face in the image is a live person or spoofed."""
    try:
        img_bytes = await image.read()
        img = resize_image_if_needed(read_image_from_bytes(img_bytes))
        
        result = pipeline.run_liveness_check(img)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/document")
async def verify_document(image: UploadFile = File(...)):
    """Extract Data from ID card or Passport."""
    try:
        img_bytes = await image.read()
        img = resize_image_if_needed(read_image_from_bytes(img_bytes))
        
        result = pipeline.run_document_verification(img)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/kyc")
async def full_kyc(
    face_image: UploadFile = File(...), 
    doc_image: UploadFile = File(...),
    id_face_image: UploadFile = File(None)
):
    """End-to-End KYC verification."""
    try:
        f_bytes = await face_image.read()
        d_bytes = await doc_image.read()
        
        f_img = resize_image_if_needed(read_image_from_bytes(f_bytes))
        d_img = resize_image_if_needed(read_image_from_bytes(d_bytes))
        
        id_f_img = None
        if id_face_image:
            id_f_bytes = await id_face_image.read()
            id_f_img = resize_image_if_needed(read_image_from_bytes(id_f_bytes))
            
        result = pipeline.run_full_kyc(f_img, d_img, id_f_img)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)

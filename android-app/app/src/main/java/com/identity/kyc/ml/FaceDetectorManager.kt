package com.identity.kyc.ml

import android.graphics.Bitmap
import android.graphics.Rect
import androidx.annotation.OptIn
import androidx.camera.core.ExperimentalGetImage
import androidx.camera.core.ImageProxy
import com.google.mlkit.vision.common.InputImage
import com.google.mlkit.vision.face.Face
import com.google.mlkit.vision.face.FaceDetection
import com.google.mlkit.vision.face.FaceDetectorOptions

/**
 * Wrapper for Google ML Kit Face Detection.
 * Runs on device to ensure a face is present and of sufficient quality BEFORE 
 * sending it to the backend for the heavy biometric processing.
 */
class FaceDetectorManager {

    // Fast detection configuration for live camera feed
    private val realTimeOpts = FaceDetectorOptions.Builder()
        .setPerformanceMode(FaceDetectorOptions.PERFORMANCE_MODE_FAST)
        .setContourMode(FaceDetectorOptions.CONTOUR_MODE_NONE)
        .setClassificationMode(FaceDetectorOptions.CLASSIFICATION_MODE_ALL) // Detect smiles/eyes open
        .enableTracking()
        .build()

    private val detector = FaceDetection.getClient(realTimeOpts)

    @OptIn(ExperimentalGetImage::class)
    fun processImageProxy(imageProxy: ImageProxy, onFacesDetected: (List<Face>) -> Unit) {
        val mediaImage = imageProxy.image
        if (mediaImage != null) {
            val image = InputImage.fromMediaImage(mediaImage, imageProxy.imageInfo.rotationDegrees)
            
            detector.process(image)
                .addOnSuccessListener { faces ->
                    onFacesDetected(faces)
                }
                .addOnFailureListener { e ->
                    e.printStackTrace()
                }
                .addOnCompleteListener {
                    imageProxy.close()
                }
        } else {
            imageProxy.close()
        }
    }

    /**
     * Helper to determine if a detected face is "good enough" to capture
     * for backend verification (centered, large enough, eyes open).
     */
    fun isFaceQualitySufficient(face: Face, frameWidth: Int, frameHeight: Int): Boolean {
        // 1. Face must exist
        if (face.boundingBox.isEmpty) return false

        // 2. Face must take up a reasonable portion of the frame (e.g., > 10% area)
        val faceArea = face.boundingBox.width() * face.boundingBox.height()
        val frameArea = frameWidth * frameHeight
        if (faceArea < frameArea * 0.10) return false

        // 3. Eyes should be open (Liveness/Quality check)
        val leftEyeOpen = face.leftEyeOpenProbability ?: 0f
        val rightEyeOpen = face.rightEyeOpenProbability ?: 0f
        if (leftEyeOpen < 0.5f || rightEyeOpen < 0.5f) return false

        // 4. Face shouldn't be too rotated (must face camera)
        if (Math.abs(face.headEulerAngleY) > 20 || Math.abs(face.headEulerAngleZ) > 20) {
            return false
        }

        return true
    }
}

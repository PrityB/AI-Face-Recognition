package com.identity.kyc.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.identity.kyc.data.api.KycApiService
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.toRequestBody

sealed class KycUiState {
    object Idle : KycUiState()
    object Loading : KycUiState()
    data class Success(val status: String, val riskLevel: String) : KycUiState()
    data class Error(val message: String) : KycUiState()
}

class KycViewModel(
    private val apiService: KycApiService // In a real app, injected via Hilt/Dagger
) : ViewModel() {

    private val _uiState = MutableStateFlow<KycUiState>(KycUiState.Idle)
    val uiState: StateFlow<KycUiState> = _uiState.asStateFlow()

    private var documentImageBytes: ByteArray? = null
    private var faceImageBytes: ByteArray? = null

    fun saveDocumentImage(bytes: ByteArray) {
        documentImageBytes = bytes
    }

    fun saveFaceImage(bytes: ByteArray) {
        faceImageBytes = bytes
    }

    fun submitVerificationFlow() {
        if (documentImageBytes == null || faceImageBytes == null) {
            _uiState.value = KycUiState.Error("Missing required images")
            return
        }

        _uiState.value = KycUiState.Loading

        viewModelScope.launch {
            try {
                // Convert ByteArray to Retrofit MultipartBody
                val docReqFile = documentImageBytes!!.toRequestBody("image/jpeg".toMediaTypeOrNull())
                val docPart = MultipartBody.Part.createFormData("docImage", "doc.jpg", docReqFile)

                val faceReqFile = faceImageBytes!!.toRequestBody("image/jpeg".toMediaTypeOrNull())
                val facePart = MultipartBody.Part.createFormData("liveImage", "face.jpg", faceReqFile)

                // Hardcoded user ID for demo purposes
                val response = apiService.completeKyc("demo_user_123", facePart, docPart)

                if (response.success) {
                    _uiState.value = KycUiState.Success(response.kycStatus, response.riskLevel)
                } else {
                    _uiState.value = KycUiState.Error("Verification failed on server.")
                }
            } catch (e: Exception) {
                _uiState.value = KycUiState.Error(e.message ?: "Unknown Network Error")
            }
        }
    }
}

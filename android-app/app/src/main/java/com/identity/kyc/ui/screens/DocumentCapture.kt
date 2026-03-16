package com.identity.kyc.ui.screens

import androidx.camera.core.CameraSelector
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.identity.kyc.ui.components.CameraPreview

@Composable
fun DocumentCaptureScreen(
    onDocumentCaptured: (ByteArray) -> Unit,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier.fillMaxSize().padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            text = "Scan ID Document",
            style = MaterialTheme.typography.headlineMedium
        )
        
        Spacer(modifier = Modifier.height(32.dp))
        
        // Real Camera Preview
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(400.dp),
            contentAlignment = Alignment.Center
        ) {
            CameraPreview(
                lensFacing = CameraSelector.LENS_FACING_BACK,
                modifier = Modifier.fillMaxSize()
            )
        }
        
        Spacer(modifier = Modifier.height(32.dp))
        
        Button(
            onClick = { 
                // Normally this would trigger the CameraX ImageCapture use case
                onDocumentCaptured(ByteArray(0)) 
            },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("Capture Document")
        }
    }
}

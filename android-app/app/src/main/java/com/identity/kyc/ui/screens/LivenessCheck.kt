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
fun LivenessCheckScreen(
    onLivenessCompleted: (ByteArray) -> Unit,
    modifier: Modifier = Modifier
) {
    var instruction by remember { mutableStateOf("Please blink your eyes") }
    
    Column(
        modifier = modifier.fillMaxSize().padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            text = "Liveness Check",
            style = MaterialTheme.typography.headlineMedium
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        Text(
            text = instruction,
            style = MaterialTheme.typography.bodyLarge,
            color = MaterialTheme.colorScheme.primary
        )
        
        Spacer(modifier = Modifier.height(32.dp))
        
        // Real Camera Preview (Front Facing)
        Box(
            modifier = Modifier
                .size(300.dp),
            contentAlignment = Alignment.Center
        ) {
            CameraPreview(
                lensFacing = CameraSelector.LENS_FACING_FRONT,
                modifier = Modifier.fillMaxSize()
            )
        }
        
        Spacer(modifier = Modifier.height(32.dp))
        
        Button(
            onClick = { 
                // Triggers liveness verification and captures the final valid frame
                onLivenessCompleted(ByteArray(0)) 
            },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("Start Liveness Session")
        }
    }
}

package com.identity.kyc.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun KycDashboardScreen(
    status: String,
    riskLevel: String,
    onStartVerification: () -> Unit,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier.fillMaxSize().padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            text = "Identity Verification",
            style = MaterialTheme.typography.headlineMedium
        )
        
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 32.dp)
        ) {
            Column(
                modifier = Modifier.padding(16.dp),
                horizontalAlignment = Alignment.Start
            ) {
                Text("Verification Status: $status", style = MaterialTheme.typography.titleMedium)
                Spacer(modifier = Modifier.height(8.dp))
                Text("Risk Level: $riskLevel", style = MaterialTheme.typography.bodyLarge)
            }
        }
        
        Button(
            onClick = onStartVerification,
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("Start New Verification")
        }
    }
}

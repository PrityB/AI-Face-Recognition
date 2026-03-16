package com.identity.kyc

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.identity.kyc.ui.screens.DocumentCaptureScreen
import com.identity.kyc.ui.screens.KycDashboardScreen
import com.identity.kyc.ui.screens.LivenessCheckScreen

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // The Compose Navigation Graph
        setContent {
            MaterialTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    val navController = rememberNavController()

                    NavHost(navController = navController, startDestination = "dashboard") {
                        
                        // 1. Home Dashboard
                        composable("dashboard") {
                            KycDashboardScreen(
                                status = "Pending",
                                riskLevel = "Unknown",
                                onStartVerification = {
                                    navController.navigate("document_capture")
                                }
                            )
                        }

                        // 2. Document Capture (Passport/ID)
                        composable("document_capture") {
                            DocumentCaptureScreen(
                                onDocumentCaptured = { bytes ->
                                    // Normally save bytes to ViewModel, then proceed
                                    navController.navigate("liveness_check")
                                }
                            )
                        }

                        // 3. Liveness Check (Face Capture)
                        composable("liveness_check") {
                            LivenessCheckScreen(
                                onLivenessCompleted = { bytes ->
                                    // Complete flow - Send all data to Backend API
                                    navController.navigate("dashboard") {
                                        popUpTo("dashboard") { inclusive = true }
                                    }
                                }
                            )
                        }
                    }
                }
            }
        }
    }
}

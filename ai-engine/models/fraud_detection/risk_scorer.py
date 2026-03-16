import numpy as np
from sklearn.ensemble import GradientBoostingClassifier, IsolationForest

class RiskScorer:
    """
    ML-based Fraud Risk Scoring Engine.
    Combines supervised scoring (Gradient Boosting) with unsupervised 
    anomaly detection (Isolation Forest).
    """
    def __init__(self, model_path=None):
        # In a real system, these would be loaded from disk (pickle/joblib)
        self.xgb_model = GradientBoostingClassifier()
        self.anomaly_detector = IsolationForest(contamination=0.01) # 1% assumed fraud rate
        self.is_trained = False
        
        # Define feature names for clarity
        self.features = [
            'face_match_confidence', # 0.0 to 1.0 (from FaceNet)
            'liveness_score',        # 0.0 to 1.0 (from Liveness CNN)
            'document_glare',        # 0.0 to 1.0
            'device_risk_score',     # 0.0 to 1.0 (Mock external signal)
            'ip_risk_score'          # 0.0 to 1.0 (Mock external signal)
        ]

    def _prepare_features(self, verification_data: dict) -> np.ndarray:
        """
        Extract numerical features from the raw verification results.
        """
        features = [
            float(verification_data.get('face_match_confidence', 0.0)),
            float(verification_data.get('liveness_score', 0.0)),
            float(verification_data.get('document_glare', 1.0)), # High glare is risky
            float(verification_data.get('device_risk_score', 0.1)), # Default low risk
            float(verification_data.get('ip_risk_score', 0.1))      # Default low risk
        ]
        return np.array(features).reshape(1, -1)

    def calculate_heuristic_score(self, features: list) -> float:
        """
        Fallback rule-based scoring if ML model isn't trained yet.
        Returns a score from 0 (Safe) to 100 (High Risk).
        """
        face_conf, live_score, glare, dev_risk, ip_risk = features
        
        # Heuristics:
        # High face match & high liveness -> Reduces risk
        # High device/IP risk -> Increases risk linearly
        
        base_risk = 50.0
        
        # Good signals lower risk
        base_risk -= (face_conf * 20.0)
        base_risk -= (live_score * 30.0)
        
        # Bad signals increase risk
        base_risk += (glare * 10.0)
        base_risk += (dev_risk * 25.0)
        base_risk += (ip_risk * 25.0)
        
        # Clip to 0-100 range
        return max(0.0, min(100.0, base_risk))

    def evaluate_risk(self, verification_data: dict) -> dict:
        """
        Evaluate full risk profile.
        Returns Risk Score (0-100) and Risk Level (LOW, MEDIUM, HIGH, CRITICAL).
        """
        feature_vector = self._prepare_features(verification_data)
        features_list = feature_vector.flatten().tolist()
        
        if self.is_trained:
            # Predict probability of fraud
            prob_fraud = self.xgb_model.predict_proba(feature_vector)[0][1]
            risk_score = prob_fraud * 100.0
            
            # Check for anomaly (Isolation forest returns -1 for anomaly, 1 for normal)
            is_anomaly = self.anomaly_detector.predict(feature_vector)[0] == -1
            if is_anomaly:
                risk_score = max(risk_score, 85.0) # Anomalies are automatically high risk
        else:
            # Use rules if no model loaded
            risk_score = self.calculate_heuristic_score(features_list)
            is_anomaly = False

        # Determine level
        if risk_score >= 80:
            level = "CRITICAL"
        elif risk_score >= 60:
            level = "HIGH"
        elif risk_score >= 30:
            level = "MEDIUM"
        else:
            level = "LOW"
            
        return {
            "risk_score": float(round(risk_score, 2)),
            "risk_level": level,
            "is_anomaly": bool(is_anomaly),
            "signals_used": self.features
        }

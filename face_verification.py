 #============================================================
# PROJECT: TrustNet AI - Multi-Modal Digital Trust
#          Intelligence and Authentication Verification Platform
# COLLEGE: St. John College of Engineering and Management, Palghar
# DEPARTMENT: Computer Engineering
# YEAR: B.Tech Final Year (2025-2026)
#
# FILE: modules/face_verification.py
# DESCRIPTION: Module 1 - Compares a live selfie against an ID
#              document photo using DeepFace pretrained model and
#              produces a confidence score + DS mass function
#
# GUIDE: [Guide Name] | [Designation]
# DATE: August 2026
# ============================================================
 
import os
import cv2
import numpy as np
from deepface import DeepFace
import config
 
 
class FaceVerifier:
    """
    Face Verification Module for TrustNet AI.
 
    Uses DeepFace (pretrained VGG-Face model) to compare a
    live selfie photo with the photo on an ID document.
 
    Output:
        - confidence_score : float (0 to 1)
        - mass_function    : dict  {real, fake, unknown}
        - explanation      : str   (human-readable result)
    """
 
    def __init__(self):
        self.model_name       = config.FACE_MODEL
        self.distance_metric  = config.FACE_DISTANCE_METRIC
        self.enforce_detection = config.FACE_ENFORCE_DETECTION
        self.reliability_weight = config.FACE_RELIABILITY_WEIGHT
 
    # ─────────────────────────────────────────
    # PRIVATE: Convert distance to confidence
    # ─────────────────────────────────────────
    def _distance_to_confidence(self, distance):
        """
        Convert DeepFace cosine distance (lower = more similar)
        into a confidence score between 0 and 1.
 
        Distance range  → Confidence
        0.0  to 0.2     → 0.95  (very high match)
        0.2  to 0.4     → 0.80  (high match)
        0.4  to 0.6     → 0.60  (medium match)
        0.6  and above  → 0.30  (low match / likely different person)
        """
        thresholds = config.FACE_CONFIDENCE_THRESHOLDS
        scores     = config.FACE_CONFIDENCE_SCORES
 
        if distance < thresholds["very_high"]:
            return scores["very_high"]
        elif distance < thresholds["high"]:
            return scores["high"]
        elif distance < thresholds["medium"]:
            return scores["medium"]
        else:
            return scores["low"]
 
    # ─────────────────────────────────────────
    # PRIVATE: Generate DS Mass Function
    # ─────────────────────────────────────────
    def _get_mass_function(self, confidence_score):
        """
        Convert a confidence score into a Dempster-Shafer mass function.
        Mass is discounted by the module reliability weight before fusion.
 
        Returns dict: {real, fake, unknown}
        All three values must sum to exactly 1.0
        """
        w = self.reliability_weight  # 0.9 for face module
 
        if confidence_score >= 0.85:
            # Very strong face match
            m_real    = round(0.80 * w, 4)
            m_fake    = round(0.05 * w, 4)
        elif confidence_score >= 0.70:
            # Good face match
            m_real    = round(0.65 * w, 4)
            m_fake    = round(0.10 * w, 4)
        elif confidence_score >= 0.50:
            # Moderate match - uncertain
            m_real    = round(0.40 * w, 4)
            m_fake    = round(0.25 * w, 4)
        else:
            # Poor match - likely fake
            m_real    = round(0.10 * w, 4)
            m_fake    = round(0.60 * w, 4)
 
        m_unknown = round(1.0 - m_real - m_fake, 4)
 
        # Safety clamp: ensure unknown is never negative
        if m_unknown < 0:
            m_unknown = 0.0
 
        return {
            "real":    m_real,
            "fake":    m_fake,
            "unknown": m_unknown
        }
 
    # ─────────────────────────────────────────
    # PRIVATE: Generate explanation text
    # ─────────────────────────────────────────
    def _generate_explanation(self, confidence_score, distance, verified):
        """Generate simple human-readable explanation of face result"""
        if confidence_score >= 0.85:
            return (f"Face match STRONG. Live photo closely matches ID photo "
                    f"(similarity distance: {distance:.3f}). "
                    f"High confidence this is the same person.")
        elif confidence_score >= 0.70:
            return (f"Face match GOOD. Live photo matches ID photo with acceptable "
                    f"similarity (distance: {distance:.3f}).")
        elif confidence_score >= 0.50:
            return (f"Face match MODERATE. Some differences detected between live "
                    f"photo and ID photo (distance: {distance:.3f}). "
                    f"May be lighting or angle variation.")
        else:
            return (f"Face match FAILED. Live photo does not match ID photo "
                    f"(distance: {distance:.3f}). "
                    f"Possible photo substitution or wrong person.")
 
    # ─────────────────────────────────────────
    # PUBLIC: Main verify function
    # ─────────────────────────────────────────
    def verify(self, live_image_path, id_image_path):
        """
        Main function: Compare live selfie vs ID document photo.
 
        Args:
            live_image_path (str): Path to live selfie image
            id_image_path   (str): Path to ID document photo
 
        Returns:
            tuple: (confidence_score, mass_function, explanation)
                - confidence_score : float (0 to 1)
                - mass_function    : dict {real, fake, unknown}
                - explanation      : str
        """
        print("\n" + "=" * 50)
        print("  MODULE 1: FACE VERIFICATION")
        print("=" * 50)
 
        # ── Step 1: Check both images exist ──
        if not os.path.exists(live_image_path):
            explanation = f"ERROR: Live image not found at {live_image_path}"
            print(f"  ✗ {explanation}")
            return 0.0, {"real": 0.1, "fake": 0.8, "unknown": 0.1}, explanation
 
        if not os.path.exists(id_image_path):
            explanation = f"ERROR: ID image not found at {id_image_path}"
            print(f"  ✗ {explanation}")
            return 0.0, {"real": 0.1, "fake": 0.8, "unknown": 0.1}, explanation
 
        print(f"  Live Image : {live_image_path}")
        print(f"  ID Image   : {id_image_path}")
        print(f"  Model      : {self.model_name}")
        print(f"  Metric     : {self.distance_metric}")
 
        # ── Step 2: Run DeepFace comparison ──
        try:
            result = DeepFace.verify(
                img1_path        = live_image_path,
                img2_path        = id_image_path,
                model_name       = self.model_name,
                distance_metric  = self.distance_metric,
                enforce_detection= self.enforce_detection
            )
 
            verified = result.get("verified", False)
            distance = result.get("distance", 1.0)
            threshold = result.get("threshold", 0.4)
 
            print(f"\n  DeepFace Result:")
            print(f"    Verified  : {verified}")
            print(f"    Distance  : {distance:.4f}")
            print(f"    Threshold : {threshold:.4f}")
 
        except Exception as e:
            explanation = f"Face verification failed: {str(e)}"
            print(f"  ✗ Error: {e}")
            return 0.0, {"real": 0.05, "fake": 0.90, "unknown": 0.05}, explanation
 
        # ── Step 3: Convert distance → confidence score ──
        confidence_score = self._distance_to_confidence(distance)
 
        # ── Step 4: Generate mass function ──
        mass_function = self._get_mass_function(confidence_score)
 
        # ── Step 5: Generate explanation ──
        explanation = self._generate_explanation(confidence_score, distance, verified)
 
        # ── Step 6: Print results ──
        print(f"\n  Confidence Score : {confidence_score:.3f} ({confidence_score*100:.1f}%)")
        print(f"  Mass Function    :")
        print(f"    Real    = {mass_function['real']}")
        print(f"    Fake    = {mass_function['fake']}")
        print(f"    Unknown = {mass_function['unknown']}")
        print(f"\n  Explanation: {explanation}")
 
        return confidence_score, mass_function, explanation
 
 
# ─────────────────────────────────────────
# STANDALONE TEST
# ─────────────────────────────────────────
if __name__ == "__main__":
 
    print("=" * 60)
    print("  TrustNet AI - Face Verification Module Test")
    print("  St. John College of Engineering and Management, Palghar")
    print("=" * 60)
 
    verifier = FaceVerifier()
 
    # Test with sample images
    # Replace with actual image paths to test
    live_img = "data/sample_faces/live_photo.jpg"
    id_img   = "data/sample_faces/id_photo.jpg"
 
    if os.path.exists(live_img) and os.path.exists(id_img):
        score, mass, explanation = verifier.verify(live_img, id_img)
 
        print("\n" + "=" * 60)
        print("  FINAL OUTPUT:")
        print(f"  Score       : {score:.3f}")
        print(f"  Mass        : {mass}")
        print(f"  Explanation : {explanation}")
        print("=" * 60)
    else:
        print("\n  Sample images not found.")
        print("  Place test images in data/sample_faces/")
        print("  Files needed:")
        print("    - data/sample_faces/live_photo.jpg")
        print("    - data/sample_faces/id_photo.jpg")
 
        # Run a demo with dummy values to show the logic works
        print("\n  Running DEMO with dummy distance value (0.25)...")
        dummy_distance   = 0.25
        dummy_confidence = verifier._distance_to_confidence(dummy_distance)
        dummy_mass       = verifier._get_mass_function(dummy_confidence)
        dummy_explanation= verifier._generate_explanation(dummy_confidence, dummy_distance, True)
 
        print(f"\n  Demo Confidence : {dummy_confidence}")
        print(f"  Demo Mass       : {dummy_mass}")
        print(f"  Demo Explanation: {dummy_explanation}")
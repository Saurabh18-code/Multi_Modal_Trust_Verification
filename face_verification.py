 #============================================================
# PROJECT: TrustNet AI - Multi-Modal Digital Trust
#          Intelligence and Authentication Verification Platform
# COLLEGE: St. John College of Engineering and Management, Palghar
# DEPARTMENT: Computer Engineering
# YEAR: B.Tech Final Year (2026-2027)
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
import traceback
import cv2
import numpy as np

from deepface import DeepFace
import config


class FaceVerifier:
    """
    Robust Face Verification Module for TrustNet AI.

    Compares:
        1. Live/selfie image
        2. ID/document image

    Returns:
        confidence_score : float (0.0 - 1.0)
        mass_function    : dict {real, fake, unknown}
        explanation      : str
    """

    def __init__(self):
        # Read configuration safely
        self.model_name = getattr(
            config,
            "FACE_MODEL",
            "VGG-Face"
        )

        self.distance_metric = getattr(
            config,
            "FACE_DISTANCE_METRIC",
            "cosine"
        )

        self.enforce_detection = getattr(
            config,
            "FACE_ENFORCE_DETECTION",
            True
        )

        self.reliability_weight = getattr(
            config,
            "FACE_RELIABILITY_WEIGHT",
            0.90
        )

        # OpenCV is generally available and works well for basic detection
        self.detector_backend = "opencv"

    # ============================================================
    # IMAGE VALIDATION
    # ============================================================

    def _validate_image(self, image_path, image_name):
        """
        Check that an image exists and OpenCV can read it.
        """

        if not image_path:
            return False, f"{image_name} path is empty."

        # Convert to absolute path
        image_path = os.path.abspath(str(image_path))

        print(f"\nChecking {image_name}:")
        print(f"Path: {image_path}")

        # Check file existence
        if not os.path.exists(image_path):
            return False, (
                f"{image_name} not found:\n"
                f"{image_path}"
            )

        # Check that it is actually a file
        if not os.path.isfile(image_path):
            return False, (
                f"{image_name} path is not a file:\n"
                f"{image_path}"
            )

        # Try reading image using OpenCV
        image = cv2.imread(image_path)

        if image is None:
            return False, (
                f"{image_name} exists but OpenCV could not read it. "
                f"The file may be corrupted or unsupported."
            )

        # Check dimensions
        height, width = image.shape[:2]

        if height <= 0 or width <= 0:
            return False, (
                f"{image_name} has invalid dimensions."
            )

        print(
            f"{image_name} loaded successfully "
            f"({width} x {height})"
        )

        return True, image_path

    # ============================================================
    # DISTANCE -> CONFIDENCE
    # ============================================================

    def _distance_to_confidence(self, distance):
        """
        Convert DeepFace distance into a confidence score.

        Lower distance = better face similarity.
        """

        # Get configured thresholds if available
        thresholds = getattr(
            config,
            "FACE_CONFIDENCE_THRESHOLDS",
            {
                "very_high": 0.20,
                "high": 0.40,
                "medium": 0.60
            }
        )

        scores = getattr(
            config,
            "FACE_CONFIDENCE_SCORES",
            {
                "very_high": 0.95,
                "high": 0.80,
                "medium": 0.60,
                "low": 0.30
            }
        )

        try:
            distance = float(distance)
        except (ValueError, TypeError):
            return 0.0

        if distance < thresholds["very_high"]:
            return scores["very_high"]

        elif distance < thresholds["high"]:
            return scores["high"]

        elif distance < thresholds["medium"]:
            return scores["medium"]

        else:
            return scores["low"]

    # ============================================================
    # DEMPSTER-SHAFER MASS FUNCTION
    # ============================================================

    def _get_mass_function(self, confidence_score):
        """
        Convert confidence into Dempster-Shafer mass.

        Output:
            real
            fake
            unknown

        Sum should equal 1.0.
        """

        # Keep reliability between 0 and 1
        w = max(
            0.0,
            min(
                1.0,
                float(self.reliability_weight)
            )
        )

        if confidence_score >= 0.85:

            # Strong match
            m_real = 0.80 * w
            m_fake = 0.05 * w

        elif confidence_score >= 0.70:

            # Good match
            m_real = 0.65 * w
            m_fake = 0.10 * w

        elif confidence_score >= 0.50:

            # Moderate match
            m_real = 0.40 * w
            m_fake = 0.25 * w

        else:

            # Poor match
            m_real = 0.10 * w
            m_fake = 0.60 * w

        # Remaining belief goes to unknown
        m_unknown = 1.0 - m_real - m_fake

        # Safety checks
        m_real = max(0.0, min(1.0, m_real))
        m_fake = max(0.0, min(1.0, m_fake))
        m_unknown = max(0.0, min(1.0, m_unknown))

        # Normalize so total is EXACTLY 1
        total = m_real + m_fake + m_unknown

        if total > 0:
            m_real /= total
            m_fake /= total
            m_unknown /= total

        return {
            "real": round(m_real, 4),
            "fake": round(m_fake, 4),
            "unknown": round(m_unknown, 4)
        }

    # ============================================================
    # EXPLANATION
    # ============================================================

    def _generate_explanation(
        self,
        confidence_score,
        distance,
        verified
    ):
        """
        Generate a human-readable explanation.
        """

        if verified and confidence_score >= 0.85:

            return (
                f"Face match STRONG. The live photo closely matches "
                f"the ID photo. Similarity distance: {distance:.4f}. "
                f"High confidence that both images belong to the "
                f"same person."
            )

        elif verified and confidence_score >= 0.70:

            return (
                f"Face match GOOD. The live photo matches the ID photo "
                f"with acceptable similarity. "
                f"Similarity distance: {distance:.4f}."
            )

        elif verified:

            return (
                f"Face match detected, but the similarity is moderate. "
                f"Similarity distance: {distance:.4f}. "
                f"Lighting, pose or image quality may affect the result."
            )

        else:

            return (
                f"Face match FAILED. The live photo does not sufficiently "
                f"match the ID photo. Similarity distance: "
                f"{distance:.4f}."
            )

    # ============================================================
    # MAIN VERIFICATION FUNCTION
    # ============================================================

    def verify(self, live_image_path, id_image_path):

        print("\n" + "=" * 60)
        print("             MODULE 1: FACE VERIFICATION")
        print("=" * 60)

        # --------------------------------------------------------
        # STEP 1: Validate live image
        # --------------------------------------------------------

        live_ok, live_result = self._validate_image(
            live_image_path,
            "Live image"
        )

        if not live_ok:

            print(f"\nERROR: {live_result}")

            return (
                0.0,
                {
                    "real": 0.05,
                    "fake": 0.90,
                    "unknown": 0.05
                },
                f"Face verification failed: {live_result}"
            )

        # --------------------------------------------------------
        # STEP 2: Validate ID image
        # --------------------------------------------------------

        id_ok, id_result = self._validate_image(
            id_image_path,
            "ID image"
        )

        if not id_ok:

            print(f"\nERROR: {id_result}")

            return (
                0.0,
                {
                    "real": 0.05,
                    "fake": 0.90,
                    "unknown": 0.05
                },
                f"Face verification failed: {id_result}"
            )

        live_path = live_result
        id_path = id_result

        print("\nImages validated successfully.")

        print(f"Live Image : {live_path}")
        print(f"ID Image   : {id_path}")
        print(f"Model      : {self.model_name}")
        print(f"Metric     : {self.distance_metric}")
        print(f"Detector   : {self.detector_backend}")

        # --------------------------------------------------------
        # STEP 3: Check that faces can be detected
        # --------------------------------------------------------

        print("\nDetecting face in live image...")

        try:

            live_faces = DeepFace.extract_faces(
                img_path=live_path,
                detector_backend=self.detector_backend,
                enforce_detection=True,
                align=True
            )

            if not live_faces:

                raise ValueError(
                    "No face detected in the live/selfie image."
                )

            print(
                f"Live image: {len(live_faces)} face(s) detected."
            )

        except Exception as e:

            print("\nERROR: Could not detect face in live image.")
            print("Reason:", str(e))

            return (
                0.0,
                {
                    "real": 0.05,
                    "fake": 0.90,
                    "unknown": 0.05
                },
                (
                    "Face verification failed: "
                    "No usable face was detected in the live image. "
                    "Please upload a clear front-facing selfie."
                )
            )

        # --------------------------------------------------------
        # STEP 4: Check face in ID image
        # --------------------------------------------------------

        print("\nDetecting face in ID image...")

        try:

            id_faces = DeepFace.extract_faces(
                img_path=id_path,
                detector_backend=self.detector_backend,
                enforce_detection=True,
                align=True
            )

            if not id_faces:

                raise ValueError(
                    "No face detected in the ID image."
                )

            print(
                f"ID image: {len(id_faces)} face(s) detected."
            )

        except Exception as e:

            print("\nERROR: Could not detect face in ID image.")
            print("Reason:", str(e))

            return (
                0.0,
                {
                    "real": 0.05,
                    "fake": 0.90,
                    "unknown": 0.05
                },
                (
                    "Face verification failed: "
                    "No usable face was detected in the ID image. "
                    "Please upload a clear ID image containing a visible face."
                )
            )

        # --------------------------------------------------------
        # STEP 5: DeepFace verification
        # --------------------------------------------------------

        print("\nRunning DeepFace verification...")

        try:

            result = DeepFace.verify(

                img1_path=live_path,

                img2_path=id_path,

                model_name=self.model_name,

                distance_metric=self.distance_metric,

                detector_backend=self.detector_backend,

                enforce_detection=True,

                align=True

            )

            # ----------------------------------------------------
            # Extract result
            # ----------------------------------------------------

            verified = bool(
                result.get("verified", False)
            )

            distance = float(
                result.get("distance", 1.0)
            )

            threshold = float(
                result.get("threshold", 0.4)
            )

            print("\n" + "-" * 50)
            print("DEEPFACE RESULT")
            print("-" * 50)

            print(
                f"Verified  : {verified}"
            )

            print(
                f"Distance  : {distance:.6f}"
            )

            print(
                f"Threshold : {threshold:.6f}"
            )

            # ----------------------------------------------------
            # Step 6: Convert distance to confidence
            # ----------------------------------------------------

            confidence_score = (
                self._distance_to_confidence(distance)
            )

            # If DeepFace says the faces are NOT verified,
            # don't accidentally give a high "real" score.
            if not verified:

                confidence_score = min(
                    confidence_score,
                    0.30
                )

            # ----------------------------------------------------
            # Step 7: Generate DS mass
            # ----------------------------------------------------

            mass_function = self._get_mass_function(
                confidence_score
            )

            # ----------------------------------------------------
            # Step 8: Explanation
            # ----------------------------------------------------

            explanation = self._generate_explanation(
                confidence_score,
                distance,
                verified
            )

            # ----------------------------------------------------
            # Step 9: Print final face result
            # ----------------------------------------------------

            print("\n" + "=" * 50)
            print("FACE VERIFICATION RESULT")
            print("=" * 50)

            print(
                f"Confidence : "
                f"{confidence_score:.3f} "
                f"({confidence_score * 100:.1f}%)"
            )

            print(
                f"Verified   : {verified}"
            )

            print(
                f"Distance   : {distance:.4f}"
            )

            print("\nMass Function:")

            print(
                f"  Real    = {mass_function['real']}"
            )

            print(
                f"  Fake    = {mass_function['fake']}"
            )

            print(
                f"  Unknown = {mass_function['unknown']}"
            )

            print(
                f"\nExplanation: {explanation}"
            )

            print("=" * 50)

            return (
                confidence_score,
                mass_function,
                explanation
            )

        # --------------------------------------------------------
        # STEP 10: Catch DeepFace errors
        # --------------------------------------------------------

        except Exception as e:

            print("\n" + "=" * 60)
            print("              DEEPFACE ERROR")
            print("=" * 60)

            print(
                "Error type:",
                type(e).__name__
            )

            print(
                "Error message:",
                str(e)
            )

            print("\nFULL TRACEBACK:")
            traceback.print_exc()

            print("=" * 60)

            explanation = (
                "Face verification failed while processing "
                "the uploaded images. Check the terminal for "
                "the detailed error."
            )

            return (
                0.0,
                {
                    "real": 0.05,
                    "fake": 0.90,
                    "unknown": 0.05
                },
                explanation
            )


# ================================================================
# STANDALONE TEST
# ================================================================

if __name__ == "__main__":

    print("=" * 60)
    print("       TrustNet AI - Face Verification Test")
    print("=" * 60)

    verifier = FaceVerifier()

    # Change these paths if you want to test directly
    live_img = "data/sample_faces/live_photo.jpg"
    id_img = "data/sample_faces/id_photo.jpg"

    if os.path.exists(live_img) and os.path.exists(id_img):

        score, mass, explanation = verifier.verify(
            live_img,
            id_img
        )

        print("\n" + "=" * 60)
        print("FINAL OUTPUT")
        print("=" * 60)

        print(
            f"Score       : {score:.3f}"
        )

        print(
            f"Percentage  : {score * 100:.1f}%"
        )

        print(
            f"Mass        : {mass}"
        )

        print(
            f"Explanation : {explanation}"
        )

        print("=" * 60)

    else:

        print("\nSample images were not found.")

        print(
            "Expected:"
        )

        print(
            f"Live: {live_img}"
        )

        print(
            f"ID  : {id_img}"
        )
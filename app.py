from flask import Flask, render_template, request
import os
import json

from modules.face_verification import FaceVerifier
from modules.document_verification import DocumentVerifier
from modules.fusion import TrustFusion
from modules.behavioral_verification import BehavioralVerifier


app = Flask(__name__)

UPLOAD_FOLDER = "data/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/", methods=["GET", "POST"])
def home():

    result = None

    if request.method == "POST":

        # ========================================
        # GET USER INPUT
        # ========================================

        user_id = request.form.get("user_id")

        live_photo = request.files.get("live_photo")
        id_document = request.files.get("id_document")

        print("\n========================================")
        print("🔥 VERIFICATION REQUEST RECEIVED")
        print("========================================")

        print("USER ID:", user_id)
        print("LIVE PHOTO:", live_photo)
        print("ID DOCUMENT:", id_document)

        # ========================================
        # CHECK INPUTS
        # ========================================

        if not live_photo or not id_document:
            print("❌ Missing selfie or ID document")

            result = "Please capture Live Photo and ID Document."

            return render_template(
                "index.html",
                result=result
            )

        # ========================================
        # FILE PATHS
        # ========================================

        live_path = os.path.join(
            UPLOAD_FOLDER,
            "live_photo.jpg"
        )

        id_path = os.path.join(
            UPLOAD_FOLDER,
            "id_document.jpg"
        )

        # ========================================
        # SAVE CAMERA SELFIE
        # ========================================

        try:

            live_photo.save(live_path)

            print("✓ Camera selfie saved:", live_path)

        except Exception as e:

            print("❌ Camera photo error:", e)

            result = "Could not save camera selfie."

            return render_template(
                "index.html",
                result=result
            )

        # ========================================
        # SAVE ID DOCUMENT
        # ========================================

        try:

            id_document.save(id_path)

            print("✓ ID document saved:", id_path)

        except Exception as e:

            print("❌ ID document error:", e)

            result = "Could not save ID document."

            return render_template(
                "index.html",
                result=result
            )

        print("🔥 BOTH FILES SAVED — STARTING VERIFICATION")

        # ========================================
        # MODULE 1: FACE VERIFICATION
        # ========================================

        print("\nMODULE 1: FACE VERIFICATION")
        print("🔥 STARTING FACE VERIFICATION")

        try:

            face_verifier = FaceVerifier()

            face_score, face_mass, face_explanation = (
                face_verifier.verify(
                    live_path,
                    id_path
                )
            )

            print("✓ FACE VERIFICATION COMPLETE")
            print("Face Score:", face_score)

        except Exception as e:

            print("❌ Face verification error:", e)

            face_score = 0.0

            face_mass = {
                "real": 0.0,
                "fake": 0.0,
                "unknown": 1.0
            }

            face_explanation = (
                "Face verification could not be completed."
            )

        # ========================================
        # MODULE 2: DOCUMENT VERIFICATION
        # ========================================

        print("\nMODULE 2: DOCUMENT VERIFICATION")

        try:

            document_verifier = DocumentVerifier()

            document_score, document_mass, document_explanation = (
                document_verifier.verify(id_path)
            )

            print("✓ DOCUMENT VERIFICATION COMPLETE")
            print("Document Score:", document_score)

        except Exception as e:

            print("❌ Document verification error:", e)

            document_score = 0.0

            document_mass = {
                "real": 0.0,
                "fake": 0.0,
                "unknown": 1.0
            }

            document_explanation = (
                "Document verification could not be completed."
            )

        # ========================================
        # MODULE 3: BEHAVIORAL VERIFICATION
        # ========================================

        print("\nMODULE 3: BEHAVIORAL VERIFICATION")

        behavioral_verifier = BehavioralVerifier()

        typing_data = request.form.get(
            "typing_data",
            ""
        )

        if typing_data:

            try:

                keystroke_times = json.loads(
                    typing_data
                )

            except Exception as e:

                print(
                    "Typing data error:",
                    e
                )

                keystroke_times = []

        else:

            keystroke_times = []

        try:

            behavioral_score, behavioral_mass, behavioral_explanation = (
                behavioral_verifier.verify(
                    user_id,
                    keystroke_times
                )
            )

            print("✓ BEHAVIORAL VERIFICATION COMPLETE")
            print("Behavioral Score:", behavioral_score)

        except Exception as e:

            print(
                "❌ Behavioral verification error:",
                e
            )

            behavioral_score = 0.5

            behavioral_mass = {
                "real": 0.3,
                "fake": 0.3,
                "unknown": 0.4
            }

            behavioral_explanation = (
                "Behavioral verification could not be completed."
            )

        # ========================================
        # MODULE 4: DEMPSTER-SHAFER FUSION
        # ========================================

        print("\nMODULE 4: DEMPSTER-SHAFER FUSION")

        try:

            fusion = TrustFusion()

            fusion_result = fusion.combine(
                face_mass,
                document_mass,
                behavioral_mass
            )

            print("✓ FUSION COMPLETE")

            print(
                "Trust Score:",
                fusion_result["trust_score"]
            )

            print(
                "Decision:",
                fusion_result["decision"]
            )

        except Exception as e:

            print("❌ Fusion error:", e)

            fusion_result = {
                "trust_score": 0.0,
                "decision": "VERIFICATION ERROR"
            }

        # ========================================
        # FINAL RESULT
        # ========================================

        result = {

            "face_score": round(
                face_score * 100,
                2
            ),

            "face_explanation":
                face_explanation,

            "document_score": round(
                document_score * 100,
                2
            ),

            "document_explanation":
                document_explanation,

            "behavioral_score": round(
                behavioral_score * 100,
                2
            ),

            "behavioral_explanation":
                behavioral_explanation,

            "trust_score": round(
                fusion_result["trust_score"] * 100,
                2
            ),

            "decision":
                fusion_result["decision"]
        }

        # ========================================
        # PRINT FINAL RESULTS
        # ========================================

        print("\n========================================")
        print("🔥 FINAL MODULE RESULTS")
        print("========================================")

        print(
            "Face Score:",
            face_score
        )

        print(
            "Document Score:",
            document_score
        )

        print(
            "Behavioral Score:",
            behavioral_score
        )

        print(
            "Trust Score:",
            fusion_result["trust_score"]
        )

        print(
            "Decision:",
            fusion_result["decision"]
        )

        print("========================================\n")

    return render_template(
        "index.html",
        result=result
    )


if __name__ == "__main__":

    app.run(debug=True)
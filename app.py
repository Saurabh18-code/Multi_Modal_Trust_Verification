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

        user_id = request.form.get("user_id")
        live_photo = request.files.get("live_photo")
        id_document = request.files.get("id_document")

        if not live_photo or not id_document:
            result = "Please upload both Live Photo and ID Document."
            return render_template("index.html", result=result)

        # Save uploaded files
        live_path = os.path.join(
            UPLOAD_FOLDER, "live_photo.jpg"
        )

        id_path = os.path.join(
            UPLOAD_FOLDER, "id_document.jpg"
        )

        live_photo.save(live_path)
        id_document.save(id_path)

        print("\n========================================")
        print("TRUSTNET AI VERIFICATION")
        print("========================================")
        print("User ID:", user_id)

        # -------------------------------
        # MODULE 1: FACE VERIFICATION
        # -------------------------------

        face_verifier = FaceVerifier()

        face_score, face_mass, face_explanation = face_verifier.verify(
            live_path,
            id_path
        )

        # -------------------------------
        # MODULE 2: DOCUMENT VERIFICATION
        # -------------------------------

        document_verifier = DocumentVerifier()

        document_score, document_mass, document_explanation = (
            document_verifier.verify(id_path)
        )

        # -------------------------------
        # MODULE 3: DEMPSTER-SHAFER FUSION
        # -------------------------------

      # -------------------------------
        # MODULE 3: BEHAVIORAL VERIFICATION
        # -------------------------------

        behavioral_verifier = BehavioralVerifier()

        # Get typing data from the HTML form
        keystroke_data = request.form.get("keystroke_data", "")

        if keystroke_data:
            try:
                keystroke_times = json.loads(keystroke_data)

                behavioral_score, behavioral_mass, behavioral_explanation = (
                    behavioral_verifier.verify(
                        user_id,
                        keystroke_times
                    )
                )

            except Exception as e:
                print("Behavioral verification error:", e)

                behavioral_score = 0.5
                behavioral_mass = {
                    "real": 0.3,
                    "fake": 0.3,
                    "unknown": 0.4
                }
                behavioral_explanation = "Behavioral verification could not be completed."

        else:
            behavioral_score = 0.5
            behavioral_mass = {
                "real": 0.3,
                "fake": 0.3,
                "unknown": 0.4
            }
            behavioral_explanation = "No typing data received."


        # -------------------------------
        # MODULE 4: DEMPSTER-SHAFER FUSION
        # -------------------------------

        fusion = TrustFusion()
        behavioral_verifier = BehavioralVerifier()

        # Get typing data from the HTML form
        typing_data = request.form.get("typing_data")

        # Convert typing data into Python list
        import json

        if typing_data:
            try:
                keystroke_times = json.loads(typing_data)
            except:
                keystroke_times = []
        else:
            keystroke_times = []

        # Module 3: Behavioral Verification
        behavioral_score, behavioral_mass, behavioral_explanation = behavioral_verifier.verify(
            user_id,
            keystroke_times
        )

        # Combine all 3 verification modules
        fusion_result = fusion.combine(
            face_mass,
            document_mass,
            behavioral_mass
        )
        # -------------------------------
        # DISPLAY RESULTS
        # -------------------------------

        result = {
    "face_score": round(face_score * 100, 2),
    "face_explanation": face_explanation,

    "document_score": round(document_score * 100, 2),
    "document_explanation": document_explanation,

    "behavioral_score": round(behavioral_score * 100, 2),
    "behavioral_explanation": behavioral_explanation,

    "trust_score": round(
        fusion_result["trust_score"] * 100, 2
    ),

    "decision": fusion_result["decision"]
}

        # -------------------------------
        # PRINT FINAL RESULTS
        # -------------------------------

        print("\n========================================")
        print("FINAL MODULE RESULTS")
        print("========================================")

        print("Face Score:", face_score)
        print("Document Score:", document_score)
        print("Behavioral Score:", behavioral_score)
        print("Trust Score:", fusion_result["trust_score"])
        print("Decision:", fusion_result["decision"])
    return render_template(
        "index.html",
        result=result
    )


if __name__ == "__main__":
    app.run(debug=True)
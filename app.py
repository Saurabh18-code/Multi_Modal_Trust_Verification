from flask import Flask, render_template, request, session, send_file
import os
import json

from modules.face_verification import FaceVerifier
from modules.document_verification import DocumentVerifier
from modules.dempster_shafer import DempsterShaferFusion
from modules.behavioral_verification import BehavioralVerifier
from modules.pdf_generator import generate_pdf_report
import config

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

UPLOAD_FOLDER = "data/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/", methods=["GET", "POST"])
def home():
    result = None

    if request.method == "POST":
        user_id = request.form.get("user_id", "Unknown User")
        live_photo = request.files.get("live_photo")
        id_document = request.files.get("id_document")

        if not live_photo or not id_document:
            result = "Please capture Live Photo and ID Document."
            return render_template("index.html", result=result)

        live_path = os.path.join(UPLOAD_FOLDER, "live_photo.jpg")
        id_path = os.path.join(UPLOAD_FOLDER, "id_document.jpg")

        try:
            live_photo.save(live_path)
            id_document.save(id_path)
        except Exception as e:
            result = "Could not save uploaded files."
            return render_template("index.html", result=result)

        # 1. Face Verification
        try:
            face_verifier = FaceVerifier()
            face_score, face_mass, face_explanation = face_verifier.verify(live_path, id_path)
        except Exception as e:
            face_score, face_mass = 0.0, {"real": 0.0, "fake": 0.0, "unknown": 1.0}
            face_explanation = "Face verification failed due to processing error."

        # 2. Document Verification
        try:
            document_verifier = DocumentVerifier()
            doc_score, doc_mass, doc_explanation = document_verifier.verify(id_path)
        except Exception as e:
            doc_score, doc_mass = 0.0, {"real": 0.0, "fake": 0.0, "unknown": 1.0}
            doc_explanation = "Document verification failed due to processing error."

        # 3. Behavioral Verification
        behavioral_verifier = BehavioralVerifier()
        typing_raw = request.form.get("typing_data", "")

        keystrokes = []
        is_pasted = False
        pointer_velocity = []

        if typing_raw:
            try:
                parsed_data = json.loads(typing_raw)
                if isinstance(parsed_data, dict):
                    keystrokes = parsed_data.get("keystrokes", [])
                    is_pasted = parsed_data.get("isPasted", False)
                    pointer_velocity = parsed_data.get("pointerVelocity", [])
                elif isinstance(parsed_data, list):
                    keystrokes = parsed_data
            except Exception as e:
                pass

        try:
            beh_score, beh_mass, beh_explanation = behavioral_verifier.verify(
                user_id, keystrokes, is_pasted=is_pasted, pointer_velocity=pointer_velocity
            )
        except Exception as e:
            beh_score, beh_mass = 0.5, {"real": 0.3, "fake": 0.3, "unknown": 0.4}
            beh_explanation = "Behavioral verification could not be completed."

        # 4. Dempster-Shafer Fusion
        try:
            fusion = DempsterShaferFusion()
            fusion_result = fusion.fuse(
                (face_score, face_mass, face_explanation),
                (doc_score, doc_mass, doc_explanation),
                (beh_score, beh_mass, beh_explanation)
            )
        except Exception as e:
            fusion_result = {
                "trust_percent": 0.0,
                "decision": "VERIFICATION ERROR",
                "explanation": "Fusion computation failed."
            }

        result = {
            "face_score": round(face_score * 100, 2),
            "face_explanation": face_explanation,
            "document_score": round(doc_score * 100, 2),
            "document_explanation": doc_explanation,
            "behavioral_score": round(beh_score * 100, 2),
            "behavioral_explanation": beh_explanation,
            "trust_score": fusion_result["trust_percent"],
            "decision": fusion_result["decision"]
        }

        # Store in session for PDF generation
        session["latest_result"] = result
        session["latest_user_id"] = user_id

    return render_template("index.html", result=result)


@app.route("/download_report")
def download_report():
    result = session.get("latest_result")
    user_id = session.get("latest_user_id", "Unknown")

    if not result:
        return "No active verification report found. Please complete verification first.", 400

    pdf_buffer = generate_pdf_report(result, user_id=user_id)
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"TrustNet_Report_{user_id}.pdf",
        mimetype="application/pdf"
    )


@app.route("/admin")
def admin():
    return render_template("admin.html") if os.path.exists("templates/admin.html") else "Admin Dashboard"


if __name__ == "__main__":
    app.run(debug=True, port=5000)
Markdown
# Multi-Modal Trust Verification (TrustNet)

A robust, multi-modal identity verification and security platform developed as a final year capstone project. TrustNet combines active liveness detection, document OCR, behavioral telemetry, and secure reporting to calculate an aggregate trust score for identity authentication.

---

## 🚀 Key Features

* **Active Liveness Detection:** Real-time facial verification to ensure the user is physically present and prevent spoofing.
* **Document OCR:** Automated data extraction and verification from identity documents.
* **Behavioral Telemetry:** Analyzes user interaction patterns for enhanced fraud detection and anomaly tracking.
* **Mathematical Trust Scoring:** Fuses multi-modal inputs using **Dempster-Shafer Evidence Theory** to compute an accurate and reliable aggregate trust score.
* **Automated PDF Report Generation:** Instantly generates professional verification audit certificates and summaries using Python and ReportLab (`modules/pdf_generator.py`).
* **Secure Database Logging:** Utilizes an SQLite backend to safely log verification attempts and audit trails.

---

## 🛠️ Tech Stack

* **Backend:** Python, Flask (`app.py`)
* **Frontend:** HTML5, CSS3, JavaScript (`templates/index.html`)
* **Database:** SQLite
* **Modules & Libraries:** ReportLab (PDF Generation), OpenCV, and specialized multi-modal verification modules.

---

## 📁 Project Structure

```text
FINAL YEAR PROJECT/
│
├── app.py                  # Main Flask application backend
├── requirements.txt        # Python package dependencies
├── templates/
│   └── index.html          # Main frontend UI interface
├── modules/
│   └── pdf_generator.py    # ReportLab PDF certificate generator module
└── README.md               # Project documentation
⚙️ Installation & Setup
Follow these steps to set up and run the project locally on your machine:

Clone the repository:

Bash
git clone [https://github.com/harshalpatil362/Multi_Modal_Trust_Verification.git](https://github.com/harshalpatil362/Multi_Modal_Trust_Verification.git)
cd Multi_Modal_Trust_Verification
Create and activate a virtual environment:

Bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
Install dependencies:

Bash
pip install -r requirements.txt
Run the Flask application:

Bash
python app.py
Open your browser and navigate to http://127.0.0.1:5000 to interact with the platform.

📄 License
This project is developed as an academic capstone initiative for final year B.E. Computer Engineering.

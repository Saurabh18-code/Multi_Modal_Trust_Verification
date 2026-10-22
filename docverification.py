# ============================================================
# PROJECT: TrustNet AI - Multi-Modal Digital Trust
#          Intelligence and Authentication Verification Platform
# COLLEGE: St. John College of Engineering and Management, Palghar
# DEPARTMENT: Computer Engineering
# YEAR: B.Tech Final Year (2026-2027)
#
# FILE: modules/document_verification.py
# DESCRIPTION: Module 2 - Extracts text from ID document images
#              using Tesseract OCR, validates document format/
#              pattern rules, and produces a confidence score
#              + DS mass function for fusion
#
# GUIDE: [Guide Name] | [Designation]
# DATE: August 2026
# ============================================================
 
import re
import os
import cv2
import numpy as np
import pytesseract
from PIL import Image
import config
 
# Set Tesseract path (Windows)
pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_PATH
 
 
class DocumentVerifier:
    """
    Document Verification Module for TrustNet AI.
 
    Uses Tesseract OCR to extract text from an ID document image,
    then validates the extracted text against known Indian ID
    document formats (Aadhaar, PAN, Passport).
 
    Output:
        - confidence_score : float (0 to 1)
        - mass_function    : dict  {real, fake, unknown}
        - explanation      : str   (human-readable result)
    """
 
    def __init__(self):
        self.reliability_weight = config.DOCUMENT_RELIABILITY_WEIGHT
        self.document_rules     = config.DOCUMENT_RULES
        self.min_text_length    = config.DOCUMENT_MIN_TEXT_LENGTH
 
    # ─────────────────────────────────────────
    # PRIVATE: Preprocess image for better OCR
    # ─────────────────────────────────────────
    def _preprocess_image(self, image_path):
        """
        Preprocess document image to improve OCR accuracy.
        Steps: Read → Grayscale → Denoise → Threshold → Return
        """
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Cannot read image: {image_path}")
 
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
 
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
 
        # Apply adaptive thresholding for better text contrast
        threshold = cv2.adaptiveThreshold(
            blurred, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11, 2
        )
 
        return threshold
 
    # ─────────────────────────────────────────
    # PRIVATE: Extract text using Tesseract OCR
    # ─────────────────────────────────────────
    def _extract_text(self, image_path):
        """
        Extract all text from document image using Tesseract OCR.
        Returns cleaned text string.
        """
        # Preprocess for better accuracy
        processed_img = self._preprocess_image(image_path)
 
        # Run Tesseract OCR
        # Config: --psm 6 = assume uniform block of text
        custom_config = r"--oem 3 --psm 6"
        raw_text = pytesseract.image_to_string(processed_img, config=custom_config)
 
        # Clean: remove extra spaces, newlines, special chars
        cleaned_text = " ".join(raw_text.split())
        cleaned_text = cleaned_text.upper()   # Uppercase for pattern matching
 
        return cleaned_text
 
    # ─────────────────────────────────────────
    # PRIVATE: Validate Aadhaar number
    # ─────────────────────────────────────────
    def _validate_aadhaar(self, text):
        """
        Find and validate Aadhaar number in extracted text.
        Aadhaar = 12 consecutive digits
        Returns (found: bool, number: str)
        """
        # Find all 12-digit sequences
        pattern = r"\b\d{4}\s?\d{4}\s?\d{4}\b"
        matches = re.findall(pattern, text)
 
        for match in matches:
            # Remove spaces
            number = re.sub(r"\s", "", match)
            if len(number) == 12 and number.isdigit():
                return True, number
 
        return False, ""
 
    # ─────────────────────────────────────────
    # PRIVATE: Validate PAN number
    # ─────────────────────────────────────────
    def _validate_pan(self, text):
        """
        Find and validate PAN number in extracted text.
        PAN format = 5 letters + 4 digits + 1 letter (e.g. ABCDE1234F)
        Returns (found: bool, number: str)
        """
        pattern = r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b"
        matches = re.findall(pattern, text)
 
        if matches:
            return True, matches[0]
 
        return False, ""
 
    # ─────────────────────────────────────────
    # PRIVATE: Validate Passport number
    # ─────────────────────────────────────────
    def _validate_passport(self, text):
        """
        Find and validate Indian Passport number in extracted text.
        Passport format = 1 letter + 7 digits (e.g. A1234567)
        Returns (found: bool, number: str)
        """
        pattern = r"\b[A-Z]{1}[0-9]{7}\b"
        matches = re.findall(pattern, text)
 
        if matches:
            return True, matches[0]
 
        return False, ""
 
    # ─────────────────────────────────────────
    # PRIVATE: Check for required keywords
    # ─────────────────────────────────────────
    def _check_keywords(self, text):
        """
        Check if document contains expected keywords
        that indicate it is a genuine ID document.
        Returns (found_count: int, found_keywords: list)
        """
        id_keywords = [
            "GOVERNMENT", "INDIA", "AADHAAR", "INCOME TAX",
            "PAN", "PASSPORT", "DATE OF BIRTH", "DOB",
            "NAME", "ADDRESS", "VALID", "AUTHORITY"
        ]
 
        found = []
        for keyword in id_keywords:
            if keyword in text:
                found.append(keyword)
 
        return len(found), found
 
    # ─────────────────────────────────────────
    # PRIVATE: Calculate confidence score
    # ─────────────────────────────────────────
    def _calculate_confidence(self, aadhaar_found, pan_found,
                               passport_found, keyword_count,
                               text_length):
        """
        Calculate overall document confidence score based on
        what was found in the extracted text.
 
        Scoring logic:
          - Found valid Aadhaar/PAN/Passport = high score
          - Found relevant keywords = medium score
          - Found some text = low score
          - Nothing found = very low score
        """
        scores = config.DOCUMENT_CONFIDENCE_SCORES
 
        # Priority: valid ID number found first
        if aadhaar_found or pan_found or passport_found:
            if keyword_count >= 3:
                return scores["high"]       # 0.90 - ID number + keywords
            else:
                return 0.75                 # 0.75 - ID number found alone
 
        # Keywords found but no clear ID number
        elif keyword_count >= 4:
            return scores["medium"]         # 0.65
        elif keyword_count >= 2:
            return 0.45
        elif text_length >= config.DOCUMENT_MIN_TEXT_LENGTH:
            return scores["low"]            # 0.30 - some text extracted
        else:
            return scores["very_low"]       # 0.10 - almost nothing found
 
    # ─────────────────────────────────────────
    # PRIVATE: Generate DS mass function
    # ─────────────────────────────────────────
    def _get_mass_function(self, confidence_score):
        """
        Convert confidence score to Dempster-Shafer mass function,
        discounted by this module's reliability weight (0.8).
        """
        w = self.reliability_weight  # 0.8 for document module
 
        if confidence_score >= 0.85:
            m_real = round(0.75 * w, 4)
            m_fake = round(0.05 * w, 4)
        elif confidence_score >= 0.65:
            m_real = round(0.60 * w, 4)
            m_fake = round(0.15 * w, 4)
        elif confidence_score >= 0.45:
            m_real = round(0.35 * w, 4)
            m_fake = round(0.30 * w, 4)
        else:
            m_real = round(0.10 * w, 4)
            m_fake = round(0.65 * w, 4)
 
        m_unknown = round(1.0 - m_real - m_fake, 4)
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
    def _generate_explanation(self, confidence_score, aadhaar_found,
                               pan_found, passport_found, keyword_count,
                               found_keywords, aadhaar_num, pan_num,
                               passport_num, text_length):
        """Generate human-readable explanation of document result"""
 
        found_ids = []
        if aadhaar_found:
            found_ids.append(f"Aadhaar ({aadhaar_num})")
        if pan_found:
            found_ids.append(f"PAN ({pan_num})")
        if passport_found:
            found_ids.append(f"Passport ({passport_num})")
 
        if confidence_score >= 0.85:
            return (f"Document VERIFIED. Valid ID number(s) found: "
                    f"{', '.join(found_ids)}. "
                    f"Keywords detected: {', '.join(found_keywords[:5])}.")
        elif confidence_score >= 0.65:
            if found_ids:
                return (f"Document LIKELY VALID. ID found: {', '.join(found_ids)}. "
                        f"Some keywords detected ({keyword_count}).")
            else:
                return (f"Document PARTIALLY VALID. No clear ID number found but "
                        f"{keyword_count} relevant keywords detected: "
                        f"{', '.join(found_keywords[:3])}.")
        elif confidence_score >= 0.45:
            return (f"Document UNCERTAIN. Limited text extracted ({text_length} chars). "
                    f"Only {keyword_count} keywords found. "
                    f"Image quality may be poor.")
        else:
            return (f"Document FAILED VERIFICATION. Insufficient data extracted. "
                    f"No valid ID numbers or document keywords found. "
                    f"Possible forged or non-standard document.")
 
    # ─────────────────────────────────────────
    # PUBLIC: Main verify function
    # ─────────────────────────────────────────
    def verify(self, document_image_path):
        """
        Main function: Extract and validate text from ID document.
 
        Args:
            document_image_path (str): Path to ID document image
 
        Returns:
            tuple: (confidence_score, mass_function, explanation)
        """
        print("\n" + "=" * 50)
        print("  MODULE 2: DOCUMENT VERIFICATION")
        print("=" * 50)
 
        # ── Step 1: Check image exists ──
        if not os.path.exists(document_image_path):
            explanation = f"ERROR: Document image not found at {document_image_path}"
            print(f"  ✗ {explanation}")
            return 0.0, {"real": 0.05, "fake": 0.90, "unknown": 0.05}, explanation
 
        print(f"  Document Image : {document_image_path}")
 
        # ── Step 2: Extract text via OCR ──
        try:
            extracted_text = self._extract_text(document_image_path)
            text_length    = len(extracted_text)
            print(f"\n  Extracted Text ({text_length} chars):")
            print(f"  '{extracted_text[:200]}{'...' if text_length > 200 else ''}'")
 
        except Exception as e:
            explanation = f"OCR extraction failed: {str(e)}"
            print(f"  ✗ Error: {e}")
            return 0.0, {"real": 0.05, "fake": 0.90, "unknown": 0.05}, explanation
 
        # ── Step 3: Validate ID formats ──
        aadhaar_found,  aadhaar_num  = self._validate_aadhaar(extracted_text)
        pan_found,      pan_num      = self._validate_pan(extracted_text)
        passport_found, passport_num = self._validate_passport(extracted_text)
 
        print(f"\n  ID Number Validation:")
        print(f"    Aadhaar  : {'FOUND (' + aadhaar_num + ')' if aadhaar_found else 'NOT FOUND'}")
        print(f"    PAN      : {'FOUND (' + pan_num + ')' if pan_found else 'NOT FOUND'}")
        print(f"    Passport : {'FOUND (' + passport_num + ')' if passport_found else 'NOT FOUND'}")
 
        # ── Step 4: Check keywords ──
        keyword_count, found_keywords = self._check_keywords(extracted_text)
        print(f"\n  Keywords Found : {keyword_count}")
        print(f"  Keywords       : {found_keywords}")
 
        # ── Step 5: Calculate confidence ──
        confidence_score = self._calculate_confidence(
            aadhaar_found, pan_found, passport_found,
            keyword_count, text_length
        )
 
        # ── Step 6: Generate mass function ──
        mass_function = self._get_mass_function(confidence_score)
 
        # ── Step 7: Generate explanation ──
        explanation = self._generate_explanation(
            confidence_score, aadhaar_found, pan_found, passport_found,
            keyword_count, found_keywords, aadhaar_num, pan_num,
            passport_num, text_length
        )
 
        # ── Step 8: Print results ──
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
    print("  TrustNet AI - Document Verification Module Test")
    print("  St. John College of Engineering and Management, Palghar")
    print("=" * 60)
 
    verifier = DocumentVerifier()
 
    doc_img = "data/sample_docs/sample_id.jpg"
 
    if os.path.exists(doc_img):
        score, mass, explanation = verifier.verify(doc_img)
 
        print("\n" + "=" * 60)
        print("  FINAL OUTPUT:")
        print(f"  Score       : {score:.3f}")
        print(f"  Mass        : {mass}")
        print(f"  Explanation : {explanation}")
        print("=" * 60)
    else:
        print("\n  Sample document image not found.")
        print("  Place a test ID image at: data/sample_docs/sample_id.jpg")
        print("\n  Running DEMO with mock extracted text...")
 
        # Demo: test the validation logic with a fake Aadhaar number
        mock_text = "GOVERNMENT OF INDIA AADHAAR 1234 5678 9012 DATE OF BIRTH 01/01/1999 NAME JOHN DOE ADDRESS PALGHAR MAHARASHTRA"
        print(f"\n  Mock Text: '{mock_text}'")
 
        verifier_demo = DocumentVerifier()
        a_found, a_num   = verifier_demo._validate_aadhaar(mock_text.upper())
        p_found, p_num   = verifier_demo._validate_pan(mock_text.upper())
        kw_count, kw_list = verifier_demo._check_keywords(mock_text.upper())
        conf = verifier_demo._calculate_confidence(a_found, p_found, False, kw_count, len(mock_text))
        mass = verifier_demo._get_mass_function(conf)
 
        print(f"\n  Aadhaar Found : {a_found} ({a_num})")
        print(f"  Keywords      : {kw_count} → {kw_list}")
        print(f"  Confidence    : {conf}")
        print(f"  Mass Function : {mass}")
 
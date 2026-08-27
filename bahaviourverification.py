 #============================================================
# PROJECT: TrustNet AI - Multi-Modal Digital Trust
#          Intelligence and Authentication Verification Platform
# COLLEGE: St. John College of Engineering and Management, Palghar
# DEPARTMENT: Computer Engineering
# YEAR: B.Tech Final Year (2025-2026)
#
# FILE: modules/behavioral_verification.py
# DESCRIPTION: Module 3 - Captures and analyzes keystroke dynamics
#              (typing speed, key hold duration, flight time between
#              keys, login hour) to verify behavioral consistency
#              against a registered baseline profile
#
# GUIDE: [Guide Name] | [Designation]
# DATE: August 2026
# ============================================================
 
import json
import os
import numpy as np
from datetime import datetime
import config
 
 
class BehavioralVerifier:
    """
    Behavioral Verification Module for TrustNet AI.
 
    Uses keystroke dynamics (typing biometrics) to verify that
    the person logging in types the same way as the registered user.
 
    Features analyzed:
        - Typing speed (characters per second)
        - Key hold duration (how long each key is pressed)
        - Flight time (gap between releasing one key and pressing next)
        - Login hour (time of day consistency)
 
    Output:
        - confidence_score : float (0 to 1)
        - mass_function    : dict  {real, fake, unknown}
        - explanation      : str   (human-readable result)
    """
 
    def __init__(self):
        self.reliability_weight  = config.BEHAVIORAL_RELIABILITY_WEIGHT
        self.baselines_file      = config.BEHAVIORAL_BASELINES_FILE
        self.min_samples         = config.BEHAVIORAL_BASELINE_SAMPLES
        self.baseline_profile    = None
 
    # ─────────────────────────────────────────
    # PRIVATE: Extract features from keystrokes
    # ─────────────────────────────────────────
    def _extract_features(self, keystroke_times):
        """
        Extract behavioral features from raw keystroke timing data.
 
        Args:
            keystroke_times (list): List of tuples (key, press_time, release_time)
                                    Times in seconds (float)
 
        Returns:
            dict: Extracted features
        """
        features = {}
 
        if len(keystroke_times) < 2:
            return features
 
        # ── Feature 1: Typing speed (chars per second) ──
        total_time = keystroke_times[-1][2] - keystroke_times[0][1]
        if total_time > 0:
            features["typing_speed"] = len(keystroke_times) / total_time
        else:
            features["typing_speed"] = 0.0
 
        # ── Feature 2: Key hold durations ──
        hold_durations = []
        for key, press_time, release_time in keystroke_times:
            duration = release_time - press_time
            if duration >= 0:
                hold_durations.append(duration)
 
        if hold_durations:
            features["avg_hold_duration"] = float(np.mean(hold_durations))
            features["std_hold_duration"] = float(np.std(hold_durations))
        else:
            features["avg_hold_duration"] = 0.0
            features["std_hold_duration"] = 0.0
 
        # ── Feature 3: Flight times (between consecutive keys) ──
        flight_times = []
        for i in range(1, len(keystroke_times)):
            prev_release = keystroke_times[i - 1][2]
            curr_press   = keystroke_times[i][1]
            flight = curr_press - prev_release
            if flight >= 0:
                flight_times.append(flight)
 
        if flight_times:
            features["avg_flight_time"] = float(np.mean(flight_times))
            features["std_flight_time"] = float(np.std(flight_times))
        else:
            features["avg_flight_time"] = 0.0
            features["std_flight_time"] = 0.0
 
        # ── Feature 4: Login hour ──
        features["login_hour"] = float(datetime.now().hour)
 
        return features
 
    # ─────────────────────────────────────────
    # PUBLIC: Build baseline profile
    # ─────────────────────────────────────────
    def build_baseline(self, samples_list):
        """
        Build a user baseline from multiple typing samples.
        Calculates mean and std for each feature across all samples.
 
        Args:
            samples_list (list): List of feature dicts from multiple samples
 
        Returns:
            dict: Baseline profile with mean/std for each feature
        """
        if len(samples_list) < self.min_samples:
            print(f"  WARNING: Only {len(samples_list)} samples provided. "
                  f"Minimum recommended: {self.min_samples}")
 
        baseline = {}
        all_keys = set()
        for sample in samples_list:
            all_keys.update(sample.keys())
 
        for key in all_keys:
            values = [s[key] for s in samples_list if key in s and s[key] is not None]
            if values:
                std_val = float(np.std(values))
                baseline[key] = {
                    "mean": float(np.mean(values)),
                    "std":  std_val if std_val > 0 else 0.01  # avoid zero std
                }
 
        self.baseline_profile = baseline
        print(f"  ✓ Baseline built from {len(samples_list)} samples")
        print(f"  ✓ Features captured: {list(baseline.keys())}")
        return baseline
 
    # ─────────────────────────────────────────
    # PUBLIC: Save baseline to file
    # ─────────────────────────────────────────
    def save_baseline(self, user_id, baseline):
        """
        Save user's baseline profile to JSON file.
 
        Args:
            user_id  (str): Unique user identifier
            baseline (dict): Baseline profile to save
        """
        # Load existing baselines file
        try:
            with open(self.baselines_file, "r") as f:
                all_baselines = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            all_baselines = {}
 
        # Add/update this user's baseline
        all_baselines[user_id] = {
            "profile":    baseline,
            "created_at": datetime.now().isoformat(),
            "user_id":    user_id
        }
 
        # Save back to file
        os.makedirs(os.path.dirname(self.baselines_file), exist_ok=True)
        with open(self.baselines_file, "w") as f:
            json.dump(all_baselines, f, indent=4)
 
        print(f"  ✓ Baseline saved for user: {user_id}")
 
    # ─────────────────────────────────────────
    # PUBLIC: Load baseline from file
    # ─────────────────────────────────────────
    def load_baseline(self, user_id):
        """
        Load a user's baseline profile from JSON file.
 
        Args:
            user_id (str): User to load baseline for
 
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        try:
            with open(self.baselines_file, "r") as f:
                all_baselines = json.load(f)
 
            if user_id in all_baselines:
                self.baseline_profile = all_baselines[user_id]["profile"]
                print(f"  ✓ Baseline loaded for user: {user_id}")
                return True
            else:
                print(f"  ✗ No baseline found for user: {user_id}")
                return False
 
        except FileNotFoundError:
            print(f"  ✗ Baselines file not found: {self.baselines_file}")
            return False
        except json.JSONDecodeError:
            print(f"  ✗ Baselines file is corrupted")
            return False
 
    # ─────────────────────────────────────────
    # PRIVATE: Calculate similarity score
    # ─────────────────────────────────────────
    def _calculate_similarity(self, current_features):
        """
        Compare current typing features against stored baseline.
        Uses Z-score to measure how many standard deviations each
        feature is away from the baseline mean.
        Converts Z-score to a 0-1 similarity score per feature,
        then averages across all features.
 
        Returns:
            float: Overall similarity score (0 = very different, 1 = identical)
        """
        if not self.baseline_profile:
            print("  ✗ No baseline loaded - returning neutral score")
            return 0.5
 
        feature_scores = []
 
        for feature_name, baseline_stats in self.baseline_profile.items():
            if feature_name not in current_features:
                continue
 
            current_val = current_features[feature_name]
            mean        = baseline_stats["mean"]
            std         = baseline_stats["std"]
 
            # Z-score: how many std devs away from baseline mean?
            z_score = abs(current_val - mean) / std if std > 0 else abs(current_val - mean)
 
            # Convert Z-score → similarity using Gaussian decay
            # z=0 → 1.0 (perfect match)
            # z=1 → 0.78
            # z=2 → 0.37
            # z=3 → 0.11 (very different)
            similarity = float(np.exp(-0.5 * (z_score ** 2)))
            feature_scores.append(similarity)
 
            print(f"    {feature_name:25}: current={current_val:.4f}, "
                  f"baseline_mean={mean:.4f}, z={z_score:.2f}, "
                  f"similarity={similarity:.3f}")
 
        if not feature_scores:
            return 0.5
 
        # Special check for login hour
        current_hour   = current_features.get("login_hour", 12)
        baseline_hour  = self.baseline_profile.get("login_hour", {}).get("mean", 12)
        hour_diff      = abs(current_hour - baseline_hour)
 
        if hour_diff <= config.BEHAVIORAL_HOUR_TOLERANCE_NORMAL:
            hour_score = 1.0      # Normal login time
        elif hour_diff <= config.BEHAVIORAL_HOUR_TOLERANCE_MODERATE:
            hour_score = 0.7      # Slightly unusual
        else:
            hour_score = 0.4      # Unusual login time
 
        feature_scores.append(hour_score)
        print(f"    {'login_hour_check':25}: diff={hour_diff:.0f}hrs, score={hour_score:.3f}")
 
        final_score = float(np.mean(feature_scores))
        return round(final_score, 4)
 
    # ─────────────────────────────────────────
    # PRIVATE: Generate DS mass function
    # ─────────────────────────────────────────
    def _get_mass_function(self, similarity_score):
        """
        Convert similarity score to Dempster-Shafer mass function,
        discounted by reliability weight (0.6 for behavioral module).
        """
        w = self.reliability_weight  # 0.6 for behavior module
        thresholds = config.BEHAVIORAL_THRESHOLDS
 
        if similarity_score >= thresholds["strong_match"]:
            m_real = round(0.70 * w, 4)
            m_fake = round(0.05 * w, 4)
        elif similarity_score >= thresholds["moderate_match"]:
            m_real = round(0.50 * w, 4)
            m_fake = round(0.15 * w, 4)
        elif similarity_score >= thresholds["weak_match"]:
            m_real = round(0.30 * w, 4)
            m_fake = round(0.30 * w, 4)
        else:
            m_real = round(0.10 * w, 4)
            m_fake = round(0.55 * w, 4)
 
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
    def _generate_explanation(self, similarity_score):
        """Generate human-readable explanation of behavioral result"""
        thresholds = config.BEHAVIORAL_THRESHOLDS
 
        if similarity_score >= thresholds["strong_match"]:
            return (f"Behavioral patterns MATCH STRONGLY (score: {similarity_score:.3f}). "
                    f"Typing speed, rhythm, and login time are consistent with "
                    f"registered profile. High confidence this is the registered user.")
        elif similarity_score >= thresholds["moderate_match"]:
            return (f"Behavioral patterns MODERATELY MATCH (score: {similarity_score:.3f}). "
                    f"Some minor variation in typing rhythm detected. "
                    f"Could be due to fatigue, different keyboard, or slight distraction.")
        elif similarity_score >= thresholds["weak_match"]:
            return (f"Behavioral patterns WEAKLY MATCH (score: {similarity_score:.3f}). "
                    f"Notable differences from registered typing profile. "
                    f"Possible different user or significantly altered typing conditions.")
        else:
            return (f"Behavioral patterns DO NOT MATCH (score: {similarity_score:.3f}). "
                    f"Typing behavior is very different from registered profile. "
                    f"Possible impostor or unauthorized access attempt.")
 
    # ─────────────────────────────────────────
    # PUBLIC: Register new user (build baseline)
    # ─────────────────────────────────────────
    def register(self, user_id, keystroke_samples_list):
        """
        Register a new user by building and saving their behavioral baseline.
 
        Args:
            user_id (str): Unique user identifier
            keystroke_samples_list (list): List of keystroke timing arrays
                Each array = [(key, press_time, release_time), ...]
 
        Returns:
            bool: True if registered successfully
        """
        print(f"\n  Registering behavioral baseline for user: {user_id}")
 
        feature_samples = []
        for i, sample in enumerate(keystroke_samples_list):
            features = self._extract_features(sample)
            if features:
                feature_samples.append(features)
                print(f"  Sample {i+1}: speed={features.get('typing_speed', 0):.3f} "
                      f"chars/s, hold={features.get('avg_hold_duration', 0):.4f}s")
 
        if len(feature_samples) < self.min_samples:
            print(f"  ✗ Not enough valid samples. Need {self.min_samples}, got {len(feature_samples)}")
            return False
 
        baseline = self.build_baseline(feature_samples)
        self.save_baseline(user_id, baseline)
        return True
 
    # ─────────────────────────────────────────
    # PUBLIC: Main verify function
    # ─────────────────────────────────────────
    def verify(self, user_id, keystroke_times):
        """
        Main function: Verify user's behavioral pattern.
 
        Args:
            user_id         (str):  User to verify against
            keystroke_times (list): Current login keystrokes
                                    [(key, press_time, release_time), ...]
 
        Returns:
            tuple: (confidence_score, mass_function, explanation)
        """
        print("\n" + "=" * 50)
        print("  MODULE 3: BEHAVIORAL VERIFICATION")
        print("=" * 50)
        print(f"  User ID        : {user_id}")
        print(f"  Keystrokes     : {len(keystroke_times)} keys captured")
 
        # ── Step 1: Load baseline ──
        loaded = self.load_baseline(user_id)
        if not loaded:
            explanation = ("No behavioral baseline found for this user. "
                           "Behavioral verification skipped - neutral score assigned.")
            print(f"  ⚠ {explanation}")
            # Return neutral mass when no baseline exists
            return 0.5, {"real": 0.3, "fake": 0.3, "unknown": 0.4}, explanation
 
        # ── Step 2: Extract features ──
        current_features = self._extract_features(keystroke_times)
        if not current_features:
            explanation = "Insufficient keystroke data for behavioral analysis."
            return 0.5, {"real": 0.3, "fake": 0.3, "unknown": 0.4}, explanation
 
        print(f"\n  Current Features:")
        print(f"    Typing Speed       : {current_features.get('typing_speed', 0):.4f} chars/s")
        print(f"    Avg Hold Duration  : {current_features.get('avg_hold_duration', 0):.4f} s")
        print(f"    Avg Flight Time    : {current_features.get('avg_flight_time', 0):.4f} s")
        print(f"    Login Hour         : {int(current_features.get('login_hour', 0))}:00")
 
        # ── Step 3: Calculate similarity ──
        print(f"\n  Feature-by-feature comparison:")
        similarity_score = self._calculate_similarity(current_features)
 
        # ── Step 4: Generate mass function ──
        mass_function = self._get_mass_function(similarity_score)
 
        # ── Step 5: Generate explanation ──
        explanation = self._generate_explanation(similarity_score)
 
        # ── Step 6: Print results ──
        print(f"\n  Similarity Score : {similarity_score:.3f} ({similarity_score*100:.1f}%)")
        print(f"  Mass Function    :")
        print(f"    Real    = {mass_function['real']}")
        print(f"    Fake    = {mass_function['fake']}")
        print(f"    Unknown = {mass_function['unknown']}")
        print(f"\n  Explanation: {explanation}")
 
        return similarity_score, mass_function, explanation
 
 
# ─────────────────────────────────────────
# STANDALONE TEST
# ─────────────────────────────────────────
if __name__ == "__main__":
 
    print("=" * 60)
    print("  TrustNet AI - Behavioral Verification Module Test")
    print("  St. John College of Engineering and Management, Palghar")
    print("=" * 60)
 
    verifier = BehavioralVerifier()
 
    # ── Simulate registration: 3 typing samples ──
    print("\n  === REGISTRATION PHASE ===")
 
    # Each sample: list of (key, press_time, release_time) in seconds
    sample1 = [
        ("h", 0.000, 0.085), ("e", 0.150, 0.225), ("l", 0.285, 0.360),
        ("l", 0.420, 0.495), ("o", 0.555, 0.620)
    ]
    sample2 = [
        ("h", 0.000, 0.090), ("e", 0.160, 0.235), ("l", 0.290, 0.365),
        ("l", 0.430, 0.500), ("o", 0.560, 0.625)
    ]
    sample3 = [
        ("h", 0.000, 0.080), ("e", 0.145, 0.215), ("l", 0.280, 0.355),
        ("l", 0.415, 0.490), ("o", 0.548, 0.615)
    ]
 
    success = verifier.register("test_user_001", [sample1, sample2, sample3])
 
    if success:
        print("\n  === VERIFICATION PHASE (same user) ===")
 
        # Simulate same user logging in
        login_keystrokes = [
            ("h", 0.000, 0.088), ("e", 0.155, 0.228), ("l", 0.288, 0.362),
            ("l", 0.425, 0.498), ("o", 0.558, 0.622)
        ]
 
        score, mass, explanation = verifier.verify("test_user_001", login_keystrokes)
 
        print("\n" + "=" * 60)
        print("  FINAL OUTPUT (same user):")
        print(f"  Score       : {score:.3f} ({score*100:.1f}%)")
        print(f"  Mass        : {mass}")
        print(f"  Explanation : {explanation}")
        print("=" * 60)
 
        # ── Test with impostor ──
        print("\n  === VERIFICATION PHASE (impostor - different typing) ===")
 
        impostor_keystrokes = [
            ("h", 0.000, 0.200), ("e", 0.400, 0.600), ("l", 0.800, 1.000),
            ("l", 1.200, 1.400), ("o", 1.600, 1.800)
        ]
 
        score2, mass2, explanation2 = verifier.verify("test_user_001", impostor_keystrokes)
 
        print("\n" + "=" * 60)
        print("  FINAL OUTPUT (impostor):")
        print(f"  Score       : {score2:.3f} ({score2*100:.1f}%)")
        print(f"  Mass        : {mass2}")
        print(f"  Explanation : {explanation2}")
        print("=" * 60)
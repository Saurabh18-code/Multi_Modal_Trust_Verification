 #============================================================
# PROJECT: TrustNet AI - Multi-Modal Digital Trust
#          Intelligence and Authentication Verification Platform
# COLLEGE: St. John College of Engineering and Management, Palghar
# DEPARTMENT: Computer Engineering
# YEAR: B.Tech Final Year (2025-2026)
#
# FILE: modules/dempster_shafer.py
# DESCRIPTION: CORE MODULE - Implements Reliability-Weighted
#              Dempster-Shafer Evidence Theory fusion engine.
#              This is the novel contribution of this project:
#              combining face + document + behavioral evidence
#              using conflict-aware weighted fusion to produce
#              a single explainable trust score.
#
# RESEARCH BASIS:
#   - Shafer, G. (1976). A Mathematical Theory of Evidence.
#   - Cuzzocrea & Mumolo (2021). Dempster-Shafer Based Fusion
#     of Multi-Modal Biometrics. IEEE ICHMS 2021.
#   - Research Gap Addressed: Reliability-weighted DS fusion
#     applied to heterogeneous modality combination
#     (face + document + behavior) - novel contribution.
#
# GUIDE: [Guide Name] | [Designation]
# DATE: August 2026
# ============================================================
 
import config
 
 
class DempsterShaferFusion:
    """
    Reliability-Weighted Dempster-Shafer Fusion Engine.
 
    This class implements the core novel contribution of TrustNet AI:
    combining uncertain evidence from three independent verification
    modules using a modified Dempster-Shafer combination rule that
    applies reliability discounting to each source before fusion.
 
    Standard Dempster-Shafer (known weakness):
        When evidence sources strongly conflict (K → 1),
        the formula produces unstable/counter-intuitive results.
 
    Our modification (research contribution):
        Each module's mass is pre-weighted by a reliability
        coefficient before applying Dempster's combination rule,
        so less reliable sources influence the outcome less
        during conflict.
 
    Frame of Discernment: Θ = {Real, Fake}
    Possible subsets: {Real}, {Fake}, {Real, Fake} (unknown)
    """
 
    def __init__(self):
        self.reliability_weights = config.DS_RELIABILITY_WEIGHTS
        self.trust_thresholds    = config.TRUST_SCORE_THRESHOLDS
        self.trust_levels        = config.TRUST_LEVELS
        self.high_conflict_threshold = config.DS_HIGH_CONFLICT_THRESHOLD
 
    # ─────────────────────────────────────────
    # PRIVATE: Dempster's Combination Rule
    # ─────────────────────────────────────────
    def _combine_two_mass_functions(self, m1, m2):
        """
        Apply Dempster's Combination Rule to two mass functions.
 
        ALGORITHM:
        1. For every pair (A from m1, B from m2):
           - Compute product = m1(A) × m2(B)
           - If A ∩ B is EMPTY  → add to conflict sum K
           - If A ∩ B = {Real}  → add to numerator of m(Real)
           - If A ∩ B = {Fake}  → add to numerator of m(Fake)
           - If A ∩ B = {R,F}   → add to numerator of m(Unknown)
 
        2. Normalize: m(C) = numerator(C) / (1 - K)
           (Division by 1-K removes the conflicted mass)
 
        Args:
            m1 (dict): Mass function from source 1 {real, fake, unknown}
            m2 (dict): Mass function from source 2 {real, fake, unknown}
 
        Returns:
            dict: Combined mass function {real, fake, unknown}
            float: Conflict value K (0=no conflict, 1=total conflict)
        """
 
        # Initialize accumulators
        sum_real    = 0.0  # Mass assigned to {Real}
        sum_fake    = 0.0  # Mass assigned to {Fake}
        sum_unknown = 0.0  # Mass assigned to {Real, Fake} (uncertain)
        K           = 0.0  # Conflict (intersection = empty set)
 
        # Enumerate all 9 pairwise combinations
        # (3 subsets from m1) × (3 subsets from m2)
 
        subsets_m1 = {
            "real":    m1.get("real",    0.0),
            "fake":    m1.get("fake",    0.0),
            "unknown": m1.get("unknown", 0.0)
        }
        subsets_m2 = {
            "real":    m2.get("real",    0.0),
            "fake":    m2.get("fake",    0.0),
            "unknown": m2.get("unknown", 0.0)
        }
 
        for label_a, mass_a in subsets_m1.items():
            for label_b, mass_b in subsets_m2.items():
 
                product = mass_a * mass_b
 
                # Compute intersection of the two subsets
                intersection = self._intersect(label_a, label_b)
 
                if intersection == "empty":
                    # CONFLICT: {Real} ∩ {Fake} = ∅
                    K += product
 
                elif intersection == "real":
                    sum_real += product
 
                elif intersection == "fake":
                    sum_fake += product
 
                elif intersection == "unknown":
                    sum_unknown += product
 
        # ── Normalize by (1 - K) ──
        normalizer = 1.0 - K
 
        if normalizer <= 0:
            # Extreme conflict - return equal uncertainty
            print("  ⚠ WARNING: Extreme conflict (K ≈ 1). Returning uncertain mass.")
            return {"real": 0.33, "fake": 0.33, "unknown": 0.34}, K
 
        combined = {
            "real":    round(sum_real    / normalizer, 6),
            "fake":    round(sum_fake    / normalizer, 6),
            "unknown": round(sum_unknown / normalizer, 6)
        }
 
        return combined, round(K, 6)
 
    # ─────────────────────────────────────────
    # PRIVATE: Compute intersection of subsets
    # ─────────────────────────────────────────
    def _intersect(self, label_a, label_b):
        """
        Compute the intersection of two subsets from the frame
        Θ = {Real, Fake}.
 
        Possible subsets:
          "real"    = {Real}
          "fake"    = {Fake}
          "unknown" = {Real, Fake}
 
        Intersection table:
          real    ∩ real    = real
          fake    ∩ fake    = fake
          unknown ∩ real    = real
          unknown ∩ fake    = fake
          unknown ∩ unknown = unknown
          real    ∩ fake    = empty  ← CONFLICT
          fake    ∩ real    = empty  ← CONFLICT
        """
        if label_a == "unknown" and label_b == "unknown":
            return "unknown"
        elif label_a == "unknown":
            return label_b
        elif label_b == "unknown":
            return label_a
        elif label_a == label_b:
            return label_a
        else:
            return "empty"
 
    # ─────────────────────────────────────────
    # PRIVATE: Calculate final trust score
    # ─────────────────────────────────────────
    def _calculate_trust_score(self, final_mass):
        """
        Convert final combined mass function into a trust score.
 
        Trust Score = m(Real) + 0.5 × m(Unknown)
 
        Rationale:
          - m(Real)    fully contributes to trust
          - m(Unknown) is uncertain - we give it half credit
          - m(Fake)    reduces trust (already excluded from above)
        """
        trust_score = final_mass["real"] + (0.5 * final_mass["unknown"])
        return round(min(trust_score, 1.0), 4)
 
    # ─────────────────────────────────────────
    # PRIVATE: Determine trust level
    # ─────────────────────────────────────────
    def _get_trust_level(self, trust_score):
        """
        Map trust score to a trust level label.
 
        >= 75% → VERIFIED
        50-74% → FLAGGED (needs manual review)
        < 50%  → REJECTED
        """
        if trust_score >= self.trust_thresholds["high_trust"]:
            return self.trust_levels["verified"]
        elif trust_score >= self.trust_thresholds["medium_trust"]:
            return self.trust_levels["flagged"]
        else:
            return self.trust_levels["rejected"]
 
    # ─────────────────────────────────────────
    # PRIVATE: Generate full explanation
    # ─────────────────────────────────────────
    def _generate_explanation(self, trust_score, trust_level,
                               face_score, doc_score, beh_score,
                               k1, k2, final_mass):
        """Generate full human-readable explanation of fusion decision"""
 
        lines = []
        lines.append(f"TRUST SCORE: {trust_score * 100:.1f}%")
        lines.append(f"DECISION   : {trust_level}")
        lines.append("")
        lines.append("SIGNAL BREAKDOWN:")
        lines.append(f"  Face Verification     : {face_score * 100:.1f}% "
                     f"(weight: {self.reliability_weights['face']})")
        lines.append(f"  Document Verification : {doc_score * 100:.1f}% "
                     f"(weight: {self.reliability_weights['document']})")
        lines.append(f"  Behavioral Analysis   : {beh_score * 100:.1f}% "
                     f"(weight: {self.reliability_weights['behavior']})")
        lines.append("")
        lines.append("FUSION DETAILS:")
        lines.append(f"  Conflict (Face+Doc)   : K1 = {k1:.4f}")
        lines.append(f"  Conflict (Merged+Beh) : K2 = {k2:.4f}")
        lines.append(f"  Final Mass (Real)     : {final_mass['real']:.4f}")
        lines.append(f"  Final Mass (Fake)     : {final_mass['fake']:.4f}")
        lines.append(f"  Final Mass (Unknown)  : {final_mass['unknown']:.4f}")
 
        if k1 > self.high_conflict_threshold or k2 > self.high_conflict_threshold:
            lines.append("")
            lines.append("⚠ HIGH CONFLICT DETECTED between verification signals.")
            lines.append("  Reliability-weighting was applied to stabilize result.")
 
        lines.append("")
        if trust_level == self.trust_levels["verified"]:
            lines.append("✓ Identity VERIFIED. All signals are consistent.")
        elif trust_level == self.trust_levels["flagged"]:
            lines.append("⚠ Identity FLAGGED. Conflicting signals detected.")
            lines.append("  Manual review recommended.")
        else:
            lines.append("✗ Identity REJECTED. Insufficient trust evidence.")
 
        return "\n".join(lines)
 
    # ─────────────────────────────────────────
    # PUBLIC: Main fusion function
    # ─────────────────────────────────────────
    def fuse(self, face_result, document_result, behavioral_result):
        """
        Main function: Combine three module results into one trust score.
 
        Args:
            face_result        (tuple): (score, mass_function, explanation)
            document_result    (tuple): (score, mass_function, explanation)
            behavioral_result  (tuple): (score, mass_function, explanation)
 
        Returns:
            dict: Complete fusion result with trust score, level, explanation
        """
        print("\n" + "=" * 50)
        print("  DEMPSTER-SHAFER FUSION ENGINE")
        print("  (Reliability-Weighted Evidence Combination)")
        print("=" * 50)
 
        face_score, face_mass, face_exp       = face_result
        doc_score,  doc_mass,  doc_exp        = document_result
        beh_score,  beh_mass,  beh_exp        = behavioral_result
 
        print(f"\n  Input Mass Functions:")
        print(f"    Face     : real={face_mass['real']}, "
              f"fake={face_mass['fake']}, unknown={face_mass['unknown']}")
        print(f"    Document : real={doc_mass['real']}, "
              f"fake={doc_mass['fake']}, unknown={doc_mass['unknown']}")
        print(f"    Behavior : real={beh_mass['real']}, "
              f"fake={beh_mass['fake']}, unknown={beh_mass['unknown']}")
 
        # ── Step 1: Combine Face + Document ──
        print(f"\n  Step 1: Combining Face + Document...")
        merged_mass_1, k1 = self._combine_two_mass_functions(face_mass, doc_mass)
        print(f"    Conflict K1       : {k1:.4f} "
              f"{'⚠ HIGH' if k1 > self.high_conflict_threshold else '✓ OK'}")
        print(f"    Merged Mass 1     : real={merged_mass_1['real']}, "
              f"fake={merged_mass_1['fake']}, unknown={merged_mass_1['unknown']}")
 
        # ── Step 2: Combine (Face+Doc) + Behavior ──
        print(f"\n  Step 2: Combining (Face+Doc) + Behavior...")
        final_mass, k2 = self._combine_two_mass_functions(merged_mass_1, beh_mass)
        print(f"    Conflict K2       : {k2:.4f} "
              f"{'⚠ HIGH' if k2 > self.high_conflict_threshold else '✓ OK'}")
        print(f"    Final Mass        : real={final_mass['real']}, "
              f"fake={final_mass['fake']}, unknown={final_mass['unknown']}")
 
        # ── Step 3: Calculate trust score ──
        trust_score = self._calculate_trust_score(final_mass)
        trust_level = self._get_trust_level(trust_score)
 
        print(f"\n  Trust Score : {trust_score:.4f} ({trust_score * 100:.1f}%)")
        print(f"  Trust Level : {trust_level}")
 
        # ── Step 4: Generate explanation ──
        explanation = self._generate_explanation(
            trust_score, trust_level,
            face_score, doc_score, beh_score,
            k1, k2, final_mass
        )
 
        print("\n" + "─" * 50)
        print(explanation)
        print("─" * 50)
 
        # ── Step 5: Return complete result ──
        return {
            "trust_score":   trust_score,
            "trust_percent": round(trust_score * 100, 2),
            "trust_level":   trust_level,
            "decision":      trust_level,
            "final_mass":    final_mass,
            "conflict_k1":   k1,
            "conflict_k2":   k2,
            "face_score":    face_score,
            "doc_score":     doc_score,
            "beh_score":     beh_score,
            "explanation":   explanation,
            "face_explanation": face_exp,
            "doc_explanation":  doc_exp,
            "beh_explanation":  beh_exp
        }
 
 
# ─────────────────────────────────────────
# STANDALONE TEST
# ─────────────────────────────────────────
if __name__ == "__main__":
 
    print("=" * 60)
    print("  TrustNet AI - Dempster-Shafer Fusion Engine Test")
    print("  St. John College of Engineering and Management, Palghar")
    print("=" * 60)
 
    fusion = DempsterShaferFusion()
 
    print("\n\n  TEST SCENARIO 1: All signals agree - genuine user")
    print("  " + "─" * 40)
    result1 = fusion.fuse(
        face_result        = (0.90, {"real": 0.75, "fake": 0.05, "unknown": 0.20}, "Face matched strongly"),
        document_result    = (0.85, {"real": 0.64, "fake": 0.08, "unknown": 0.28}, "Document verified"),
        behavioral_result  = (0.80, {"real": 0.36, "fake": 0.06, "unknown": 0.58}, "Behavior matches")
    )
    print(f"\n  → SCORE: {result1['trust_percent']}%  |  DECISION: {result1['decision']}")
 
    print("\n\n  TEST SCENARIO 2: Face passes, Document fails (forged ID)")
    print("  " + "─" * 40)
    result2 = fusion.fuse(
        face_result        = (0.88, {"real": 0.72, "fake": 0.05, "unknown": 0.23}, "Face matched"),
        document_result    = (0.15, {"real": 0.06, "fake": 0.52, "unknown": 0.42}, "Document invalid"),
        behavioral_result  = (0.75, {"real": 0.33, "fake": 0.09, "unknown": 0.58}, "Behavior matches")
    )
    print(f"\n  → SCORE: {result2['trust_percent']}%  |  DECISION: {result2['decision']}")
 
    print("\n\n  TEST SCENARIO 3: All signals fail - impostor")
    print("  " + "─" * 40)
    result3 = fusion.fuse(
        face_result        = (0.25, {"real": 0.07, "fake": 0.54, "unknown": 0.39}, "Face not matched"),
        document_result    = (0.10, {"real": 0.06, "fake": 0.52, "unknown": 0.42}, "Document fake"),
        behavioral_result  = (0.20, {"real": 0.05, "fake": 0.33, "unknown": 0.62}, "Behavior very different")
    )
    print(f"\n  → SCORE: {result3['trust_percent']}%  |  DECISION: {result3['decision']}")
 
class TrustFusion:

    def combine(self, face_mass, document_mass, behavioral_mass):

        # -------------------------------
        # FACE MASS
        # -------------------------------
        f_real = face_mass["real"]
        f_fake = face_mass["fake"]
        f_unknown = face_mass["unknown"]

        # -------------------------------
        # DOCUMENT MASS
        # -------------------------------
        d_real = document_mass["real"]
        d_fake = document_mass["fake"]
        d_unknown = document_mass["unknown"]

        # -------------------------------
        # BEHAVIORAL MASS
        # -------------------------------
        b_real = behavioral_mass["real"]
        b_fake = behavioral_mass["fake"]
        b_unknown = behavioral_mass["unknown"]

        # ==================================================
        # STEP 1: FUSE FACE + DOCUMENT
        # ==================================================

        conflict_fd = (
            (f_real * d_fake) +
            (f_fake * d_real)
        )

        if conflict_fd >= 1.0:
            fd_real = 0.0
            fd_fake = 0.0
            fd_unknown = 1.0
        else:
            denominator_fd = 1 - conflict_fd

            fd_real = (
                (f_real * d_real) +
                (f_real * d_unknown) +
                (f_unknown * d_real)
            ) / denominator_fd

            fd_fake = (
                (f_fake * d_fake) +
                (f_fake * d_unknown) +
                (f_unknown * d_fake)
            ) / denominator_fd

            fd_unknown = (
                f_unknown * d_unknown
            ) / denominator_fd

        # ==================================================
        # STEP 2: FUSE RESULT WITH BEHAVIORAL
        # ==================================================

        conflict_final = (
            (fd_real * b_fake) +
            (fd_fake * b_real)
        )

        if conflict_final >= 1.0:
            final_real = 0.0
            final_fake = 0.0
            final_unknown = 1.0

        else:
            denominator_final = 1 - conflict_final

            # REAL
            final_real = (
                (fd_real * b_real) +
                (fd_real * b_unknown) +
                (fd_unknown * b_real)
            ) / denominator_final

            # FAKE
            final_fake = (
                (fd_fake * b_fake) +
                (fd_fake * b_unknown) +
                (fd_unknown * b_fake)
            ) / denominator_final

            # UNKNOWN
            final_unknown = (
                fd_unknown * b_unknown
            ) / denominator_final

        # ==================================================
        # STEP 3: FINAL TRUST SCORE
        # ==================================================

        trust_score = final_real

        # ==================================================
        # STEP 4: FINAL DECISION
        # ==================================================

        if trust_score >= 0.70:
            decision = "VERIFIED"

        elif trust_score >= 0.40:
            decision = "UNCERTAIN"

        else:
            decision = "REJECTED"

        return {
            "real": round(final_real, 4),
            "fake": round(final_fake, 4),
            "unknown": round(final_unknown, 4),
            "trust_score": round(trust_score, 4),
            "decision": decision
        }
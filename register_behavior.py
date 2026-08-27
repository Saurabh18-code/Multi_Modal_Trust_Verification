from modules.behavioral_verification import BehavioralVerifier

verifier = BehavioralVerifier()

user_id = input("Enter User ID: ")

print("\nType your sentence 3 times.")
print("For now, we will use sample typing data.\n")

sample1 = [
    ("T", 0.000, 0.100),
    ("r", 0.150, 0.220),
    ("u", 0.270, 0.340),
    ("s", 0.390, 0.460),
    ("t", 0.510, 0.580),
    (" ", 0.630, 0.680),
    ("N", 0.730, 0.820),
    ("e", 0.870, 0.940),
    ("t", 0.990, 1.060)
]

sample2 = [
    ("T", 0.000, 0.105),
    ("r", 0.155, 0.225),
    ("u", 0.275, 0.345),
    ("s", 0.395, 0.465),
    ("t", 0.515, 0.585),
    (" ", 0.635, 0.685),
    ("N", 0.735, 0.825),
    ("e", 0.875, 0.945),
    ("t", 0.995, 1.065)
]

sample3 = [
    ("T", 0.000, 0.095),
    ("r", 0.145, 0.215),
    ("u", 0.265, 0.335),
    ("s", 0.385, 0.455),
    ("t", 0.505, 0.575),
    (" ", 0.625, 0.675),
    ("N", 0.725, 0.815),
    ("e", 0.865, 0.935),
    ("t", 0.985, 1.055)
]

success = verifier.register(
    user_id,
    [sample1, sample2, sample3]
)

if success:
    print("\n================================")
    print("BEHAVIORAL REGISTRATION SUCCESS")
    print("================================")
    print("User:", user_id)
    print("Baseline created successfully.")
else:
    print("\nBehavioral registration failed.")
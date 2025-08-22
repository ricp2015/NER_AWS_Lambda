# testing/locust_ner.py
from locust import HttpUser, task, LoadTestShape, events
import os, json, random, gevent, time

# ------------ Env knobs ------------
BASE_URL = os.environ.get("NER_API_BASE_URL")  # e.g. https://abc123.execute-api.us-east-1.amazonaws.com
SCENARIO = os.environ.get("SCENARIO", "B").upper()  # A, B, C, D

# Warm-up
WARMUP_SECONDS    = int(os.environ.get("WARMUP_SECONDS", "60"))
WARMUP_USERS      = int(os.environ.get("WARMUP_USERS", "2"))
WARMUP_SPAWN_RATE = int(os.environ.get("WARMUP_SPAWN_RATE", "2"))
FAST_WARMUP       = os.environ.get("FAST_WARMUP", "1") in ("1", "true", "True")

# Heavy mode
HEAVY       = os.environ.get("HEAVY", "0") in ("1","true","True")
HEAVY_USERS = int(os.environ.get("HEAVY_USERS", "10"))  # stay ≤10 in Learner Lab
HEAVY_SPAWN = int(os.environ.get("HEAVY_SPAWN", "5"))
HIGH_RPS = os.environ.get("HIGH_RPS", "0") in ("1","true","True")

# Payload-only-long-texts mode
LONG_TEXTS = os.environ.get("LONG_TEXTS", "0") in ("1","true","True")

# Hard stop (seconds) – safety guard; 0 = disabled
HARD_STOP_SECS = int(os.environ.get("HARD_STOP_SECS", "0"))

# Warm-up flag (affects wait pacing)
IN_WARMUP = True

# ------------ Payloads ------------
SAMPLES = [
    "Tim Cook met Elon Musk in Rome on Monday.",
    "Barack Obama visited Berlin in 2013.",
    "Amazon acquired Whole Foods for $13.7 billion in 2017.",
    "The conference will be held at Stanford University in California.",
    ("OpenAI collaborated with Microsoft to expand Azure’s AI capabilities, "
     "hosting a conference in San Francisco attended by researchers from MIT and Stanford."),
    ("The European Commission met with Apple and Google executives in Brussels to discuss "
     "Digital Markets Act implications for app stores across the EU."),
    ("At the annual developer summit in New York, representatives from IBM, NVIDIA, and Meta "
     "announced new initiatives with the University of Toronto, the University of Oxford, and "
     "Carnegie Mellon University, aiming to support startups and publish research results in 2025.")
]

def scenario_wait():
    # If we want maximum throughput, shrink think time for all heavy scenarios
    if HIGH_RPS or HEAVY:
        # ~0–0.1s pauses → high RPS; keep D (endurance) moderate
        if SCENARIO == "D":
            return random.uniform(1.0, 3.0)
        return random.uniform(0.0, 0.1)

    # Non-heavy defaults (baseline profiles)
    if SCENARIO == "A":   # Bursty users with long think-time
        return random.uniform(5.0, 10.0)
    if SCENARIO == "D":   # Endurance (low RPS)
        return random.uniform(1.0, 3.0)
    # B or C (faster)
    return random.uniform(0.2, 1.0)


class NerUser(HttpUser):
    # Provide Host via env var (or fill Host in UI if None)
    if BASE_URL:
        host = BASE_URL

    # Use a dynamic wait function (Locust calls this between tasks)
    def wait_time(self):
        if IN_WARMUP and FAST_WARMUP:
            return random.uniform(0.2, 0.8)
        return scenario_wait()

    @task
    def ner(self):
        texts = [t for t in SAMPLES if len(t) > 160] if LONG_TEXTS else SAMPLES
        payload = {"text": random.choice(texts)}
        self.client.post(
            "/ner",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )

class TrafficShape(LoadTestShape):
    """
    Staged load with a Warm-Up phase first (WU), then main scenario.
    We auto-reset stats right after WU so charts/CSVs reflect only RU→S→RD.
    Durations below are per-segment (not cumulative).
    """
    def __init__(self):
        super().__init__()
        # ----- Main scenario stages (after WU) -----
        if SCENARIO == "A":   # Bursty (intermittent)
            main = [(300, 5, 1)]  # 5m @5
            if HEAVY:
                main = [(360, HEAVY_USERS, HEAVY_SPAWN)]  # ~6m @ up to 10
        elif SCENARIO == "B": # Ramp→Steady
            # baseline: ~12m main (ramp 6m, steady 4m, rampdown 2m)
            main = [
                (60, 1, 1), (60, 3, 2), (60, 5, 2), (60, 6, 2), (60, 7, 2), (60, 8, 3),
                (240, 8, 2),
                (60, 4, 4), (60, 1, 4)
            ]
            if HEAVY:
                # ~10m main: ramp to HEAVY, short steady, rampdown
                main = [
                    (60, 2, 2), (60, 5, 3), (60, 8, 3), (60, HEAVY_USERS, HEAVY_SPAWN),
                    (240, HEAVY_USERS, HEAVY_SPAWN),
                    (60, 4, 6), (60, 1, 6)
                ]
        elif SCENARIO == "C": # Spike
            main = [(30, 1, 2), (240, 8, 8), (60, 2, 6)]  # ~5.5m
            if HEAVY:
                main = [(30, 2, 4), (240, HEAVY_USERS, HEAVY_SPAWN), (60, 2, 8)]
        else:                 # D: Endurance (low RPS, long S)
            main = [(900, 2, 1)]  # 15m

        # Prepend WU stage
        self.stages = [("WU", WARMUP_SECONDS, WARMUP_USERS, WARMUP_SPAWN_RATE)]
        # Tag main stages as MAIN
        for seg in main:
            dur, u, r = seg
            self.stages.append(("MAIN", dur, u, r))

        self.run_started_at = time.time()

    def tick(self):
        # Hard stop guard
        if HARD_STOP_SECS > 0 and (self.get_run_time() >= HARD_STOP_SECS):
            return None

        run_time = self.get_run_time()
        for label, duration, users, rate in self.stages:
            if run_time < duration:
                return (users, rate)
            run_time -= duration
        return None

# -------- Auto-reset stats right after warm-up --------
@events.test_start.add_listener
def _on_test_start(environment, **kwargs):
    def _reset_after_wu():
        global IN_WARMUP
        gevent.sleep(WARMUP_SECONDS)
        IN_WARMUP = False
        if environment.runner:
            try:
                environment.runner.stats.reset_all()
                environment.runner.stats.reset_all_exceptions()
            except Exception:
                try:
                    environment.stats.reset_all()
                except Exception:
                    pass
        print(f"--- Locust stats reset after warm-up ({WARMUP_SECONDS}s) ---")
    gevent.spawn(_reset_after_wu)

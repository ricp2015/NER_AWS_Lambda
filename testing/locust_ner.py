# testing/locust_ner.py
from locust import HttpUser, task, between, LoadTestShape, events
import os, json, random, gevent

# -------- Config via env --------
BASE_URL = os.environ.get("NER_API_BASE_URL")  # e.g., https://abc123.execute-api.us-east-1.amazonaws.com
SCENARIO = os.environ.get("SCENARIO", "B").upper()  # A, B, C, D

# Warm-up knobs
WARMUP_SECONDS     = int(os.environ.get("WARMUP_SECONDS", "60"))
WARMUP_USERS       = int(os.environ.get("WARMUP_USERS", "2"))
WARMUP_SPAWN_RATE  = int(os.environ.get("WARMUP_SPAWN_RATE", "2"))
FAST_WARMUP        = os.environ.get("FAST_WARMUP", "1") in ("1", "true", "True")

# Global warm-up flag used by wait() to speed up WU if requested
IN_WARMUP = True

# -------- Payloads --------
SAMPLES = [
    "Ciao, come stai oggi a Roma?",
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
    # Non-WU pacing per scenario
    if SCENARIO == "A":   # Bursty (intermittent)
        return random.uniform(5.0, 10.0)
    if SCENARIO == "D":   # Endurance (low RPS)
        return random.uniform(1.0, 3.0)
    # B or C (faster)
    return random.uniform(0.2, 1.0)

class NerUser(HttpUser):
    if BASE_URL:
        host = BASE_URL

    # we override wait() to make warm-up faster when FAST_WARMUP=1
    wait_time = between(0, 0)

    def wait(self):
        if IN_WARMUP and FAST_WARMUP:
            self._sleep(random.uniform(0.2, 0.8))
        else:
            self._sleep(scenario_wait())

    @task
    def ner(self):
        payload = {"text": random.choice(SAMPLES)}
        self.client.post(
            "/ner",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )

class TrafficShape(LoadTestShape):
    """
    Staged load with a Warm-Up phase first.
    After WARMUP_SECONDS, we reset Locust stats so final graphs exclude WU.
    """
    def __init__(self):
        super().__init__()
        # ----- Main scenario stages (after WU) -----
        if SCENARIO == "A":
            main = [(300, 5, 1)]  # 5 min @ 5 users
# inside class TrafficShape(LoadTestShape).__init__
        elif SCENARIO == "B":
            # RAMP: 1→8 over ~6m (60s steps), STEADY: 6m, RAMPDOWN: 2m  => ~14m main (+ WU 60s ≈ 15m total)
            main = [
                (60, 1, 1),
                (60, 3, 2),
                (60, 5, 2),
                (60, 6, 2),
                (60, 7, 2),
                (60, 8, 3),   # ramp totals ~6m
                (360, 8, 2),  # steady 6m
                (60, 4, 4),
                (60, 1, 4)    # rampdown 2m
            ]
        elif SCENARIO == "C":
            # SPIKE: quick jump to 8, hold ~4m, rampdown 1m => ~5.5m main (+ WU)
            main = [
                (30, 1, 2),
                (240, 8, 8),
                (60, 2, 6)
            ]

        else:  # D
            main = [(900, 2, 1)]  # 15 min low concurrency

        # Prepend Warm-Up stage
        self.stages = [("WU", WARMUP_SECONDS, WARMUP_USERS, WARMUP_SPAWN_RATE)]
        # Then tag the main stages so we know when WU ends (for stats reset timer)
        for dur, u, r in main:
            self.stages.append(("MAIN", dur, u, r))

        self.elapsed = 0
        self.wu_done = False

    def tick(self):
        run_time = self.get_run_time()
        elapsed = 0
        for label, duration, users, rate in self.stages:
            if run_time < duration:
                # At the first tick AFTER warm-up ends, flip flag so our test_start hook can reset stats
                if label == "MAIN" and not self.wu_done:
                    self.wu_done = True
                return (users, rate)
            run_time -= duration
            elapsed += duration
        return None  # stop test

# -------- Auto-reset stats right after warm-up --------
@events.test_start.add_listener
def _on_test_start(environment, **kwargs):
    def _reset():
        global IN_WARMUP
        gevent.sleep(WARMUP_SECONDS)
        # Mark warm-up finished (affects wait behavior)
        IN_WARMUP = False

        # Reset Locust stats so graphs/CSV exclude WU samples
        if environment.runner:
            try:
                environment.runner.stats.reset_all()
                environment.runner.stats.reset_all_exceptions()
            except Exception:
                # Fallback for older/newer locust versions
                try:
                    environment.stats.reset_all()
                except Exception:
                    pass
        print(f"--- Locust stats reset after warm-up ({WARMUP_SECONDS}s) ---")
    gevent.spawn(_reset)

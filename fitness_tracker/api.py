import time
import random
import threading
from typing import Callable, Optional

class MockSensorAPI:
    def __init__(self):
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._callbacks: list[Callable[[dict], None]] = []
        
        # Simulation state
        self.current_heart_rate = 70
        self.total_steps = 0
        self.start_time = 0

    def add_callback(self, callback: Callable[[dict], None]):
        """Register a callback to receive live data updates."""
        self._callbacks.append(callback)

    def start_stream(self):
        """Start the mock data stream."""
        if self._running:
            return
        
        self._running = True
        self.start_time = time.time()
        self.total_steps = 0
        self._thread = threading.Thread(target=self._generate_data, daemon=True)
        self._thread.start()

    def stop_stream(self):
        """Stop the mock data stream."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
            self._thread = None

    def _generate_data(self):
        """Internal loop to generate mock data."""
        while self._running:
            # Simulate heart rate fluctuation
            change = random.randint(-2, 3)
            self.current_heart_rate = max(60, min(180, self.current_heart_rate + change))
            
            # Simulate steps (approx 2 steps per second if running)
            self.total_steps += random.choice([0, 1, 1, 2])
            
            elapsed = time.time() - self.start_time
            
            data = {
                "timestamp": time.time(),
                "elapsed_seconds": elapsed,
                "heart_rate": self.current_heart_rate,
                "steps": self.total_steps
            }
            
            for callback in self._callbacks:
                callback(data)
            
            time.sleep(1.0) # Update every second

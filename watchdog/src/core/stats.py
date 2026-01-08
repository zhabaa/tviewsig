from datetime import datetime


class WatchdogStats:
    def __init__(self):
        self.signals_processed = 0
        self.signals_sent = 0
        self.last_processed = None
        self.errors = 0

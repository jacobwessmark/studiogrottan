# led.py
import neopixel
import machine
import _thread
import time
import logging

class LEDControl:
    def __init__(self, pin, num_leds, logger=None):
        if logger is None:
            logger = logging.getLogger(__name__)
        self.logger = logger
        try:
            self.np = neopixel.NeoPixel(machine.Pin(pin, machine.Pin.OUT), num_leds)
            self.color = (0, 0, 0)
            self.mode = "solid"  # Default mode
            self.lock = _thread.allocate_lock()
            _thread.start_new_thread(self.run, ())
            self.blink(color=(255, 0, 0), interval=3)  # Blink on init to indicate readiness
            self.logger.info("LEDControl initialized successfully")
        except Exception as e:
            self.logger.error("Failed to initialize LEDControl: %s", str(e))
            raise  # Optionally re-raise if initialization failure is critical

    def run(self):
        while True:
            try:
                self.lock.acquire()
                mode = self.mode
                color = self.color
                self.lock.release()

                if mode == "solid":
                    self.solid(color)
                elif mode == "blink":
                    self.blink(color)
                elif mode == "chase":
                    self.chase(color)
                time.sleep(0.1)
            except Exception as e:
                self.logger.error("Error during run loop: %s", str(e))
                time.sleep(1)  # Pause before continuing loop to prevent spamming logs if error persists

    def solid(self, color):
        try:
            self.logger.debug("Running solid color mode")
            for i in range(len(self.np)):
                self.np[i] = color
            self.np.write()
        except Exception as e:
            self.logger.error("Error in solid mode: %s", str(e))

    def blink(self, color, interval=3):
        try:
            self.logger.debug("Running blink mode with interval %s", interval)
            self.np.fill((0, 0, 0))
            self.np.write()
            time.sleep(interval)
            self.np.fill(color)
            self.np.write()
            time.sleep(interval)
        except Exception as e:
            self.logger.error("Error in blink mode: %s", str(e))

    def chase(self, color, interval=0.1):
        try:
            self.logger.debug("Running chase mode with interval %s", interval)
            for i in range(len(self.np)):
                self.np[i] = (0, 0, 0)
            for i in range(len(self.np)):
                self.np[i] = color
                if i > 0:
                    self.np[i - 1] = (0, 0, 0)
                self.np.write()
                time.sleep(interval)
        except Exception as e:
            self.logger.error("Error in chase mode: %s", str(e))

    def set_color(self, r, g, b):
        try:
            with self.lock:
                self.color = (r, g, b)
                self.logger.info("Color set to (%s, %s, %s)", r, g, b)
        except Exception as e:
            self.logger.error("Error setting color: %s", str(e))

    def set_mode(self, mode):
        try:
            with self.lock:
                self.mode = mode
                self.logger.info("Mode set to %s", mode)
        except Exception as e:
            self.logger.error("Error setting mode: %s", str(e))

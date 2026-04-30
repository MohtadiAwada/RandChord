from pychord import Chord
import pyaudio
import numpy as np
import threading

SAMPLE_RATE = 44100
NOTE_DURATION = 0.25

def _note_freq(note: str) -> float:
    """Convert a note name like 'A4' to its frequency in Hz."""
    semitones = {
        'C': -9, 'C#': -8, 'Db': -8, 'D': -7, 'D#': -6, 'Eb': -6,
        'E': -5, 'F': -4, 'F#': -3, 'Gb': -3, 'G': -2, 'G#': -1,
        'Ab': -1, 'A': 0, 'A#': 1, 'Bb': 1, 'B': 2
    }
    for name in sorted(semitones, key=len, reverse=True):
        if note.startswith(name):
            octave = int(note[len(name):])
            n = semitones[name] + (octave - 4) * 12
            return 440.0 * (2 ** (n / 12))
    raise ValueError(f"Unknown note: {note}")

def _sine_wave(freq: float, duration: float) -> bytes:
    """Generate a sine wave as raw bytes for pyaudio."""
    import numpy as np
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    fade = int(SAMPLE_RATE * 0.01)
    wave = np.sin(2 * np.pi * freq * t).astype(np.float32)
    wave[:fade] *= np.linspace(0, 1, fade)
    wave[-fade:] *= np.linspace(1, 0, fade)
    return wave.tobytes()

class Music:
    def __init__(self):
        self._pa = pyaudio.PyAudio()
        self._stop_event = threading.Event()
        self._thread = None

    def _playChord(self, chord_name: str, stop_event: threading.Event):
        chord = Chord(chord_name)
        notes = chord.components_with_pitch(root_pitch=4)
        stream = self._pa.open(format=pyaudio.paFloat32, channels=1, rate=SAMPLE_RATE, output=True)
        try:
            played = 0
            while played < 8:
                for note in notes:
                    if stop_event.is_set():
                        return
                    stream.write(_sine_wave(_note_freq(note), NOTE_DURATION))
                    played += 1
                    if played >= 8:
                        break
        finally:
            stream.stop_stream()
            stream.close()

    def _playProg(self, chord_prog: list, stop_event: threading.Event):
        for chord_name in chord_prog:
            if stop_event.is_set():
                return
            self._playChord(chord_name, stop_event)

    def playProg(self, chord_prog: list):
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join()

        self._stop_event = threading.Event()
        self._thread = threading.Thread(
            target=self._playProg,
            args=(chord_prog, self._stop_event),
            daemon=True,
        )
        self._thread.start()

    def stop(self):
        self._stop_event.set()

    def __del__(self):
        self.stop()
        self._pa.terminate()
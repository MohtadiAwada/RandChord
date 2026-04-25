from pychord import Chord
from pysinewave import SineWave
import time
import threading

class Music:
    def __init__(self):
        self.pitch = {
            # Octave 3
            'C3': -12, 'C#3': -11, 'Db3': -11, 'D3': -10, 'D#3': -9, 'Eb3': -9, 
            'E3': -8, 'F3': -7, 'F#3': -6, 'Gb3': -6, 'G3': -5, 'G#3': -4, 
            'Ab3': -4, 'A3': -3, 'A#3': -2, 'Bb3': -2, 'B3': -1,
            
            # Octave 4
            'C4': 0, 'C#4': 1, 'Db4': 1, 'D4': 2, 'D#4': 3, 'Eb4': 3, 
            'E4': 4, 'F4': 5, 'F#4': 6, 'Gb4': 6, 'G4': 7, 'G#4': 8, 
            'Ab4': 8, 'A4': 9, 'A#4': 10, 'Bb4': 10, 'B4': 11,
            
            # Octave 5
            'C5': 12, 'C#5': 13, 'Db5': 13, 'D5': 14, 'D#5': 15, 'Eb5': 15, 
            'E5': 16, 'F5': 17, 'F#5': 18, 'Gb5': 18, 'G5': 19, 'G#5': 20, 
            'Ab5': 20, 'A5': 21, 'A#5': 22, 'Bb5': 22, 'B5': 23,

            # Octave 6
            'C6': 24, 'C#6': 25, 'Db6': 25, 'D6': 26, 'D#6': 27, 'Eb6': 27, 
            'E6': 28, 'F6': 29, 'F#6': 30, 'Gb6': 30, 'G6': 31, 'G#6': 32, 
            'Ab6': 32, 'A6': 33, 'A#6': 34, 'Bb6': 34, 'B6': 35
        }

        self._stop_event = threading.Event()
        self._thread = None

    def _playChord(self, chord_name: str, stop_event: threading.Event):
        chord = Chord(chord_name)
        played = 0
        while played < 8:
            for i in chord.components_with_pitch(root_pitch=4):
                if stop_event.is_set():
                    return
                note = SineWave(pitch=self.pitch[i])
                note.play()
                # Check the stop event every 50ms instead of sleeping the full 250ms at once
                for _ in range(5):
                    if stop_event.is_set():
                        note.stop()
                        return
                    time.sleep(0.05)
                note.stop()
                played += 1
                if played >= 8:
                    break

    def _playProg(self, chord_prog: list, stop_event: threading.Event):
        for chord_name in chord_prog:
            if stop_event.is_set():
                return
            self._playChord(chord_name, stop_event)

    def playProg(self, chord_prog: list):
        # Signal any running playback to stop
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join()

        # Reset the event and start fresh
        self._stop_event = threading.Event()
        self._thread = threading.Thread(
            target=self._playProg,
            args=(chord_prog, self._stop_event),
            daemon=True,
        )
        self._thread.start()

    def stop(self):
        """Immediately stop any ongoing playback."""
        self._stop_event.set()
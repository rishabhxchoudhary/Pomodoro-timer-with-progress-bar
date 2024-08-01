import time
import progressbar
import os
from threading import Thread, Event
import simpleaudio as sa

class PomodoroTimer:
    def __init__(self, work_time, break_time, cycles):
        self.work_time = work_time * 60
        self.break_time = break_time * 60
        self.cycles = cycles
        self.current_cycle = 0
        self.paused = Event()
        self.stopped = Event()
        self.sound_stopped = Event()
        self.paused.set()
        self.sound_stopped.set()
        self.thread = Thread(target=self.run_timer)
        
    def notify(self, message):
        os.system(f"""
                  osascript -e 'display notification "{message}" with title "Pomodoro Timer"'
                  """)
    def stop_sound(self):
        print("In stop_sound")
        input("Press Enter to stop the alarm: ")
        self.sound_stopped.set()

    def play_sound(self):
        wave_obj = sa.WaveObject.from_wave_file("alarm.wav")
        play_obj = wave_obj.play()
        play_obj.wait_done()


    def countdown(self, total_time, message):
        widgets = [
            ' [', progressbar.Percentage(), '] ',
            progressbar.Bar(), ' (', progressbar.ETA(), ') '
        ]
        bar = progressbar.ProgressBar(max_value=total_time, widgets=widgets).start()
        start = time.time()
        for t in range(total_time):
            if self.stopped.is_set():
                bar.finish()
                return
            self.paused.wait()
            bar.update(t + 1)
            time.sleep(1)
        bar.finish()
        print("Time Elapsed: ", time.time() - start)
        self.notify(message)
        self.play_sound()

    def run_timer(self):
        while self.current_cycle < self.cycles and not self.stopped.is_set():
            print(f"Cycle {self.current_cycle + 1}")
            self.notify(f"Cycle {self.current_cycle + 1} - Work Time")
            print(f"Work for {self.work_time//60} minutes")
            self.countdown(self.work_time, "Break Time")
            
            if self.stopped.is_set():
                break
            
            print(f"Take a {self.break_time//60}-minute break")
            self.notify("Break Time - Relax")
            self.countdown(self.break_time, "Work Time")
            
            self.current_cycle += 1
        
        if not self.stopped.is_set():
            self.notify("Pomodoro session complete!")
            print("Pomodoro session complete!")

    def start(self):
        self.thread.start()
        
    def pause(self):
        self.paused.clear()
        
    def resume(self):
        self.paused.set()
        
    def stop(self):
        self.stopped.set()
        self.paused.set()
        self.thread.join()

def main():
    work_time = int(input("Enter work time in minutes: "))
    break_time = int(input("Enter break time in minutes: "))
    cycles = int(input("Enter the number of cycles: "))
    
    timer = PomodoroTimer(work_time, break_time, cycles)
    timer.start()
    
    while timer.thread.is_alive():
        command = input("Enter 'p' to pause, 'r' to resume, 'q' to quit: ").strip().lower()
        if command == 'p':
            timer.pause()
        elif command == 'r':
            timer.resume()
        elif command == 'q':
            timer.stop()
            break

if __name__ == "__main__":
    main()

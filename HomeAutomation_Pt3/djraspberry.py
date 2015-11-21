import os, signal, subprocess, time

VOLUME_SETTINGS = (LOW, MEDIUM, NORMAL, HI, MAX) = ('low', 'medium', 'normal', 'hi', 'max')
COMMANDS = (PLAY, STOP, PAUSE, RESUME, VOLUME) = ('play', 'stop', 'pause', 'resume', 'volume')
VOLUME_CONTROL = {LOW: 0, MEDIUM: 10, NORMAL: 20, HI: 25, MAX: 30}

class DJRaspberry(object):

    def __init__(self):
        self.music_process = None
        self.current_volume = VOLUME_CONTROL[NORMAL]

    def stop_music(self):
        if self.music_process:
            os.killpg(self.music_process.pid, signal.SIGTERM)
            self.music_process = None

    def adjust_volume(self, target_volume):
        if not self.music_process:
            return
        target_volume = VOLUME_CONTROL.get(target_volume.split(' ')[0])
        while self.current_volume < target_volume:
            self.current_volume += 1
            self.music_process.stdin.write("=")
            time.sleep(1)

        while self.current_volume > target_volume:
            self.current_volume -= 1
            self.music_process.stdin.write("-")
            time.sleep(1)

    def pause_and_resume(self):
        if self.music_process:
            self.music_process.stdin.write(" ".format(**locals()))

    def play_music(self, song):
        self.stop_music()
        self.music_process = subprocess.Popen('sudo mpsyt;'.format(**locals()),
                                              shell=True,
                                              stdout=subprocess.PIPE,
                                              stdin=subprocess.PIPE,
                                              preexec_fn=os.setsid)
        self.music_process.stdin.write("/{song}\n1\n".format(**locals()))

    def run(self, data):
        action = data.split(' ')[0]
        if PLAY in action:
            self.play_music(data.split(PLAY)[1].strip())
        elif STOP in action:
            self.stop_music()
        elif VOLUME in action:
            self.adjust_volume(data.split(VOLUME)[1].strip())
        elif PAUSE in action or RESUME in action:
            self.pause_and_resume()
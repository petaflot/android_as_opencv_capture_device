import subprocess
class Camera:
    app_string = 'foundation.e.camera'
    filename = None

    def start(self):
        subprocess.run(['adb', 'shell', 'am start -a android.media.action.IMAGE_CAPTURE'])
        res = subprocess.run(['adb', 'shell', f'pidof {self.app_string}'], capture_output=True)
        self.pid = int(res.stdout.strip().decode())

    def set(self):
        print("NotImplemented")
        pass

    def read(self):
        try:
            res = subprocess.run(['adb', 'shell', f'pidof {self.app_string}'], capture_output=True)
            self.pid = int(res.stdout.strip().decode())
        except ValueError:
            self.pid = None
            self.start()
        finally:
            #print(f"Camera {self.pid=}")
            # ensure app is in foreground
            res = subprocess.run(['adb', 'shell', 'dumpsys activity activities'], capture_output=True)
            for line in res.stdout.split(b'\n')[::-1]:
                line = line.strip().split(b':',1)
                if line[0] == b'VisibleActivityProcess':
                    if bytes(f" {self.pid}:{self.app_string}/",'ascii') in line[1]:
                        # app is already in foreaground
                        pass
                    else:
                        # TODO this is flaky!!! won't work if camera is not ready to capture (ie. settings open)
                        subprocess.run(['adb', 'shell', f'monkey -p {self.app_string} 1'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    break

            subprocess.run(['adb', 'shell', 'input keyevent CAMERA'])
            res = subprocess.run(['adb', 'shell', 'ls -t /sdcard/DCIM/Camera/*.jpg'], capture_output=True)
            self.filename = res.stdout.split(b'\n')[0]

    def download(self, delete=False):
        # TODO only delete if pull was successfull, chekc and return exit status
        subprocess.run(['adb', 'pull',self.filename], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        if delete:
            subprocess.run(['adb', 'shell', 'rm', self.filename], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            self.filename = None

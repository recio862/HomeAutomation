import imaplib
import subprocess
import email
import yaml
import os
import signal
import time
from djraspberry import DJRaspberry

send_command = 'sudo ./codesend '
last_checked = -1
commands = yaml.load(open('commands.yaml'))

dj = DJRaspberry()

def execute_command(data):
    if 'dj' in data:
        dj.run(data.split('dj')[1].strip())

    for key in commands.keys():
        split_keys = key.split(' ') if isinstance(key, str) else key
        filtered = filter(lambda x: x in data, split_keys)
        if filtered == split_keys:
            send_codes(commands[key])
            break

def send_codes(codes):
    command = send_command + codes if isinstance(codes, str) else ''
    if isinstance(codes, list):
        for code in codes:
            command += 'sudo ./codesend {code};'.format(**locals())
    p = subprocess.Popen(command,
                         shell=True,
                         stdout=subprocess.PIPE,
                         cwd='/home/pi/433Utils/RPi_utils',
                         preexec_fn=os.setsid)
    time.sleep(1)
    os.killpg(p.pid, signal.SIGTERM)

def fetch_siri_command(mail):
    global last_checked
    mail.list()
    mail.select("Notes")
    result, uidlist = mail.search(None, "ALL")
    latest_email_id = uidlist[0].split()[-1]
    if latest_email_id == last_checked:
        return
    last_checked = latest_email_id
    result, data = mail.fetch(latest_email_id, "(RFC822)")
    voice_command = email.message_from_string(data[0][1]).get_payload()
    return voice_command.strip().lower()


def main(username, password):
    mail = imaplib.IMAP4_SSL('imap.gmail.com', 993)
    mail.login(username, password)
    while True:
        try:
            command = fetch_siri_command(mail)
            if command:
                execute_command(command)
        except Exception as exc:
            print("Received an exception while running: {exc}"
                  "\nRestarting...".format(**locals()))

if __name__ == '__main__':
    main(username, password)

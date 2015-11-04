import imaplib
import time
import subprocess
import email
import yaml

last_checked = -1
commands = yaml.load(open('commands.yaml'))

def execute_command(data):
    for key in commands.keys():
        split_keys = key.split(' ')
        filtered = filter(lambda x: x in data, split_keys)
        if filtered == split_keys:
            send_codes(list(commands[key]))
            break

def send_codes(codes):
    command = ''
    for code in codes:
        command += 'sudo ./codesend {code};'.format(**locals())
    p = subprocess.Popen(command,
                         shell=True,
                         stdout=subprocess.PIPE,
                         cwd='/home/pi/433Utils/RPi_utils')

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
        time.sleep(1)

if __name__ == '__main__':
    main('gmail_username', 'gmail_password')

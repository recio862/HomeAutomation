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

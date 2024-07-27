# Establishes a connection to the database and configures the logging

import socket
import sqlite3
import classes_Server as classes
import time
import json
import os.path
import sys

if sys._git[0] != "CPython":
    print("This program only works with CPython")
    sys.exit()

# Reads the server configuration from config_server.json
with open("config_server.json", "r") as f:
    data = json.load(f)

# Prints the logo defined in the server configuration
print(data["logo"]["logo"])

# Initializes a socket and retrieves the server host and port from the configuration
s = socket.socket()
host = data["server"]["host"]
port = data["server"]["port"]
s.bind((host, port))

# Connects to the SQLite database and creates a users table if it does not exist
conn = sqlite3.connect(data["database"]["name"])
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        name text not null,
        pw text
    )
''')

# Creates a UserDatabase instance to interact with the database
db = classes.UserDatabase(cursor, conn)

# Retrieves the username and password dictionary from the database
un_and_pw_dictionary = db.inquire()

# Initializes a Log instance for logging server activities to a file
log = classes.Log("log/server_" + time.strftime("%Y-%m-%d", time.localtime()) + ".log")
log.write("DEBUG", f"Start! time:{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")

# Listens for incoming connections and handles client requests
if __name__ == "__main__":
    s.listen(5)

    while True:
        c, addr = s.accept()

        # Receives and processes client messages
        msg = c.recv(1024 * 10).decode("utf-8").split(" ")
        print('ip address:', addr, "Connection attempts:", msg, end=" ", flush=True)

        # Validates the username and password received from the client
        if msg[0] in un_and_pw_dictionary.keys():
            if un_and_pw_dictionary[msg[0]][0] != msg[1]:
                log.write("Error", f"longin:{addr}-try:{msg}-PwError")
                c.send(b"PW or UserName Error")
                c.close()
                print("Passwords vary", flush=True)
                continue
        else:
            log.write("Error", f"longin:{addr}-try:{msg}-UserNameError")
            print("Username not found", flush=True)
            c.send(b"PW or UserName Error")
            c.close()
            continue

        # Sends a start message to the client to indicate successful login
        c.send(data["server"]["start"].encode("utf-8"))
        log.write("DEBUG", f"longin:{addr}-try:{msg}-Succeed")

        # Initializes a Command instance to handle client commands
        cmd = classes.Command(log.name, data["server"]["loc"], un_and_pw_dictionary[msg[0]][1])
        print("The connection is successful")

        # Receives and processes client commands
        while 1:
            get = c.recv(1024 ** 3).decode("utf-8").split(" ")
            log.write("DEBUG", f"from:{addr}-get:{get}")

            # If the client sends an 'exit' message, disconnects from the client
            if get[0] == "exit":
                log.write("DEBUG", f"{addr}-LogOut")
                c.send(data["server"]["end"].encode("utf-8"))
                print("connect:", addr, "disconnection")
                break
            print(get)
            # Executes the client command and sends the result back to the client
            data = cmd.run(get[0], get[1:])
            try:
                data = data.encode("utf-8")
            except AttributeError as e:
                pass
            c.send(str(len(data) // 1024 + 1).encode("utf-8"))
            try:
                start = 0                   # start index of data to send
                end = min(1024, len(data))  # end index of data to send
                while start < len(data):
                    result = data[start:end]
                    c.send(result)
                    start = end
                    end = min(start + 1024, len(data))
                    print("The result of the command execution:", result)
            except Exception as e:
                print(e)
                log.write("Error", f"{addr}-send:{e}")

        # Closes the connection with the client
        c.close()

# Logs the end of server activities
log.write("DEBUG", f"End! time:{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")

# Closes the database connection
conn.close()

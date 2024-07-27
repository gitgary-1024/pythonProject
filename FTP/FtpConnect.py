import socket  # Import the socket module
import json
import classes
import time
import cmd

login = classes.Log("log/connect_" + time.strftime("%Y-%m-%d", time.localtime()) + ".log")


try:
    with open("config_connect.json", "r") as f:
        data = json.load(f)

    s = socket.socket()  # Create a socket object
    port = data["connect"]["port"]  # Set the port number
    s.connect((data["connect"]["host"], port))

    login.write("DEBUG", f"Start! time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")

    print(data["other"]["logo"])

    u_p = input("Please enter username and password: (separated by a space)")
    # Perform secure processing and validation of the username and password
    s.send(u_p.encode("utf-8"))

    if __name__ == "__main__":
        print(s.recv(1024 * 10).decode("utf-8"), flush=True)

        while 1:
            get = input().encode("utf-8")
            login.write("DEBUG", f"send :{get}")
            if len(get) >= 1024 ** 3:
                login.write("ERROR", f"input too large:{len(get)}")
                print(f"Input larger than {1024 ** 3} bytes", flush=True)
                continue

            s.send(get)
            length = int(s.recv(1024).decode("utf-8"))
            print(f"Received {length} bytes of data", flush=True)
            print(length, flush=True)
            for i in range(length):
                print(s.recv(1024).decode("utf-8"), flush=True)

            if get == b"exit":
                login.write("DEBUG", "exit")
                print(s.recv(1024 ** 3), flush=True)
                break
    login.write("DEBUG", f"Stop! time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")
    s.close()
except Exception as e:
    print(e)
    login.write("ERROR", str(e))

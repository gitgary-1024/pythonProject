import os
import sqlite3
import operator
import logging
import chardet
import cmd


# noinspection PyMethodMayBeStatic

class DatabaseError(Exception):
    def __init__(self, *args, **kwargs):
        pass


class CommandError(Exception):
    def __init__(self, *args, **kwargs):
        pass


# noinspection PyMethodMayBeStatic
class UserDatabase:
    def __init__(self, cursor, conn):
        self.cursor = cursor
        self.conn = conn

    def insert(self, content):  # insert new user
        """
            :return: Null
            """
        try:
            self.cursor.execute("INSERT INTO users (name, pw) VALUES (?, ?)", content)
            self.conn.commit()
        except sqlite3.Error as e:
            raise DatabaseError(e)

    def inquire(self):  # inquire all users
        """
            :return: Dictionary, {username:(password,permission);...}
            """
        dit = {}
        try:
            self.cursor.execute("SELECT * FROM users")
            rows = self.cursor.fetchall()
            for row in rows:
                dit[row[0]] = (row[1], row[2])
        except sqlite3.Error as e:
            raise DatabaseError(e)
        return dit

    def update(self, content):  # update password
        """
            :param content: A tuple, (new name, new password)
            :return: Null
            """
        try:
            self.cursor.execute("UPDATE users SET pw = ? WHERE name = ?", content)
            self.conn.commit()
        except sqlite3.Error as e:
            raise DatabaseError(e)

    def delete(self, content):  # delete user
        """
            :param content: A tuple, (name,)
            :return: Null
            """
        try:
            self.cursor.execute("DELETE FROM users WHERE name = ?", content)
            self.conn.commit()
        except sqlite3.Error as e:
            raise DatabaseError(e)


# noinspection PyMethodMayBeStatic
class Log:
    def __init__(self, name):
        self.name = name
        logging.basicConfig(filename=self.name, filemode="a",
                            format="%(asctime)s -%(levelname)s -%(filename)s -%(message)s", level=logging.DEBUG,
                            encoding="utf-8")

    def write(self, level, information):
        """
        :param level: string
        :param information: string
        """
        if level == "DEBUG":
            logging.debug(information)
        else:
            logging.error(information)

    def clean(self):
        with open(self.name, "w") as f:
            f.write("")

    def delete(self):
        os.remove(self.name)
        return os.path.isfile(self.name)


# noinspection PyMethodMayBeStatic,PyUnusedLocal,PyComparisonWithNone
class Command(cmd.Cmd):  # this class is used to communicate with the server
    def __init__(self, user_db, log, socket):
        """
        :param user_db:
        :param log:
        :param socket: socket.socket
        """

        self.prompt = "FPT connect> "  # prompt of the command line
        super().__init__()
        self.user_db = user_db  # user database
        self.log = log  # log file
        self.socket = socket  # socket object

    def send_message(self, message):  # send message to the server
        """
        :param message: string
        """
        length = len(message.encode("utf-8"))
        if length > 1024 ** 3:
            print(f"Message too long (more than {1024 ** 3} bytes)")
            return False
        self.socket.send(str(length).encode("utf-8"))
        try:
            start = 0
            end = min(1024, length)
            while start < length:
                result = data[start:end]
                c.send(result)
                start = end
                end = min(start + 1024, len(data))
                # print("The result of the command execution:", result)
        except Exception as e:
            print(e)
            log.write("Error", f"{addr}-send:{e}")
            return False
        return True

    def get_message(self):
        """
        :return: bytes
        """
        length = int(self.socket.recv(1024).decode("utf-8"))
        message = b""
        for i in range(length):
            message += self.socket.recv(1024)
        return message

    def do_help(self, arg):
        """
        :param arg: Null
        """
        if self.send_message("help"):
            print("Waiting for response...")
        print(self.get_message().decode("utf-8"))

    def do_copy(self, arg):
        """
        :param arg: <old file name> <new file name>
        :return:
        """
        if self.send_message(f"copy {arg}"):
            print("Waiting for response...")
        print(self.get_message().decode("utf-8"))

    def do_move(self, arg):
        """
        :param arg: <old file name>
        :return:
        """
        if self.send_message(f"move {arg}"):
            print("Waiting for response...")
        print(self.get_message().decode("utf-8"))

    def do_remove(self, arg):
        """
        :param arg: <file name>
        :return:
        """
        if self.send_message(f"remove {arg}"):
            print("Waiting for response...")
        print(self.get_message().decode("utf-8"))

    def do_del_dir(self, arg):
        """
        :param arg: <dir name>
        :return:
        """
        if self.send_message(f"del_dir {arg}"):
            print("Waiting for response...")
        print(self.get_message().decode("utf-8"))

    def do_mkdir(self, arg):
        """
        :param arg: <new directory name>
        :return:
        """
        if self.send_message(f"mkdir {arg}"):
            print("Waiting for response...")
        print(self.get_message().decode("utf-8"))

    def do_download(self, arg):
        """
        :param arg: <file name>
        :return:
        """
        if self.send_message(f"download {arg}"):
            print("Waiting for response...")
            with open(arg, "wb") as f:
                f.write(self.get_message())
        else:
            print("Failed to send message")

    def do_upload(self, arg):
        """
        :param arg: <file name>
        :return:
        """
        if os.path.isfile(arg):
            with open(arg, "rb") as f:
                print("Waiting for response...")
                massage = str(f.read())
                self.send_message(f"upload {arg}" + massage)
            print(self.get_message().decode("utf-8"))

        else:
            print("File not found")

    def do_ls(self, arg):
        """
        :param arg: Null
        :return:
        """
        if self.send_message("ls"):
            print("Waiting for response...")
            print(self.get_message().decode("utf-8"))
        else:
            print("Failed to send message")

    def do_now(self, arg):
        """
        :param arg: Null
        :return:
        """
        if self.send_message("now"):
            print("Waiting for response...")
            print(self.get_message().decode("utf-8"))
        else:
            print("Failed to send message")

    def do_exit(self, arg):
        """
        :param arg: Null
        :return:
        """
        if self.send_message("exit"):
            print("Waiting for response...")
            print(self.get_message().decode("utf-8"))
        else:
            print("Failed to send message")
        return True

    def do_quit(self, arg):
        """
        :param arg: Null
        :return:
        """
        self.do_exit(arg)
        return True

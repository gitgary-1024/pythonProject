import os
import sqlite3
import operator
import logging
import chardet


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
class Command:
    def __init__(self, log, loc, permission):
        self.__log = Log(log)
        self.__location = loc
        self.__permission = permission

    # Define a method to run a command with arguments
    def run(self, cmd, args):
        # Use getattr to obtain the method object based on the command
        method = getattr(self, cmd, None)

        # Check for restricted commands containing "self" or "_"
        if "self." in cmd or "_" in cmd:
            # Log and return an error message
            self.__log.write("error", f":Denied when attempting to access: {cmd}")
            return f"Unknown directives: {cmd} : {args}"

        # Check if the method exists and is callable
        if cmd is not None and callable(method):
            # Call the method and log the action
            self.__log.write("DEBUG", f'run:{cmd} : {args}')
            return method(args)
        else:
            # Log and return an error message for unknown directives
            self.__log.write("error", f"Unknown directives: {cmd} : {args}")
            return f"Unknown directives: {cmd} : parameters {args}"

    def now(self, args):
        """

show current location
:param args: None
        """
        return f"Current location: {self.__location}"

    def goto(self, args):
        """

change current location
:param args: A tuple, (new location)
        """
        print(args)
        if os.path.isdir(args[0]):
            self.__location = args[0]
            return f"Goto {args[0]} successful"
        else:
            return f"There is no location {args[0]}"

    def ls(self, args):
        """

list files and directories in current directory
:param args: None
        """
        s = ""
        for i in os.listdir(self.__location):
            s += (i + "\n")
        return s

    def upload(self, args):
        """

upload file
:param args: A tuple, (file name, file content)
        """
        if os.path.isfile(args[0]):
            return f"The file already exists: {args[0]} "
        try:
            with open(os.path.join(self.__location, args[0]), "a", encoding="utf-8") as f:
                f.write(args[1])
            return f"Upload {args[0]} successful"
        except Exception as e:
            return f"Upload {args[0]} failed: {e}"

    def download(self, args):
        """

download file
:param args: A tuple, (file name)
        """
        if os.path.isfile(os.path.join(self.__location, args[0])):
            try:
                with open(os.path.join(self.__location, args[0]), "rb", encoding="utf-8") as f:
                    data = f.read()
                return data
            except Exception as e:
                return f"Download {args[0]} failed: {e}"
        else:
            return f"There is no file {args[0]}"

    def make_dir(self, args):
        """

create directory
:param args: A tuple, (new directory name)
        """
        try:
            os.mkdir(os.path.join(self.__location, args[0]))
            return f"Create directory {args[0]} successful"
        except Exception as e:
            return f"Create directory {args[0]} failed: {e}"

    def del_dir(self, args):
        """

remove directory
:param args: A tuple, (old directory name)
        """
        try:
            os.rmdir(os.path.join(self.__location, args[0]))
            return f"Remove directory {args[0]} successful"
        except Exception as e:
            return f"Remove directory {args[0]} failed: {e}"

    def remove(self, args):
        """

remove file
:param args: A tuple, (file name)
        """
        try:
            os.remove(os.path.join(self.__location, args[0]))
            return f"Remove file {args[0]} successful"
        except Exception as e:
            return f"Remove file {args[0]} failed: {e}"

    def move(self, args):
        """

move file from source to destination
:param args: A tuple, (source, destination)
        """
        try:
            os.rename(os.path.join(self.__location, args[0]), os.path.join(self.__location, args[1]))
            return f"Move file {args[0]} to {args[1]} successful"
        except Exception as e:
            return f"Move file {args[0]} to {args[1]} failed: {e}"

    def copy(self, args):
        """

copy file from source to destination
:param args: A tuple, (source, destination)
        """
        try:
            with open(os.path.join(self.__location, args[0]), "rb") as f:
                data = f.read()
            with open(os.path.join(self.__location, args[1]), "ab") as f:
                f.write(data)
            return f"Copy file {args[0]} to {args[1]} successful"
        except Exception as e:
            return f"Copy file {args[0]} to {args[1]} failed: {e}"

    def help(self, args):
        if args:
            try:
                doc = getattr(self, args[0]).__doc__
                if doc:
                    return "%s\n" % str(doc)
            except AttributeError:
                pass
        else:
            names = ""
            for name in dir(self):
                if not name.startswith("_"):
                    names += "%s\n" % name
            return names

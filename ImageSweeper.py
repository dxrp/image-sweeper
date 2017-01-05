import os
import struct
import time
from os import getcwd
from time import gmtime, strftime
#from basc_py4chan import File

import basc_py4chan
import requests

class Run(object):
    intro = ("dxrp's chan Image Sweeper.                                        |\n"
             "Version 0.1a - built 14:14 27/12/16  elementaryOS-linux           |\n"
             "Project home - https://github.com/dxrp/image-sweeper branch-master|\n"
             "Written using Python 3.5.2 | Type '?' for a list of actions.      |\n"
             "-------------------------------------------------------------------\n")
    print(intro)
    help = ("Image Sweeper action list:\n"
            "update        - Grabs latest Image Sweeper package from Github\n"
            "%thread_link% - Enter a valid boards.4chan.org thread link to sweep.\n"
            "exit          - Ends ImageSweeper.py process.\n"
            "?             - Lists actions\n"
            "clear         - Deletes everything where Image Sweeper saves its images."
            "\n\nIf the chan you want to sweep has an API and similar python wrappers (I'm sure\nyou can edit the basc_py4chan wrappers) for the API,"
            " feel free to use this as a base.\n")

    def __init__(self):
            pass

    def main(self):
        try:
            self.parse_action(self.NewAction())
        except Exception as e:
            print("Error: " + str(e))

    def NewAction(self) -> str:
        action = input("IS> ")
        return action

    def update(self):
        update = Update()
        if update.check_vers():
            print("Checking github.com/dxrp/image-sweeper for updates... ",end="")
            print("update found! Starting update...\n")
            update.main()
        else:
            print("Checking github.com/dxrp/image-sweeper for updates... ",end="")
            print("all files are up to date.\n")
            self.restart()

    def parse_action(self, thread):
        if not thread:
            print("Invalid entry.")
            self.restart()

        if not self.is_valid_action(thread):
            print("Invalid action entered.")
            self.restart()

        if self.is_link(thread):  # action is a link -> sweep thread
            _res = input("What resolution would you like to sweep for? (E.g 1920x1080) ")
            self._start(thread, _res)
            self.restart()

        if thread == "?":
            print(self.help)
            self.restart()

        if thread == "update" or thread == "Update":
            self.update()
            self.restart()

        if thread == "exit":
            try:
                os.exit() # For error thrown by IDE, vvvv
            except:
                pass  # On linux it tries to throw an error (exit() not found in os.py module) yet it still
                      # returns an exit code of 0. So fuck it, it works.
    def is_link(self, link) -> bool:
        if "boards.4chan.org" in link:
            return True
        else:
            return False

    def is_valid_action(self, action) -> bool:
        if action == "?" or action == "update" or self.is_link(action) or action == "exit" or action == "clear":
            return True
        else:
            return False

    def restart(self):
        run = Run()
        run.main()

class Sweep(object):
    def start(self, thread, _res):
        print(Sweep.get_img_links(self, thread, _res))

    @staticmethod
    def get_img_links(self, thread, _res):

        # File = high, width and file
        board = basc_py4chan.Board('g')
        threadid = board.get_thread(58112557)
        links = []
        zsfile = []
        post = 0
        try:
            for file in threadid.files():
                links.append(file)
                current = File(threadid.posts[post], file)
                post += 1
                print(str(current))
        except Exception as e:
            print(str(e))
            Run.restart(self)

    def start_sweep(self, links):
        pass

    def get_sizes(self, uri):
        pass

class Update(Exception):

    def main(self):

        try:
            print("Updated!\n")
        except OSError as e:
            raise Update("Error: " + str(e))
        except IOError as e:
            raise Update("Error: " + str(e))

    def check_vers(self) -> bool:

        try:
            url = "https://raw.githubusercontent.com/dxrp/image-sweeper/master/vers.txt"
            directory = getcwd()
            filename = directory + '\\vers.txt'
            r = requests.get(url)

            if '0.2' in str(r.content):
                return True  # update is ready
            else:
                return False  # no update
        except Exception as e:
            print("Error obtaining update information. More info:\n" + str(e) + "\n")

class UnknownImageFormat(Exception):
    @property
    def get_image_size(file_path) -> int:
        """
        Return (width, height) for a given img file content - no external
        dependencies except the os and struct modules from core
        """
        size = os.path.getsize(file_path)

        with open(file_path) as input:
            height = -1
            width = -1
            data = input.read(25)

            if (size >= 10) and data[:6] in ('GIF87a', 'GIF89a'):
                # GIFs
                w, h = struct.unpack("<HH", data[6:10])
                width = int(w)
                height = int(h)
            elif ((size >= 24) and data.startswith('\211PNG\r\n\032\n')
                  and (data[12:16] == 'IHDR')):
                # PNGs
                w, h = struct.unpack(">LL", data[16:24])
                width = int(w)
                height = int(h)
            elif (size >= 16) and data.startswith('\211PNG\r\n\032\n'):
                # older PNGs?
                w, h = struct.unpack(">LL", data[8:16])
                width = int(w)
                height = int(h)
            elif (size >= 2) and data.startswith('\377\330'):
                # JPEG
                msg = " raised while trying to decode as JPEG."
                input.seek(0)
                input.read(2)
                b = input.read(1)
                try:
                    while (b and ord(b) != 0xDA):
                        while (ord(b) != 0xFF): b = input.read(1)
                        while (ord(b) == 0xFF): b = input.read(1)
                        if (ord(b) >= 0xC0 and ord(b) <= 0xC3):
                            input.read(3)
                            h, w = struct.unpack(">HH", bytes(input.read(4)))
                            break
                        else:
                            input.read(int(struct.unpack(">H", bytes(input.read(2)))[0]) - 2)
                        b = input.read(1)
                    width = int(w)
                    height = int(h)
                except struct.error:
                    raise UnknownImageFormat("StructError" + msg)
                except ValueError:
                    raise UnknownImageFormat("ValueError" + msg)
                except Exception as e:
                    raise UnknownImageFormat(e.__class__.__name__ + msg)
            else:
                raise UnknownImageFormat(
                    "Sorry, don't know how to get information from this file."
                )
        return int(width, height)

class Res(object):
    _list_of_res = ['1920x1080'
                    '1600x900']

if __name__ == "__main__":
    run = Run()
    run.main()

import logging
import sys
import os
import re
import tomli
import requests


class Metabase:
    def __init__(self):
        with open("config.toml", "rb") as f:
            self.config = tomli.load(f)

        self.logger = logging.getLogger()

        logging.getLogger().setLevel(self.config["loglevel"])
        logging.getLogger().info(self.config)

        if not os.path.isfile("session.txt"):
            self.session_id = self.authenticate()
        else:
            with open("session.txt", "r") as f:
                self.session_id = f.read()

        logging.getLogger().info("Session-ID: " + self.session_id)

    def authenticate(self):
        session_req = requests.post(self.config["url"] + "/api/session",
                                    json={"username": self.config["username"], "password": self.config["password"]})
        if "id" in session_req.json():
            with open("session.txt", "w") as f:
                f.write(session_req.json()["id"])
            return session_req.json()["id"]
        else:
            raise Exception(str(session_req.json()))

    def get(self, path):
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "X-Metabase-Session": self.session_id
        }
        req = requests.get(self.config["url"] + path, headers=headers)
        if req.status_code not in [200]:
            if req.text == "Unauthenticated":
                self.session_id = self.authenticate()
                return self.get(path)
            else:
                raise Exception("Error: " + req.text)

        return req.json()

    def put(self, path, data):
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "X-Metabase-Session": self.session_id
        }
        req = requests.put(self.config["url"] + path, headers=headers, json=data)
        if req.status_code not in [200, 202]:
            raise Exception("Error: " + req.text)

        return req.json()

    def update_from_files(self):
        cards = self.get("/api/card")
        for card in cards:
            if card["dataset_query"]["type"] == "native":
                self.logger.info(f"Found native sql with id: {card['id']} - \"{card['name']}\"")

                # if card['id'] == 97:
                regex = r"--%%mb_snippet_tool:(.*)%%.*--([\S\s]*)--%%mb_snippet_tool_end%%--"

                def replace_with_file(match):
                    filename = match.group(1)
                    # old_snippet = match.group(2)
                    if os.path.isfile(os.path.join("snippets", filename)):
                        with open(os.path.join("snippets", filename)) as f:
                            new_snippet = f.read()
                            replaced = f"--%%mb_snippet_tool:{filename}%% DO NOT EDIT BETWEEN HERE AND " \
                                       f"MB_SNIPPET_TOOL_END!--\n{new_snippet}\n--%%mb_snippet_tool_end%%--"
                            self.logger.info(f"Replaced snippet with \"{filename}\"")
                            return replaced
                if "--%%mb_snippet_tool:" in card["dataset_query"]["native"]["query"]:
                    card["dataset_query"]["native"]["query"] = re.sub(regex, replace_with_file, card["dataset_query"]["native"]["query"])
                    self.put(f"/api/card/{card['id']}", card)


if __name__ == "__main__":
    logger = logging.getLogger()
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)-5.5s: %(message)s", "%Y-%m-%d %H:%M:%S"))
    logger.addHandler(console_handler)

    mb = Metabase()
    mb.update_from_files()
    # input("Press any key to continue...")

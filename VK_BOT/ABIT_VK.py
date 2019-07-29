import vk, time, json, yaml

with open("./yaml/token.yaml", 'r') as stream:
    API_TOKEN = yaml.safe_load(stream)

CHATID_TO_SEND = 54
GROUP_ID = -184403760
API_VERSION = 5.73
OUT_FILE = "./yaml/last_post.yaml"

class vk_class():

    def __init__(self):
        session = vk.Session(access_token=API_TOKEN)
        self.api = vk.API(session)
        self.APIVersion = API_VERSION

        while True:
            self.get_last_post_id()
            self.group_check_posts()
            time.sleep(60)

    def group_check_posts(self):
        results = self.api.wall.get(owner_id=GROUP_ID,v=self.APIVersion)["items"][0]
        if results["date"] != self.post_id:
            self.write_post_to_chat(results)
            self.post_id = results["date"]
            self.set_last_post_id()

    def write_post_to_chat(self, input_json):
        attachment_str = "wall"+str(input_json["from_id"])+"_"+str(input_json["id"])
        self.api.messages.send(chat_id=CHATID_TO_SEND, attachment=attachment_str,v=self.APIVersion)

    def get_last_post_id(self):
        with open(OUT_FILE, 'r') as stream:
            self.post_id = yaml.safe_load(stream)

    def set_last_post_id(self):
        with open(OUT_FILE, 'w') as stream:
            yaml.dump(self.post_id, stream)

if __name__ == '__main__':
    vk_class()
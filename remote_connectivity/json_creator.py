import json



class DopQToJsonConversion():
    def __init__(self, dopq):
        self.dopq = dopq
        self.history = []
        self.write_history_info_json()

    def write_history_info_json(self):
        with open("./remote_connectivity/container_history.json", mode='w', encoding='utf-8') as f:
            json.dump([], f)
        info = []
        for container in self.dopq.history:
            json_string = json.dumps(container.container_stats())
            info.append(json_string)

        with open("./remote_connectivity/container_history.json", mode='w', encoding='utf-8') as feedsjson:
            json.dump(info, feedsjson)


    def write_running_container_json(self):
        for container in self.dopq.running_containers:
            json_string = json.dumps(container.container_stats())
            with open('running_container.json', 'w') as f:
                json.dump(json_string, f)


    def write_enqueued_container_json(self):
        pass

    def write_user_stats_json(self):
        pass

    def write_dopq_status_json(self):
        pass


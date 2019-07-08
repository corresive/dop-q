import Pyro4


class PyroRemoteConnectivity():
    def __init__(self, dopq):
        self.dopq_obj = dopq

    @Pyro4.expose
    def send_info_toclient(self):
        # Add more codes later on

        return self.dopq_obj


def start_server(dopq):
    print("Call in start_server")
    custom_daemon = Pyro4.Daemon(host="localhost", nathost=9090)

    # ------ alternatively, using serveSimple -----
    Pyro4.Daemon.serveSimple(
        {
            PyroRemoteConnectivity: "remote_dopq"
        },
        ns=True, host="localhost", daemon=custom_daemon)

'''
def start_server(dopq):
    print("Inside Start Server ..")
    rmt_conn_obj = PyroRemoteConnectivity(dopq)
    daemon = Pyro4.Daemon()
    name_server = Pyro4.locateNS() # Finding the name server
    uri = daemon.register(rmt_conn_obj)
    name_server.register("server.DopQInfo", uri)

    print("DopQ Server is Running and Ready ..... ")
    daemon.requestLoop()
'''
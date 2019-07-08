import Pyro4
from pyqt_interface.qt_interface import qt_main


#dopq = Pyro4.Proxy("PYRONAME:remote_dopq")
#dopq.start()


def main():
    daemon = Pyro4.Daemon()
    ns = Pyro4.locateNS(host="10.167.183.184")
    server_uri = ns.lookup("remote_dopq")
    print("Server URI is: ", server_uri)
    dopq = Pyro4.Proxy(server_uri)
    #dopq = Pyro4.Proxy("PYRONAME:remote_dopq")
    #qt_interface.qt_main(dopq)
    #dopq.start()
    dopq.remote_conn_test_frm_diff_machine("10.167.183.148")
    qt_main(dopq)
    daemon.requestLoop()


if __name__ == "__main__":
    main()
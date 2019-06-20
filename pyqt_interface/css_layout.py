import os

MAIN_HEADER_HTML = """<font color="#ff0000">Do</font><font color='darkturquoise'>cker</font> 
                    <font color="#ff0000">P</font><font color='darkturquoise'>riority</font>  
                    <font color="#ff0000">Q</font><font color='darkturquoise'>ueue</font>
                    <font color="#2300fe">!</font>"""
USER_STAT_TITLE_HTML = """<span style='color:#000000;'>User Statistics</span>"""
STATUS_TITLE_HTML = """<span style='color:#000000;'>DoPQ Status</span>"""
RUNNING_CONT_TITLE_HTML = """<span style='color:#000000;'>Running Containers</span>"""
ENQUEUED_CONT_TITLE_HTML = """<span style='color:#000000;'>Enqueued Containers</span>"""
HISTORY_TITLE_HTML = """<span style='color:#000000;'>History</span>"""

def dopq_status_widget_richtext_formatting(data):
    html_text = ""
    html_text += "<div style='text-align:left;'> <b>Queue:<b> <span style='color:#00ff00;'> <b>" + data['Queue Status'] \
                 + "... </b></span></div><br>"
    html_text += "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
    html_text += "<span style='color:Yellow;'> <b> Uptime: <b></span> " + data["Queue Uptime"]
    html_text += "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
    html_text += "<span style='color:Yellow'><b>StartTime: </b></span>" + data["Queue Starttime"] + "<br>"
    html_text += "<div style='text-align:left;'> <b>Provider:<b> <span style='color:#00ff00;'> <b>" \
                 + data["Provider Status"] + "...</b></span></div><br>"
    html_text += "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
    html_text += "<span style='color:Yellow;'> <b> Uptime: <b></span>" + data["Provider Uptime"]
    html_text += "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
    html_text += "<span style='color:Yellow'><b>StartTime: </b></span>" + data["Provider Starttime"] + "<br>"

    return html_text


def user_status_widget_richtext_formatting(container):
    html_text = ""
    html_text += "<span style='color:white'><b> User Name:</b> <font color='forestgreen'><b>" + container['user'] + "</b></font></span>"
    html_text += "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
    html_text += "<hr>"
    html_text += "<table>"
    html_text += "<tr>"
    html_text += "<th width='22%'></th>"
    html_text += "<th width='11%'></th>"
    html_text += "<th width='22%'></th>"
    html_text += "<th width='12%'></th>"
    html_text += "<th width='22%'></th>"
    html_text += "<th width='11%'></th>"
    html_text += "</tr>"

    html_text += "<tr>"
    html_text += "<td> <p align='right'> <font color='red'>Penalty: </td>"
    html_text += "<td> <p align='left'> <b>" + str(container['penalty']) + "</b></td>"
    html_text += "<td> <p align='right'> <font color='Yellow'> Containers Run: </font></td>"
    html_text += "<td> <p align='left'><b>" + str(container['containers run']) + "</b></td>"
    html_text += "<td> <p align='right'> <font color='Yellow'> Containers Enqueued: </font></td>"
    html_text += "<td> <p align='left'><b>" + str(container['containers enqueued']) + "</b></td>"
    html_text += "</tr>"
    html_text += "</table>"

    return html_text


def running_containers_richtext_formatting(container, cnt):
    html_text = ""
    html_text += "<span style='color:#ff0000;'><b> Container No.: " + str(cnt) + "</b></span>"
    html_text += "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
    html_text += "Container Name: <span style='color:salmon;'><b>" + container["name"] + "</b></span>"
    html_text += "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
    html_text += "Container Status: <span style='color:red;'><b>" + container["status"] + "</b></span>"
    html_text += "<hr>"
    html_text += "<table>"
    html_text += "<tr>"
    html_text += "<th width='25%'></th>"
    html_text += "<th width='20%'></th>"
    html_text += "<th width='25%'></th>"
    html_text += "<th width='25%'></th>"
    html_text += "</tr>"

    html_text += "<tr>"
    html_text += "<td> <p align='right'> Docker Name: </td>"

    if container['docker name'] == "":
        html_text += "<td> <p align='left'> <font color='darkcyan' size='2'><b>Not Assigned</b></font></td>"
    else:
        html_text += "<td> <p align='left'> <font color='green'><b>" + container['docker name'] + "</b></font></td>"

    html_text += "<td> <p align='right'> Executor: </td>"
    html_text += "<td> <p align='left'> <font color='Yellow'><b>" + container['executor'] + "</b></font></td>"
    html_text += "</tr>"

    html_text += "<tr>"
    html_text += "<td> <p align='right'> Uptime: </td>"
    if container['run_time']== "":
        html_text += "<td> <p align='left'> <font color='darkcyan' size='2'> <b>Not Yet Started</b></font></td>"
    else:
        html_text += "<td> <p align='left'> <font color='Yellow'><b>" + container['run_time'] + "</b></font></td>"

    html_text += "<td> <p align='right'> Created: </td>"
    if container['created']== "":
        html_text += "<td> <p align='left'> <font color='darkcyan' size='2'><b>Not Yet Created</b></font></td>"
    else:
        html_text += "<td> <p align='left'> <font color='Yellow'> <b>" + container['created'] + "</b></font></td>"
    html_text += "</tr>"

    html_text += "<tr>"
    html_text += "<td> <p align='right'> CPU Usage: </td>"
    if container['cpu'] is None:
        html_text += "<td> <p align='left'> <font color='darkcyan' size='2'> <b>None</b></font></td>"
    else:
        html_text += "<td> <p align='left'> <font color='Yellow'><b>" + container['cpu'] + "</b></font></td>"

    html_text += "<td> <p align='right'> Memory Usage: </td>"
    if container['memory'] is None:
        html_text += "<td> <p align='left'> <font color='darkcyan' size='2'><b>None</b></font></td>"
    else:
        html_text += "<td> <p align='left'> <font color='Yellow'> <b>" + container['memory'] + "</b></font></td>"
    html_text += "</tr>"


    html_text += "<tr>"
    html_text += "<td> <p align='right'> GPU Minor: </td>"
    if str(container['id'][0]) is None:
        html_text += "<td> <p align='left'> <font color='darkcyan'> <b>None</b></font></td>"
    else:
        html_text += "<td> <p align='left'> <font color='Yellow'><b>" + str(container['id'][0]) + "</b></font></td>"

    html_text += "<td> <p align='right'> GPU Usage: </td>"
    if container['usage']== "":
        html_text += "<td> <p align='left'> <font color='darkcyan' size='2'><b>None</b></font></td>"
    else:
        html_text += "<td> <p align='left'> <font color='Yellow'> <b>" + container['usage'] + "</b></font></td>"
    html_text += "</tr>"

    html_text += "</table>"

    return html_text


def enqueued_containers_richtext_formatting(container, cnt):
    html_text = ""
    html_text += "<span style='color:#ff0000;'><b> Container No.: " + str(cnt) + "</b></span>"
    html_text += "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
    html_text += "Container Name: <span style='color:#00ff00;'><b>" + container["name"] + "</b></span>"
    html_text += "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
    html_text += "Container Status: <span style='color:#00ff00;'><b>" + container["status"] + "</b></span>"
    html_text += "<hr>"
    html_text += "<table>"
    html_text += "<tr>"
    html_text += "<th width='25%'></th>"
    html_text += "<th width='20%'></th>"
    html_text += "<th width='25%'></th>"
    html_text += "<th width='25%'></th>"
    html_text += "</tr>"

    html_text += "<tr>"
    html_text += "<td> <p align='right'> Docker Name: </td>"

    if container['docker name'] == "":
        html_text += "<td> <p align='left'> <font color='darkcyan' size='2'><b>Not Assigned</b></font></td>"
    else:
        html_text += "<td> <p align='left'> <font color='green'><b>" + container['docker name'] + "</b></font></td>"

    html_text += "<td> <p align='right'> Executor: </td>"
    html_text += "<td> <p align='left'> <font color='Yellow'><b>" + container['executor'] + "</b></font></td>"
    html_text += "</tr>"
    html_text += "<tr>"
    html_text += "<td> <p align='right'> Uptime: </td>"

    if container['run_time']== "":
        html_text += "<td> <p align='left'> <font color='darkcyan' size='2'> <b>Not Yet Started</b></font></td>"
    else:
        html_text += "<td> <p align='left'> <font color='Yellow'><b>" + container['run_time'] + "</b></font></td>"

    html_text += "<td> <p align='right'> Created: </td>"

    if container['created']== "":
        html_text += "<td> <p align='left'> <font color='darkcyan' size='2'><b>Not Yet Created</b></font></td>"
    else:
        html_text += "<td> <p align='left'> <font color='Yellow'> <b>" + container['created'] + "</b></font></td>"

    html_text += "</tr>"
    html_text += "</table>"

    return html_text


main_window_layout = """
            QWidget{
                background-color: rgb(41, 55, 73);
                margin:2px;
            }
            """

userstats_title_bar = """
            QLabel{
                color: rgb(0, 0, 0);
                background: qradialgradient(cx:0, cy:0, radius: 1, fx:0.5, fy:0.5, stop:0 rgb(25, 102, 255), stop:1 rgb(220,20,60));
                border-radius: 5px;
                border-width: 2px;
                border-style: solid;
                border-color: black;
            }
            """

status_title_bar = """
            QLabel{
                color: rgb(0, 0, 0);
                background: qradialgradient(cx:0, cy:0, radius: 1, fx:0.5, fy:0.5, stop:0 rgb(25, 102, 255), stop:1 rgb(178,34,34));
                border-radius: 5px;
                border-width: 2px;
                border-style: solid;
                border-color: black;
            }
            """

running_cont_title_bar = """
            QLabel{
                color: rgb(0, 0, 0);
                background: qradialgradient(cx:0, cy:0, radius: 1, fx:0.5, fy:0.5, stop:0 rgb(128, 255, 128), stop:1 rgb(128, 0, 255));
                border-radius: 5px;
                border-width: 2px;
                border-style: solid;
                border-color: black;
            }
            """

enqueued_cont_title_bar = """
            QLabel{
                color: rgb(0, 0, 0);
                background: qradialgradient(cx:0, cy:0, radius: 1, fx:0.5, fy:0.5, stop:0 rgb(25, 102, 255), stop:1 rgb(25, 255, 102));
                border-radius: 5px;
                border-width: 2px;
                border-style: solid;
                border-color: black;
            }
            """

history_title_bar = """
            QLabel{
                color: rgb(0, 0, 0);
                background: qradialgradient(cx:0, cy:0, radius: 1, fx:0.5, fy:0.5, stop:0 rgb(255, 25, 255), stop:1 rgb(68, 0, 204));
                border-radius: 5px;
                border-width: 2px;
                border-style: solid;
                border-color: black;
            }
            """


dockwidget_layout = """
            QWidget{
                color: rgb(250,250,210);
                font: Times New Roman;
                font-size: 11pt;
                background-color: rgba(0,41,59,255);
                border-radius: 10px;
                border-width: 3px;
                border-color: rgb(75, 75, 75);
                border-style: solid;
            }
            """

# Layout for the Main Window Header section

dockwidget_main_header_layout = """
            QWidget{
                color: rgb(250,250,210);
                background: qradialgradient(cx:0, cy:0, radius: 1, fx:0.5, fy:0.5, stop:0 rgb(75,0,130), stop:1  rgb(0,191,255));
                border-radius: 10px;
                border-width: 3px;
                border-color: rgb(75, 75, 75);
                border-style: solid;
            }
            """

main_header_label_layout = """
            QLabel{
                color: rgb(0, 0,210);
                font: Times New Roman;
                font-size: 13pt;
                font-weight: bold;
                border-radius: 10px;
                border-width: 3px;
                border-color: rgb(75, 75, 75);
                border-style: solid;
            }
            """


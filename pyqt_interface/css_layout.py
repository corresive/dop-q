import os

dockwidget_title_bar = """
            QLabel{
                color: rgb(0, 0, 0);
                font: Times New Roman;
                font-family: New Century Schoolbook;
                font-size: 12pt;
                font-weight: bold;
                background: qradialgradient(cx:0, cy:0, radius: 1,
              fx:0.5, fy:0.5, stop:0 red, stop:1 rgb(50,205,50));
                border-radius: 5px;
                border-width: 2px;
                border-style: solid;
                border-color: black;
                text-align: right;
            }
            """

dockwidget_layout = """
            QWidget{
                color: rgb(250,250,210);
                font: Times New Roman;
                font-size: 11pt;
                background-color: rgb(0, 11, 0);
                border-radius: 10px;
                border-width: 3px;
                border-color: rgb(75, 75, 75);
                border-style: solid;
            }
            """
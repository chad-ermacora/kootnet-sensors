import os
from datetime import datetime
from flask import Blueprint, render_template, request, send_file
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_generic_functions
from http_server.server_http_auth import auth
from http_server.server_http_generic_functions import message_and_return
from http_server import server_plotly_graph
from http_server import server_plotly_graph_variables

html_plotly_graphing_routes = Blueprint("html_plotly_graphing_routes", __name__)


@html_plotly_graphing_routes.route("/PlotlyGraph")
def html_plotly_graphing():
    logger.network_logger.debug("* Plotly Graph viewed by " + str(request.remote_addr))
    generating_message = "Generating Plotly Graph. This may take awhile."
    generating_message2 = "Once the graph is complete, you will automatically be returned to the Graphing page."
    save_to_folder = file_locations.plotly_save_folder

    if server_plotly_graph.server_plotly_graph_variables.graph_creation_in_progress:
        logger.primary_logger.debug("Plotly Graph is currently being generated, please wait...")
        return message_and_return(generating_message, text_message2=generating_message2, url="/PlotlyGraph")

    try:
        plotly_filename_interval = file_locations.plotly_filename_interval
        unix_creation_date = os.path.getmtime(save_to_folder + plotly_filename_interval)
        interval_creation_date = str(datetime.fromtimestamp(unix_creation_date))[:-7]
    except FileNotFoundError:
        interval_creation_date = "No Plotly Graph Found"

    try:
        plotly_filename_triggers = file_locations.plotly_filename_triggers
        triggers_plotly_file_creation_date_unix = os.path.getmtime(save_to_folder + plotly_filename_triggers)
        triggers_creation_date = str(datetime.fromtimestamp(triggers_plotly_file_creation_date_unix))[:-7]
    except FileNotFoundError:
        triggers_creation_date = "No Plotly Graph Found"

    return render_template("plotly_graph.html",
                           IntervalPlotlyDate=interval_creation_date,
                           TriggerPlotlyDate=triggers_creation_date)


@html_plotly_graphing_routes.route("/CreatePlotlyGraph", methods=["POST"])
@auth.login_required
def html_create_plotly_graph():
    generating_message = "Generating Plotly Graph. This may take awhile."
    generating_message2 = "Once the graph is complete, you will automatically be returned to the Graphing page."

    if server_plotly_graph.server_plotly_graph_variables.graph_creation_in_progress:
        logger.primary_logger.debug("Plotly Graph is currently being generated, please wait...")
        return message_and_return(generating_message, text_message2=generating_message2, url="/PlotlyGraph")
    elif request.method == "POST" and "SQLRecordingType" in request.form:
        logger.network_logger.info("* Plotly Graph Initiated by " + str(request.remote_addr))
        try:
            new_graph_data = server_plotly_graph_variables.CreateGraphData()
            new_graph_data.graph_table = request.form.get("SQLRecordingType")

            if request.form.get("PlotlyRenderType") == "OpenGL":
                new_graph_data.enable_plotly_webgl = True
            else:
                new_graph_data.enable_plotly_webgl = False

            # The format the received datetime should look like "2019-01-01 00:00:00"
            new_graph_data.graph_start = request.form.get("graph_datetime_start").replace("T", " ") + ":00"
            new_graph_data.graph_end = request.form.get("graph_datetime_end").replace("T", " ") + ":00"
            new_graph_data.datetime_offset = request.form.get("HourOffset")
            new_graph_data.sql_queries_skip = int(request.form.get("SkipSQL").strip())
            new_graph_data.graph_columns = server_plotly_graph.check_form_columns(request.form)

            if len(new_graph_data.graph_columns) < 4:
                return message_and_return("Please Select at least One Sensor", url="/PlotlyGraph")
            else:
                app_generic_functions.thread_function(server_plotly_graph.create_plotly_graph, args=new_graph_data)
        except Exception as error:
            logger.primary_logger.warning("Plotly Graph: " + str(error))
        return message_and_return(generating_message, text_message2=generating_message2, url="/PlotlyGraph")
    return html_plotly_graphing()


@html_plotly_graphing_routes.route("/ViewIntervalPlotlyGraph")
def html_view_interval_graph_plotly():
    logger.network_logger.info("* Interval Plotly Graph Viewed from " + str(request.remote_addr))
    if os.path.isfile(file_locations.plotly_save_folder + file_locations.plotly_filename_interval):
        return send_file(file_locations.plotly_save_folder + file_locations.plotly_filename_interval)
    else:
        message_title = "No Interval Plotly Graph Generated - Click to Close Tab"
        return message_and_return(message_title, special_command="JavaScript:window.close()", url="")


@html_plotly_graphing_routes.route("/ViewTriggerPlotlyGraph")
def html_view_triggers_graph_plotly():
    logger.network_logger.info("* Triggers Plotly Graph Viewed from " + str(request.remote_addr))
    if os.path.isfile(file_locations.plotly_save_folder + file_locations.plotly_filename_triggers):
        return send_file(file_locations.plotly_save_folder + file_locations.plotly_filename_triggers)
    else:
        message1 = "No Triggers Plotly Graph Generated - Click to Close Tab"
        special_command = "JavaScript:window.close()"
        return message_and_return(message1, special_command=special_command, url="")

import logging
import os
from threading import Thread

from gridappsd import GridAPPSD
from gridappsd.topics import simulation_output_topic, service_output_topic
from sensors import Sensors

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)-15s %(process)d %(module)-10s %(message)s")

sim_request = {"power_system_config": {
    "GeographicalRegion_name": "_73C512BD-7249-4F50-50DA-D93849B89C43",
    "SubGeographicalRegion_name": "_A1170111-942A-6ABD-D325-C64886DC4D7D",
    "Line_name": "_AAE94E4A-2465-6F5E-37B1-3E72183A4E44"
},
    "application_config": {"applications": []},
    "simulation_config": {"start_time": "1628531887", "duration": "900", "simulator": "GridLAB-D",
                          "timestep_frequency": "1000", "timestep_increment": "1000", "run_realtime": True,
                          "simulation_name": "final9500node", "power_flow_solver_method": "NR",
                          "model_creation_config": {"load_scaling_factor": "1",
                                                    "schedule_name": "ieeezipload", "z_fraction": "0",
                                                    "i_fraction": "1", "p_fraction": "0",
                                                    "randomize_zipload_fractions": False,
                                                    "use_houses": False}},
    "test_config": {"events": [], "appId": ""}, "service_configs": [{"id": "gridappsd-sensor-simulator",
                                                                     "user_options": {
                                                                         "default-perunit-confidence-band": 0.02,
                                                                         "simulate-all": True,
                                                                         "default-normal-value": 100,
                                                                         "random-seed": 150,
                                                                         "default-aggregation-interval": 6,
                                                                         "passthrough-if-not-specified": False,
                                                                         "default-perunit-drop-rate": 0.00,
                                                                         "randomize-sensor-offset": False
                                                                         #,
                                                                         #"sensors-config": {
                                                                         #    "_b68f03f8-372e-41cd-87cd-1f7580e9669e": {}
                                                                         #}
                                                                     }}]}

simulation_id = 1000


def run_sensor_service():
    feeder = sim_request["power_system_config"]["Line_name"]
    service_id = "gridappsd-sensor-simulator"
    user_options = sim_request["service_configs"][0]["user_options"]

    gapp = GridAPPSD(username="system",
                     password="manager",
                     stomp_port=61613,
                     stomp_address="gridappsd")

    # gapp.get_logger().setLevel(opts.log_level)
    read_topic = simulation_output_topic(simulation_id)
    write_topic = service_output_topic(service_id, simulation_id)

    log_file = "/tmp/gridappsd_tmp/{}/sensors.log".format(simulation_id)
    if not os.path.exists(os.path.dirname(log_file)):
        os.makedirs(os.path.dirname(log_file))

    import sys
    from pprint import pprint
    from sensors.measurements import Measurements

    meas = Measurements()
    meta = meas.get_sensors_meta(feeder)

    with open(log_file, 'w') as fp:
        logging.basicConfig(stream=fp, level=logging.INFO)
        logging.getLogger().info("Almost ready to create sensors!")
        logging.getLogger().info(f"read topic: {read_topic}\nwrite topic: {write_topic}")
        logging.getLogger().info(f"user options: {user_options}")
        logging.getLogger().debug(f"Meta: {meta}")
        run_sensors = Sensors(gapp, read_topic=read_topic, write_topic=write_topic,
                              user_options=user_options, measurements=meta)
        run_sensors.main_loop()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    os.environ['GRIDAPPSD_APPLICATION_ID'] = 'gridappsd-sensor-simulator'
    os.environ['GRIDAPPSD_APPLICATION_STATUS'] = 'STARTED'
    os.environ['GRIDAPPSD_SIMULATION_ID'] = str(simulation_id)
    os.environ['GRIDAPPSD_USER'] = 'system'
    os.environ['GRIDAPPSD_PASSWORD'] = 'manager'

    t = Thread(target=run_sensor_service)

    t.run()

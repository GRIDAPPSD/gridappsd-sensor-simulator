import logging
import time

from gridappsd import GridAPPSD
from gridappsd.docker_handler import run_gridappsd_container, run_dependency_containers, Containers

logging.basicConfig(level=logging.DEBUG)

_log = logging.getLogger(__name__)
Containers.reset_all_containers(ignore_list=["mysql", "proven", "influxdb", "redis", "blazegraph", "mysql",
                                             "gridappsd_dev"])

with run_dependency_containers(stop_after=False):
    with run_gridappsd_container(stop_after=False):
        goss = GridAPPSD()
        goss.connect()
        assert goss.connected
        goss.disconnect()

_log.debug("After with statements!")
_log.debug(f"Containers are {Containers.container_list()}")


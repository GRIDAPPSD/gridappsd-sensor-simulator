import logging
import time

from gridappsd import GridAPPSD
from gridappsd.docker_handler import run_gridappsd_container, run_dependency_containers, Containers

logging.basicConfig(level=logging.DEBUG)

_log = logging.getLogger(__name__)
Containers.reset_all_containers(ignore_list=["gridappsd_dev"])
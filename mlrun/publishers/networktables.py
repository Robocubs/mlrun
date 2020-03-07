"""NetworkTables publisher for MLRun."""
import logging
import sys
from abc import ABC

from mlrun import strings, loader
from mlrun.loader import ComponentType
from mlrun.config import configurations
from mlrun.publishers.base import BasePublisher

from _pynetworktables import NetworkTable
from _pynetworktables._impl.structs import ConnectionInfo

NetworkTables = None


class NetworkTablesPublisher(BasePublisher, ABC):
    """Allows for publishing values to NetworkTables."""
    def __init__(self, team: int = 1701, table: str = "SmartDashboard", prefix: str = "jetson", *args, **kwargs):
        """
        Initialize NetworkTables parameters.
        Args:
            team: Team number for resolving NetworkTables server.
            table: Table name to push values to.
            prefix: Prefix for each key pushed to NetworkTables.
        """
        super().__init__(*args, **kwargs)
        self.connected = False
        self.team = team
        self.table_name = table
        self.prefix = prefix
        self.table = None
        self.logger = loader.load_component(
            ComponentType.LOGGER,
            configurations["desktop"]["logger"]["name"]
        )(
            logger=logging.getLogger("nt"),
            max_level="DEBUG"
        )

    def enable(self) -> NetworkTable:
        """
        Enable the NetworkTables client.
        Returns:
            A NetworkTable instance which can be freely called.
        """
        global NetworkTables
        self.logger.info(strings.networktables_loading)
        try:
            from networktables import NetworkTables
            self.logger.info(strings.networktables_successful)
        except ImportError:
            self.logger.error(strings.networktables_unsuccessful)
            sys.exit(1)
        NetworkTables.addConnectionListener(self._connection_listener, True)
        NetworkTables.initialize(server=f"roborio-{self.team}-frc.local")
        self.table: NetworkTable = NetworkTables.getTable(self.table_name)
        return self.table

    def disable(self):
        """
        Disable the NetworkTables client.
        Returns:
            Nothing.
        """
        global NetworkTables
        self.logger.info(strings.networktables_unloading)
        NetworkTables.removeConnectionListener(self._connection_listener)
        NetworkTables.shutdown()
        self.logger.info(strings.networktables_unloaded)

    def is_connected(self) -> bool:
        """Whether or not there is a connection."""
        return self.connected

    def _connection_listener(self, status: bool, connection: ConnectionInfo):
        if status:
            self.logger.info(strings.networktables_connection_established.format(
                ip=connection.remote_ip,
                port=connection.remote_port,
                ver=connection.protocol_version
            ))
            self.connected = True
        else:
            self.logger.warning(strings.networktables_connection_lost)
            self.connected = False

from __future__ import annotations
from myunfi.client.base import MyUNFIClientProtocol


class APIEndpointRequestable:
    """
    Base class for all API endpoints that can be requested.
    """

    def __init__(self, client: MyUNFIClientProtocol = None, session=None, account_id=None, dc=None):
        """
        Initialize the APIEndpointRequestable object.

        :param client: The API object.
        """
        self.account_id = account_id
        self.dc = dc
        assert session is not None and client is None or client is not None and session is None
        if session:
            self.session = session
        else:
            self.session = client.session



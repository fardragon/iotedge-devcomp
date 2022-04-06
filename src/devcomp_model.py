from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import List, Optional
import datetime

from auth_record import AuthRecord

from azure.identity import TokenCachePersistenceOptions, InteractiveBrowserCredential
from azure.mgmt.resource import SubscriptionClient, ResourceManagementClient
from azure.mgmt.iothub import IotHubClient
from azure.iot.hub import IoTHubRegistryManager, IoTHubConfigurationManager

@dataclass
class Subscription:
    name: str
    id: str


class AbstractModel(ABC):
    @abstractmethod
    def authorize(self, authorization_callback: Callable[[str, str, datetime], None]):
        pass

    @abstractmethod
    def get_all_subscriptions(self) -> List[Subscription]:
        pass

    @abstractmethod
    def set_subscription(self, subscription: str) -> None:
        pass

    @abstractmethod
    def get_all_resource_groups(self, subscription_id: str) -> List[str]:
        pass

    @abstractmethod
    def set_resource_group(self, resource_group: str) -> None:
        pass

    @abstractmethod
    def get_all_iothubs(self) -> List[str]:
        pass

    @abstractmethod
    def set_iothub(self, iothub: str) -> None:
        pass

    @abstractmethod
    def get_iothub_edge_devices(self) -> List[str]:
        pass


class AzureModel(AbstractModel):
    def __init__(self):
        super(AzureModel, self).__init__()

        self.credential = InteractiveBrowserCredential(cache_persistence_options=TokenCachePersistenceOptions(),
                                                       timeout=30,
                                                       authentication_record=AuthRecord.get())
        self.subscription: Optional[str] = None
        self.resource_group: Optional[str] = None
        self.iothub: Optional[str] = None

        self.resource_client: Optional[ResourceManagementClient] = None
        self.iothub_mgmt_client: Optional[IotHubClient] = None
        self.iothub_registry_client: Optional[IoTHubRegistryManager] = None

    def authorize(self, authorization_callback: Callable[[str, str, datetime], None]):
        self.credential._prompt_callback = authorization_callback
        record = self.credential.authenticate()
        AuthRecord.save(record)

    def get_all_subscriptions(self) -> List[Subscription]:
        client = SubscriptionClient(credential=self.credential)
        subscriptions = client.subscriptions.list()
        return [Subscription(sub.display_name, sub.subscription_id) for sub in subscriptions]

    def set_subscription(self, subscription: str) -> None:
        self.subscription = subscription

        self.iothub_mgmt_client = IotHubClient(credential=self.credential, subscription_id=self.subscription)
        self.resource_client = ResourceManagementClient(self.credential, subscription)

    def get_all_resource_groups(self, subscription_id: str) -> List[str]:
        groups = self.resource_client.resource_groups.list()
        return [group.name for group in groups]

    def set_resource_group(self, resource_group: str) -> None:
        self.resource_group = resource_group

    def get_all_iothubs(self) -> List[str]:
        iothubs = self.resource_client.resources.list_by_resource_group(
            self.resource_group, filter="resourceType eq 'Microsoft.Devices/IotHubs'")
        return [iothub.name for iothub in iothubs]

    def set_iothub(self, iothub: str) -> None:
        self.iothub = iothub
        self.iothub_registry_client = IoTHubRegistryManager.from_connection_string(self.__retrieve_connection_string())

    def get_iothub_edge_devices(self) -> List[str]:
        return [device for device in self.__colect_edge_devices() if
                self.iothub_registry_client.get_device(device).capabilities.iot_edge]

    def __retrieve_connection_string(self) -> str:
        keys = self.iothub_mgmt_client.iot_hub_resource.list_keys(self.resource_group, self.iothub)

        primary_key = None
        for key in keys:
            if key.key_name == 'iothubowner':
                primary_key = key.primary_key
                break

        assert primary_key is not None, "failed to retrieve primary key"
        return 'HostName={}.azure-devices.net;SharedAccessKeyName={};SharedAccessKey={}'.format(self.iothub,
                                                                                                'iothubowner',
                                                                                                primary_key)

    def __colect_edge_devices(self) -> List[str]:
        return [device.device_id for device in self.iothub_registry_client.get_devices()]

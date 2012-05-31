import ANRV.System.Registry as Registry
from ANRV.System.RPCComponent import RPCComponent

class RegistryComponent(RPCComponent):
    def rpc_createComponent(self, newcomponentname: [str, 'Name of new component template']):
        """Creates a new component and registers it with a dispatcher."""
        if "Dispatcher" in Registry.Components:
            if newcomponentname in Registry.ComponentTemplates:
                # TODO: Better addressing without too much added trouble
                # TODO: Initialize parameters correctly (How?)
                newcomponent = Registry.ComponentTemplates[newcomponentname][0]()

                Registry.Components[newcomponentname] = newcomponent

                Dispatcher = Registry.Components["Dispatcher"]
                Dispatcher.RegisterComponent(newcomponent)
                return True
            else:
                return (False, "Component not found in templates. You might want to check its installation.")
        else:
            return (False, "No Dispatcher found to register component.")

    def rpc_listRegisteredComponents(self):
        return Registry.Components

    def rpc_listRegisteredTemplates(self):
        return Registry.ComponentTemplates

    # TODO:
    # * Destruction of components

Registry.ComponentTemplates['RegistryComponent'] = [RegistryComponent, "Registry Component"]

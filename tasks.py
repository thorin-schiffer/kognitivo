import json
import os

from invoke import Collection

from invoke_collections import android_collection
from invoke_collections import kivy_collection
from invoke_collections import kognitivo as kognitivo_invoke

os.environ['INVOKE'] = "TRUE"

configuration = {
    "sdk": None,
    "genymotion_path": None,
    "genymotion_device_id": None,
    "keystore": os.path.join(os.getcwd(), "release", "kognitivo.keystore"),
    "keystore_alias": "eviltnan",
    "keystore_password": None
}

if os.path.exists("invoke.json"):
    with open("invoke.json") as f:
        configuration.update(json.load(f))

configuration['adb'] = os.path.join(configuration['sdk'], "platform-tools", "adb")
configuration['sdk_manager'] = os.path.join(configuration['sdk'], "tools", "android")

ns = Collection()

ns.add_collection(Collection.from_module(kivy_collection, name='kivy'))
ns.add_collection(Collection.from_module(android_collection, name='android'))
ns.add_collection(Collection.from_module(kognitivo_invoke))
ns.configure(configuration)

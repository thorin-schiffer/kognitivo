# Kivy based brain trainer

This repository is there for demonstration purposes mainly. 
You could possibly experience some weird issues while getting it 
running on your platform. Star and fork the repository if you want to say thank you.

Download the app on google play:

[<img src="http://steverichey.github.io/google-play-badge-svg/img/en_get.svg" width="256">](https://play.google.com/store/apps/details?id=org.kognitivo.kognitivo)

## Installation

Install [kivy](https://kivy.org/docs/gettingstarted/installation.html). 
Install audio and video deps too. 

### Virtualenv

Create using the system site packages. 

Virtualenvwrapper: `mkvirtualenv --system-site-packages kognitivo`

### Python dependencies

`pip install -r requirements.txt`

### Create static files

* create atlas: `inv kivy.atlas`
* update translation files: `inv kivy.po`
* create translation files: `inv kivy.mo`

### Development

* fill the database with fake data: `inv kognitivo.db`
* test with: `KIVY_UNITTEST=true pytest`. 
Use pytest xdist in order to start in multiprocess mode: `KIVY_UNITTEST=true pytest -n 4`.
Use keyword `<lang_code>_lang` to execute the tests for a certain language only: 
`KIVY_UNITTEST=true pytest -n 4 -k en_lang`.

## Packaging for android
Make sure you've gone all steps in [kivy packing guide](https://kivy.org/docs/guide/packaging-android.html)

### Install and setup buildozer
Buildozer is python android packaging tool. 
Because of python for android won't work inside the [virtualenv](http://python-for-android.readthedocs.io/en/latest/old_toolchain/faq/#too-many-levels-of-symbolic-links)
it must be installed within global python env.
Make sure you go through [installation instructions](https://buildozer.readthedocs.io/en/latest/installation.html) 

* Install buildozer globally `sudo pip install buildozer==0.33`. Make sure you are not in the virtualenv.
* Install android SDK and NDK with `buildozer android update`. This may take a while. Make sure you are not in the virtualenv.
* Locate location of SDK. Normally at `$HOME/.buildozer/android/platform/android-sdk-<sdk_version>`
* Set sdk path in `invoke.json` inplace of <SET_SDK_PATH>. Verify with `inv android.manager` which starts sdk manager GUI.

### Packaging
#### Packaging in DEBUG mode

* Execute `inv android.debug --no-deploy`. This one is a wrapper around `buildozer debug` with a custom patching of the
android project usually located at `<YOUR_PROJECT_DIR>/.buildozer/android/platform/build/dists/kognitivo`.
* APK built in DEBUG mode will be placed in `bin/` directory named like `Kognitivo-<version>-debug.apk` 

#### Packaging in RELEASE mode
The following instructions are there for you as example of how you could release-ready package your own app.  
Of course you can be a total jerk and just upload the copy of kognitivo into Google Play, it's your choice.

* First you'd need to have a keystore. This is a nice and short 
[write up](https://coderwall.com/p/r09hoq/android-generate-release-debug-keystores)
* Place it in `release/kognitivo.keystore`
* Set your keystore password inplace of `<SET_KEYSTORE_PASSWORD>` in your `invoke.json`. 
* Execute `inv android.release --no-deploy`. It's not much different from the bare `buildozer android release`, only
android project files patching.

## Setup emulator

### Using android emulator

* Start manager GUI with: `inv android.manager`
* Install ARM EABI image: Android 5.1.1 -> ARM EABI v7a System Image 
* Start emulators manager with: `inv android.avd-manager`
* Create a device, pick just created ARM EABI system image, set GPU acceleration, set VM Heap size min to 512 MB
* Note that the emulator performance is way worse, than on the real device, so it takes very long for the app to start
 
### Using Genymotion
**Not recommended didn't work for me**: Genymotion uses Virtual Box x86 based images, new p4a toolchain
seems to have massive problems with x86

Genymotion is a powerful android emulator free for personal use. Genymotion uses virtualbox, so make sure 
you've done [installation guide](https://docs.genymotion.com/Content/01_Get_Started/Installation.htm)

* Download [genymotion](https://www.genymotion.com/download/) installation binary
* Move the binary downloaded to a directory you want genymotion to live
* Make the binary executable with chmod +x, execute it
* Copy invoke.json.template to invoke.json (will be ignored), set genymotion path inplace of `<SET_GENYMOTION_PATH>`
* Verify genymotion path is found with `inv android.check-genymotion`, it should show: `Player found`
* Start genymotion from your OS GUI or from command line with `<genymotion>/genymotion`. Go through the wizard and
install a device you wish. Let's say it will be Google Pixel with Android 7.0. Could find gapps for 7.1, see below.
* Set the android sdk path to the one from kivy from genymotion GUI(Settings->ADB->Use custom Android SDK tools) to
your sdk path. We've just found it recently and put in `invoke.json`
* Download [ARM translation ZIP](https://yadi.sk/d/kYkDyIznkGvym), drag-and-drop it inside the emulator's window,
wait a while, click yes and yes.
* todo: Install [gapps](http://opengapps.org/) fitting your device

### Starting the emulator

* Run `VBoxManage list vms`, find the device id in the list of installed virtual boxes. It's the on in curly braces 
like `{c5ed9f35-38df-4ded-b533-8348a0f3bff8}`
* Put the device_id in `invoke.json` inplace of `<SET_GENYMOTION_DEVICE_ID>`
* Start the specified emulator with: `inv android.genymotion`.

## Install and run in emulator

* install debug version in the emulator with `inv android.install --debug`. It would use a debug apk with the biggest
version in `/bin` directory.

* usually while development you'd want to do package and run your app, you can do so by dropping 
`no-deploy` option: `inv android.debug`. This would start an emulator, install the apk and run the app. You can also 
add `--logcat` option in order to see the logs in your command line. Stop with Ctrl+C


# Troubleshooting

 * `ImportError: Cython.Distutils` -> install cython `apt install cython`
 * GL headers missing, install mesa headers: `apt install libgl1-mesa-dev`
 * ```pkg_resources.VersionConflict: (pytest 2.8.7 (/usr/lib/python2.7/dist-packages), Requirement.parse('pytest>=3.0.0'))``` 
 -> you have pytest installed globally, remove it and reinstall pytest in the virtualenv
 * Buildozer complains about missing java compiler ```Java compiler (javac) not found, please install it.```. 
 -> Install missing jdk. For openjdk and java 8: `sudo apt install openjdk-8-jdk`
 * Sometimes logger buildozer or p4a would fail with messages containing some random unicode letters. Know it's because
 your system locale is not english
 * `Failure [INSTALL_FAILED_NO_MATCHING_ABIS: Failed to extract native libraries, res=-113]` while installing the app 
 inside the emulator -> caused by the fact that genymotion emulators are based on the x86 architecture, you've probably
 forgotten to install ARM translation
 * first run of `inv android.debug` could possibly fail with missing string ids (app_id and facebook_app_id).
 Just rerun the the commands. This is happening because patching fails if there is no project directory yet.
 * `cannot create GLES surface` -> emulator doesn't have `use host GPU` checkbox


# Contribution

If you are still willing to contribute, just make a PR, run the tests and `flake8` on your branch. I'll take a look :D

# License
Apache 2.0
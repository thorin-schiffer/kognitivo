import multiprocessing
import os
from time import sleep
import re

from invoke import task
from invoke_collections import kivy_collection

from invoke_collections.utils import tprint, fprint, iprint


@task
def check_genymotion(ctx):
    """
    Checks if genymotion was installed properly
    """
    genymotion_path = ctx.get('genymotion_path')
    if not genymotion_path:
        raise RuntimeError("Genymotion path is not set. Set 'genymotion_path' in invoke.json")
    if os.path.exists(genymotion_path):
        print "Genymotion path exists. Good... Checking player..."
        if os.path.exists(os.path.join(genymotion_path, 'player')):
            print "Player found."
        else:
            fprint("Genymotion path does not contain player binary and seems not to be genymotion installation")
    else:
        fprint("Genymotion path does not exist. Set correct one in invoke.json")


@task
def projects_build(ctx):
    """
    Build third party android projects like google play services and facebook SDK
    """
    tprint("Building google play services project...")
    ctx.run("%s update project -t 1 -p ./google-play-services_lib --subprojects" % ctx['sdk_manager'])
    ctx.run("%s update project -t 1 -p ./facebook-android-sdk/facebook --subprojects" % ctx['sdk_manager'])


@task(
    help={
        "profile": "Build profile to use. Default: empty string meaning google play"
    }
)
def patch(ctx, profile=''):
    """
    Patch p4a android project with the updated versions of files, placed in patch/ directory
    """
    import buildozer

    buildo = buildozer.Buildozer()
    buildo.config_profile = profile
    buildo._merge_config_profile()
    buildozer_config = buildo.config

    package_name = buildozer_config.get('app', 'package.name')
    dist_path = ".buildozer/android/platform/build/dists/%s" % package_name
    if not os.path.exists(dist_path):
        fprint("Android project directory %s does not exist, won't patch" % dist_path)
        return False

    tprint("Patching android project: %s" % dist_path)
    ctx.run(
        "rsync -rav ./patch/android/%s/* "
        "%s" % (package_name, dist_path)
    )
    tprint("Patching done")
    return True


@task(
    pre=[check_genymotion],
)
def genymotion(ctx):
    """
    Start emulator. Device id is taken from invoke.json
    """
    tprint("Starting genymotion device...")
    print "Known virtual machines:"
    devices = ctx.run("VBoxManage list vms")
    devices = re.split('\\n|\\t', devices.stdout)
    pattern = re.compile(r"\"(.*?)\" \{(.*?)\}")

    device_names = {}
    for line in devices:
        if not line:
            continue

        match = pattern.search(line)
        if match:
            device_names[match.groups()[1]] = match.groups()[0]
        else:
            print "Can't parse machine name: %s" % line

    try:
        if not ctx['genymotion_device_id'] in device_names:
            fprint("Genymotion device %s is not found in installed genymotion machines." %
                   (ctx['genymotion_device_id'],))
        else:
            iprint("Starting %s..." % device_names[ctx['genymotion_device_id']])

            command = "%(genymotion)s --vm-name %(device_id)s&" % {
                "genymotion": os.path.join(ctx['genymotion_path'], 'player'),
                "device_id": ctx['genymotion_device_id']
            }
            process = multiprocessing.Process(target=ctx.run, args=(command,))
            process.daemon = True
            process.start()
            print 'Waiting genymotion to load'
            sleep(20)
    except KeyError:
        fprint("Genymotion device is not set. Set 'genymotion_device_id' in invoke.json")


@task(
    help={
        "debug": "List only debug apks"
    }
)
def apks(ctx, debug=True):
    """
    Print information about located apks in the bin/ directory
    """
    import buildozer

    buildozer_config = buildozer.Buildozer().config
    if debug:
        pattern = re.compile(r"%s\-(?P<version>\d+\.\d+\.\d+)\-debug\.apk$" % buildozer_config.get('app', 'title'))
    else:
        pattern = re.compile(r"%s\-(?P<version>\d+\.\d+\.\d+)\-release\.apk$" % buildozer_config.get('app', 'title'))
    candidate_apks = {}
    for path in sorted(os.listdir(os.path.abspath('bin'))):
        match = pattern.search(path)
        if match:
            version = match.groups()[0]
            candidate_apks[version] = path
            print version
    print "%s apks" % len(candidate_apks)


@task
def ensure_devices(ctx):
    """
    Check if genymotion emulator is running
    """
    tprint("Start devices...")
    ds = devices(ctx)
    if not ds:
        genymotion(ctx)
        ds = devices(ctx)
        if not ds:
            fprint("Tried to start emulator, still no devices found. Something is wrong.")
            exit(1)
    iprint("Found %s devices" % len(ds))


@task(
    pre=[ensure_devices],
    help={
        "profile": "Profile to use. Default: empty string, meaning google play",
        "debug": "Install debug apk"
    }
)
def install(ctx, profile=None, debug=False):
    """
    Install the latest available apk into currently available device (emulator or real device)
    """
    import buildozer
    profile = profile or ""
    buildo = buildozer.Buildozer()
    buildo.config_profile = profile
    buildo._merge_config_profile()

    buildozer_config = buildo.config
    name = buildozer_config.get('app', 'title').replace(" ", "")

    print "Check if already installed..."
    installed_packages = ctx.run("%(adb)s shell pm list packages %(domain)s.%(name)s" % {
        "adb": ctx['adb'],
        "domain": buildozer_config.get('app', 'package.domain'),
        "name": buildozer_config.get('app', 'package.name')
    }).stdout

    if installed_packages:
        print "Found old version, uninstall..."
        ctx.run('%(adb)s uninstall %(domain)s.%(name)s' % {
            "adb": ctx['adb'],
            "domain": buildozer_config.get('app', 'package.domain'),
            "name": buildozer_config.get('app', 'package.name')
        })
    else:
        print "Not installed, pass..."

    if debug:
        filename = "%s-%s-debug.apk" % (name, buildo.get_version())
    else:
        filename = "%s-%s-release.apk" % (name, buildo.get_version())
    ctx.run('%(adb)s install -r %(apk_path)s' % {
        'adb': ctx['adb'],
        'apk_path': os.path.join(os.path.abspath('bin'), filename)
    })


@task(
    default=True,
    pre=[ensure_devices],
    help={
        "profile": "Profile to use. Default: empty string, meaning google play",
    }
)
def start(ctx, profile=None, logcat=False):
    """
    Start kognitivo inside the current device (emulator or real device)
    """
    import buildozer
    profile = profile or ""
    buildo = buildozer.Buildozer()
    buildozer_config = buildo.config
    buildo.config_profile = profile
    buildo._merge_config_profile()

    tprint("Starting %s on android" % buildozer_config.get('app', 'package.name'))
    ctx.run("%(adb)s shell input keyevent 82" % {
        "adb": ctx["adb"],
    })
    ctx.run("%(adb)s shell am start -n %(package_id)s/org.kivy.android.PythonActivity" % {
        "adb": ctx["adb"],
        "package_id": "%s.%s" % (buildozer_config.get('app', 'package.domain'),
                                 buildozer_config.get('app', 'package.name'))
    })
    if logcat:
        log(ctx, all=True)


@task
def devices(ctx):
    """
    List currently available devices
    """
    tprint("Checking devices...")
    ds = ctx.run('%(adb)s devices' % {
        'adb': ctx['adb'],
    })
    ds = re.split('\\n', ds.stdout)

    serial_pattern = re.compile(r"([0-9a-z]{8})")
    ip_pattern = re.compile(r"(\d+\.\d+\.\d+\.\d+):\d+")

    ds_names = []
    for i, line in enumerate(ds):
        match = serial_pattern.search(line)
        if match and i != 0:
            print "Serial device %s" % match.groups()[0]
            ds_names.append(match.groups()[0])

        match = ip_pattern.search(line)
        if match:
            print "IP device %s" % match.groups()[0]
            ds_names.append(match.groups()[0])
    if not ds_names:
        print "No devices found..."
    else:
        return ds_names


@task(
    pre=[ensure_devices],
    help={
        "all": "Log everything, no filtering for log coming from python activity only"
    }
)
def log(ctx, all=False):
    """
    Start logging from current device (emulator or real device)
    """
    tprint("Starting logcat...")
    try:
        if all:
            print "Capturing all..."
            ctx.run("%(adb)s logcat -c; ADB=%(adb)s logcat-color --config=logcat-color" % {
                "adb": ctx['adb']
            }, pty=True)
        else:
            print "Capturing python only..."
            ctx.run("%(adb)s logcat -c; ADB=%(adb)s logcat-color --config=logcat-color| egrep 'python'" % {
                "adb": ctx['adb']
            }, pty=True)
    except KeyboardInterrupt:
        exit(0)


@task(
    pre=[projects_build, kivy_collection.po, kivy_collection.mo],
    help={
        "deploy": "Immediately install and run on the currently availble device",
        "logcat": "Start logging after installation is finished and the application is started"
    }
)
def debug(ctx, deploy=True, logcat=False):
    """
    Create debug apk
    """
    patched = patch(ctx)
    if deploy:
        ensure_devices(ctx)

    tprint("Building and installing android in debug mode...")
    ctx.run("buildozer android debug", pty=True)
    if not patched:
        patch(ctx)
        ctx.run("buildozer android debug", pty=True)
    if deploy:
        install(ctx, profile='', debug=True)
        start(ctx, profile='')

    if logcat:
        log(ctx, all=True)


@task(
    pre=[projects_build, kivy_collection.po, kivy_collection.mo],
    help={
        "deploy": "Immediately install and run on the currently availble device",
        "logcat": "Start logging after installation is finished and the application is started"
    }
)
def release(ctx, deploy=True, logcat=False):
    """
    Create release apk for google play
    """
    patched = patch(ctx)
    if deploy:
        ensure_devices(ctx)

    tprint("Building and installing android in release mode...")

    os.environ['P4A_RELEASE_KEYSTORE'] = ctx['keystore']
    os.environ['P4A_RELEASE_KEYALIAS'] = ctx['keystore_alias']
    os.environ['P4A_RELEASE_KEYSTORE_PASSWD'] = ctx['keystore_password']
    os.environ['P4A_RELEASE_KEYALIAS_PASSWD'] = ctx['keystore_password']
    ctx.run("buildozer android release", pty=True)

    if not patched:
        patch(ctx)
        ctx.run("buildozer android release", pty=True)

    if deploy:
        install(ctx, profile='release', debug=False)
        start(ctx, profile='release')

    if logcat:
        log(ctx, all=True)


@task
def manager(ctx):
    """
    Start android SDK manager
    """
    tprint("Starting android sdk manager...")
    process = multiprocessing.Process(target=ctx.run, args=(ctx['sdk_manager'],))
    process.daemon = True
    process.start()
    sleep(5)


@task
def avd_manager(ctx):
    """
    Start android SDK manager
    """
    tprint("Starting android emulators manager...")
    process = multiprocessing.Process(target=ctx.run, args=(ctx['sdk_manager'] + " avd",))
    process.daemon = True
    process.start()
    sleep(5)


@task
def adb_kill(ctx):
    """
    Kills running ADB daemon, sometimes useful is you get "port is in use" errors
    """
    ctx.run("%s kill-server" % ctx['adb'])


@task
def adb_start(ctx):
    """
    Starts ADB daemon, sometimes useful is you get "port is in use" errors
    """
    ctx.run("%s start-server" % ctx['adb'])

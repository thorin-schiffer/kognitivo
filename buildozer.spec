[app]
# (str) Title of your application
title = Kognitivo

# (str) Package name
package.name = kognitivo

# (str) Package domain (needed for android/ios packaging)
package.domain = org.kognitivo

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,ttf,json,mo,txt,mp3

# (list) Source files to exclude (let empty to not exclude anything)
source.exclude_exts = spec,ini,sqlite3,pot,md,Makefile

# (list) List of directory to exclude (let empty to not exclude anything)
source.exclude_dirs = tests,data/img/atlas_source, google-play-services_lib, patch, invoke_collections, facebook-android-sdk

# (list) List of exclusions using pattern matching
source.exclude_patterns = build/*, tests/*, release/*, storage-*.json, invoke.json, requirements.txt, logcat-color

# (str) Application versioning (method 1)
version.regex = (\d+\.\d+\.\d+)
version.filename = %(source.dir)s/version.txt

# (str) Application versioning (method 2)
# version = 1.2.0

# (list) Application requirements
requirements = python2, openssl, kivy, sqlite3, pyjnius==1.1.0, raven==6.3.0, android

# (str) Presplash of the application
presplash.filename = %(source.dir)s/data/presplash.jpg

# (str) Icon of the application
icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientation (one of landscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0


#
# Android specific
#

# (list) Permissions
android.permissions = INTERNET, ACCESS_NETWORK_STATE, com.android.vending.BILLING, VIBRATE, android.permission.RECEIVE_BOOT_COMPLETED, android.permission.WRITE_EXTERNAL_STORAGE, android.permission.READ_EXTERNAL_STORAGE, android.permission.READ_CALENDAR, ACCESS_WIFI_STATE

# (int) Android API to use
android.api = 19

# (int) Minimum API required (8 = Android 2.2 devices)
android.minapi = 14

# (int) Android SDK version to use
android.sdk = 22

# (str) Android NDK version to use
android.ndk = 10c

# (str) Android entry point, default is ok for Kivy-based app
#android.entrypoint = org.kivy.android.PythonActivity

# (list) List of Java .jar files to add to the libs so that pyjnius can access
# their classes. Don't add jars that you do not need, since extra jars can slow
# down the build process. Allows wildcards matching, for example:
# OUYA-ODK/libs/*.jar
android.add_jars = jar/*
android.add_src = org
android.presplash_color = #7E7EDC
p4a.branch = stable
p4a.bootstrap = sdl2

# (str) OUYA Console category. Should be one of GAME or APP
# If you leave this blank, OUYA support will not be enabled
#android.ouya.category = GAME

# (str) Filename of OUYA Console icon. It must be a 732x412 png image.
#android.ouya.icon.filename = %(source.dir)s/data/ouya_icon.png

# (str) XML file to include as an intent filters in <activity> tag
#android.manifest.intent_filters = %(source.dir)s/AndroidManifest.xml

# (list) Android additionnal libraries to copy into libs/armeabi
#android.add_libs_armeabi = libs/android/*.so

# (bool) Indicate whether the screen should stay on
# Don't forget to add the WAKE_LOCK permission if you set this to True
#android.wakelock = False
android.add_libs_armeabi = libs/android/*.so
android.add_libs_armeabi_v7a = libs/android-v7/*.so
android.add_libs_x86 = libs/android-x86/*.so
android.whitelist = unittest/*, *unittest*
android.meta_data = com.google.android.gms.version=@integer/google_play_services_version,com.google.android.gms.games.APP_ID=@string/app_id,billing_pubkey = MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAljMD8G+GOYpAXikb+djBTHJL3aeeC3rzI5fo+k1Wwkv9ORHZftKFTrobF8Hd0X6CDZpzCvOjOzxsEHCdwS1dip6oFyxhzQyK6fuqFmsMNUizH+MHRcWTtY2WyMaxqHFZsT5yoGIpW3x9WTVsEGOX2LpsbXZYAOml2QMja5b81EI9bgEf04nvpEhuC8pPza075OO4It47/l/L8opg9zs5cKNiapcqbHczimcqcAfGMV+EbheQdaiyOcs+78Vf7B9QuoxqthaTCscKH14AFPygmH6AdWzj791sO5BkzGutsRW+eDi/3BOBZA4bAeZAjkCfS2oSPhsXifn9gMi6HNe7QIDAQAB,com.facebook.sdk.ApplicationId=@string/facebook_app_id
android.library_references = google-play-services_lib/, facebook-android-sdk/facebook
android.arch = armeabi-v7a

#
# iOS specific
#

# (str) Name of the certificate to use for signing the debug version
# Get a list of available identities: buildozer ios list_identities
#ios.codesign.debug = "iPhone Developer: <lastname> <firstname> (<hexstring>)"

# (str) Name of the certificate to use for signing the release version
#ios.codesign.release = %(ios.codesign.debug)s


[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2


# -----------------------------------------------------------------------------
# List as sections
#
# You can define all the "list" as [section:key].
# Each line will be considered as a option to the list.
# Let's take [app] / source.exclude_patterns.
# Instead of doing:
#
#     [app]
#     source.exclude_patterns = license,data/audio/*.wav,data/images/original/*
#
# This can be translated into:
#
#     [app:source.exclude_patterns]
#     license
#     data/audio/*.wav
#     data/images/original/*
#


[app@release]
log_level = 1

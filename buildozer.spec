[app]
title = Itarak
package.name = itarak
package.domain = org.itarak
source.dir = .
source.include_exts = py,json,kv,png,jpg
version = 1.0.0
requirements = python3,kivy,arabic-reshaper,python-bidi
orientation = portrait
fullscreen = 0
android.api = 35
android.minapi = 24
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1

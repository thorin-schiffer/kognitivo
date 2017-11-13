import os
import pstats

from invoke import task
from invoke.exceptions import Failure

from invoke_collections.utils import tprint, wprint


@task
def profile(ctx):
    tprint("Profiling...")
    p = pstats.Stats('kognitivo.profile')
    p.sort_stats('time').print_stats(40)


@task
def atlas(ctx):
    tprint("Creating atlas...")
    os.chdir("data/atlas")
    try:
        ctx.run("rm *.png")
    except Failure:
        pass
    ctx.run("python -m kivy.atlas menu 512x1024 `find ../img/atlas_source/menu -name \*.png`")
    ctx.run("python -m kivy.atlas activity 1024x1024 `find ../img/atlas_source/activity -name \*.png`")
    ctx.run("python -m kivy.atlas purchases 512x512 `find ../img/atlas_source/purchases -name \*.png`")
    ctx.run("python -m kivy.atlas tasks 1024x1024 `find ../img/atlas_source/tasks -name \*.png`")


@task
def po(ctx):
    tprint("Creating i18n po files...")
    import settings

    ctx.run('(find . -iname "*.py" -not -path "./.buildozer/*" -not -path "./tests/*" &&'
            'find . -iname "*.kv" -not -path "./.buildozer/*" -not -path "./tests/*")'
            '| '
            'xargs xgettext --from-code=UTF-8 -Lpython --output=messages.pot '
            'settings.translate.json main.py')
    ctx.run("""
    sed -i '/POT-Creation-Date*/d' messages.pot
    """)

    ctx.run("""
    sed 's/_(//g;s/\")/"/g;' settings.translate.json > settings.json
    """)

    for lang in settings.LANGUAGES + ['system']:
        ctx.run("msgmerge  --update po/%s.po messages.pot" % (lang if lang != 'system' else 'en'))


@task(pre=[po])
def mo(ctx):
    tprint("Creating i18n files...")
    import settings

    for lang in settings.LANGUAGES + ['system']:
        print 'Processing locale %s' % lang
        ctx.run("mkdir -p data/locales/%s/LC_MESSAGES" % lang)
        report = ctx.run("msgfmt -c %(stat)s -o data/locales/%(lang)s/LC_MESSAGES/kognitivo.mo po/%(lang_po)s.po" % {
            "lang": lang,
            "lang_po": lang if lang != 'system' else 'en',
            "stat": "" if lang in ['en', 'system'] else "--statistics"
        }).stderr
        if "untranslated message" in report or "fuzzy" in report:
            wprint("Language %s has untranslated or fuzzy messages!" % lang)
            exit(1)

# -*- coding: utf-8 -*-
from collections import OrderedDict
import os
import random
from bisect import bisect_left
import gettext
from kivy import Logger
from datetime import datetime

from kivy.app import App
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.utils import get_color_from_hex

SYMBOLS_ALPHABET = [u'\ue033', u'\ue046', u'\ue104', u'\ue109', u'\ue123', u'\ue136', u'\ue139', u'\ue142',
                    u"\uE001", u"\uE002", u"\uE003", u"\u2709", u"\uE005", u"\uE006",
                    u"\uE007", u"\uE008", u"\uE009", u"\uE010", u"\uE011", u"\uE012",
                    u"\uE013", u"\uE014", u"\uE015", u"\uE016", u"\uE017", u"\uE018",
                    u"\uE019", u"\uE020", u"\uE021", u"\uE022", u"\uE023", u"\uE024",
                    u"\uE025", u"\uE026", u"\uE027", u"\uE028", u"\uE029", u"\uE030",
                    u"\uE031", u"\uE032", u"\uE034", u"\uE035", u"\uE036",
                    u"\uE037", u"\uE038", u"\uE039", u"\uE040", u"\uE041", u"\uE042",
                    u"\uE043", u"\uE044", u"\uE045", u"\uE047", u"\uE048",
                    u"\uE049", u"\uE050", u"\uE051", u"\uE052", u"\uE053", u"\uE054",
                    u"\uE055", u"\uE056", u"\uE057", u"\uE058", u"\uE059", u"\uE060",
                    u"\u270F", u"\uE062", u"\uE063", u"\uE064", u"\uE065", u"\uE066",
                    u"\uE067", u"\uE068", u"\uE069", u"\uE070", u"\uE071", u"\uE072",
                    u"\uE073", u"\uE074", u"\uE075", u"\uE076", u"\uE077", u"\uE078",
                    u"\uE079", u"\uE080", u"\uE081", u"\uE082", u"\uE083", u"\uE084",
                    u"\uE085", u"\uE086", u"\uE087", u"\uE088", u"\uE089", u"\uE090",
                    u"\uE091", u"\uE092", u"\uE093", u"\uE094", u"\uE095", u"\uE096",
                    u"\uE097", u"\u002B", u"\u2212", u"\u002A", u"\uE101", u"\uE102",
                    u"\uE103", u"\uE105", u"\uE106", u"\uE107", u"\uE108",
                    u"\uE110", u"\uE111", u"\uE112", u"\uE113", u"\uE114",
                    u"\uE115", u"\uE116", u"\uE117", u"\uE118", u"\uE119", u"\uE120",
                    u"\uE121", u"\uE122", u"\uE124", u"\uE125", u"\uE126",
                    u"\uE127", u"\uE128", u"\uE129", u"\uE130", u"\uE131", u"\uE132",
                    u"\uE133", u"\uE134", u"\uE135", u"\uE137", u"\uE138",
                    u"\uE140", u"\uE141", u"\uE143", u"\uE144",
                    u"\uE145", u"\uE146", u"\u20AC", u"\uE148", u"\uE149", u"\uE150",
                    u"\uE151", u"\uE152", u"\uE153", u"\uE154", u"\uE155", u"\uE156",
                    u"\uE157", u"\uE158", u"\uE159", u"\uE160", u"\uE161", u"\uE162",
                    u"\uE163", u"\uE164", u"\uE165", u"\uE166", u"\uE167", u"\uE168",
                    u"\uE169", u"\uE170", u"\uE171", u"\uE172", u"\uE173", u"\uE174",
                    u"\uE175", u"\uE176", u"\uE177", u"\uE178", u"\uE179", u"\uE180",
                    u"\uE181", u"\uE182", u"\uE183", u"\uE184", u"\uE185", u"\uE186",
                    u"\uE187", u"\uE188", u"\uE189", u"\uE190", u"\uE191", u"\uE192",
                    u"\uE193", u"\uE194", u"\uE195", u"\u2601", u"\uE197", u"\uE198",
                    u"\uE199", u"\uE200"]


class Interpolator(object):
    def __init__(self, x_list, y_list):
        if any(y - x <= 0 for x, y in zip(x_list, x_list[1:])):
            raise ValueError("x_list must be in strictly ascending order!")
        x_list = self.x_list = map(float, x_list)
        y_list = self.y_list = map(float, y_list)
        intervals = zip(x_list, x_list[1:], y_list, y_list[1:])
        self.slopes = [(y2 - y1) / (x2 - x1) for x1, x2, y1, y2 in intervals]

    def __getitem__(self, x):
        i = bisect_left(self.x_list, x) - 1
        return self.y_list[i] + self.slopes[i] * (x - self.x_list[i])


class NaiveProfiler(object):
    def __init__(self):
        self.start = datetime.now()
        self.ticker = OrderedDict({})
        self.times = OrderedDict({})

    def fix_from(self, label):
        self.ticker[label] = datetime.now()

    def fix_to(self, label):
        self.times[label] = (datetime.now() - self.ticker[label]).total_seconds()
        Logger.info("Profiling: %s: %s" % (label, self.times[label]))

    def print_all(self):
        s = (datetime.now() - self.start).total_seconds()
        message = ""
        for label in self.times:
            message += "%s: %s, %.2f%%\n" % (label, self.times[label], 100. * self.times[label] / s)
        Logger.info("Profiling: summary:\n%s" % message)


class _(unicode):
    observers = []
    lang = None

    def __new__(cls, s, *args, **kwargs):
        if 'KIVY_UNITTEST' in os.environ:
            _.switch_lang('en')

        if _.lang is None:
            Logger.error(
                "Gettext __new__ is called before configuration read. "
                "Put statements in constructors, not on the class/function/module level"
            )
            _.switch_lang('en')

        s = _.translate(s, *args, **kwargs)
        return super(_, cls).__new__(cls, s)

    @staticmethod
    def translate(s, *args, **kwargs):
        return _.lang(s).format(args, kwargs)

    @staticmethod
    def bind(**kwargs):
        _.observers.append(kwargs['_'])

    @staticmethod
    def switch_lang(lang):
        # get the right locales directory, and instanciate a gettext
        locale_dir = os.path.join(os.path.dirname(__file__), 'data', 'locales')
        locales = gettext.translation('kognitivo', locale_dir,
                                      languages=[lang])
        _.lang = locales.ugettext

        # update all the kv rules attached to this text
        for callback in _.observers:
            callback()


COLORS = [
    "ff5555ff", "ff7f2aff", "ccff00ff", "00aad4ff", "666666ff", "7e7edcff", "55d400ff"
]

ci = 0

random.shuffle(COLORS)


def get_random_color():
    global ci
    ret = get_color_from_hex(COLORS[ci])
    ci = (ci + 1) % len(COLORS)
    return ret


def import_kv(path):
    import os

    base_path = os.path.dirname(os.path.abspath(__file__))
    kv_path = os.path.relpath(path, base_path).rsplit(".", 1)[0] + ".kv"
    kv_path = os.path.join('kv', kv_path)
    if kv_path not in Builder.files:
        Builder.load_file(kv_path, rulesonly=True)
        Logger.info("KV: load %s, overall: %s" % (kv_path, len(Builder.files)))


FONT_SCALES = {
    "extra_small": .7,
    "small": .85,
    "normal": 1.0,
    "big": 1.3,
    "extra_big": 1.6,
}


def get_font_scale():
    app = App.get_running_app()
    name = app.config.get('preferences', 'font_size')
    return FONT_SCALES[name]


def isp(value):
    return dp(value) * get_font_scale()


def popup_open(klass):
    klass_found = False
    children = App.get_running_app().root_window.children
    for child in children:
        klass_found |= isinstance(child, klass)
    return klass_found


def export_to_png(widget, filename, fill_color):
    from kivy.graphics import (Translate, Fbo, ClearColor, ClearBuffers, Scale)

    if widget.parent is not None:
        canvas_parent_index = widget.parent.canvas.indexof(widget.canvas)
        widget.parent.canvas.remove(widget.canvas)

    fbo = Fbo(size=widget.size, with_stencilbuffer=True)

    with fbo:
        ClearColor(*fill_color)
        ClearBuffers()
        Scale(1, -1, 1)
        Translate(-widget.x, -widget.y - widget.height, 0)

    fbo.add(widget.canvas)
    fbo.draw()
    fbo.texture.save(filename, flipped=False)
    fbo.remove(widget.canvas)

    if widget.parent is not None:
        widget.parent.canvas.insert(canvas_parent_index, widget.canvas)

    return True


def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)


def writable(fname):
    try:
        touch(fname)
    except (OSError, IOError) as ex:
        Logger.info("OS: %s is not writable: %s" % (fname, unicode(ex)))
        return False
    return True

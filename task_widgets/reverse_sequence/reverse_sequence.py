# -*- coding: utf-8 -*-
import random

from kivy.properties import ListProperty

from answer_widgets import AnswerButton, BoxButtonsAnswerWidget
from description_widgets import TextDescriptionWidget
from task_widgets.task_base.base import BaseTask
from task_widgets.task_base.mixins import StartImmediatelyMixin
from utils import import_kv

import_kv(__file__)


class ReverseSequenceAnswerButton(AnswerButton):
    pass


class ReverseSequenceAnswerWidget(BoxButtonsAnswerWidget):
    BUTTON_WIDGET_CLASS = ReverseSequenceAnswerButton


class ReverseSequenceDescriptionWidget(TextDescriptionWidget):
    pass


class ReverseSequence(BaseTask, StartImmediatelyMixin):
    SIZE = 5
    ANSWER_WIDGET_CLASS = ReverseSequenceAnswerWidget
    DESCRIPTION_WIDGET_CLASS = ReverseSequenceDescriptionWidget
    ALPHABET = None
    ANSWER_JOINER = u"[color=#ccccccff]|[/color]"
    sequence = ListProperty([])
    FIXED_ELEMENTS = .2  # part of the sequence length, which fixed at start and end of the sequence while shuffling

    def sequence_to_text(self):
        return u"[color=#ccccccff]|[/color]".join(self.sequence)

    def generate_alphabet(self):
        raise NotImplementedError()

    def get_description_widget(self, **kwargs):
        self.sequence = random.sample(self.generate_alphabet(), self.SIZE)
        widget = super(ReverseSequence, self).get_description_widget(**kwargs)
        widget.text = self.sequence_to_text()
        self.correct_answer = tuple(self.sequence[::-1])
        return widget

    def get_answer_widget(self, **kwargs):
        gap = int(self.FIXED_ELEMENTS * len(self.sequence))
        variants = [self.correct_answer]

        i = 0
        while len(variants) < self.SIZE:
            variant = self.sequence[:gap]
            center = list(self.sequence[gap:-gap])
            random.shuffle(center)
            variant += center + self.sequence[-gap:]
            variant = tuple(variant[::-1])
            i += 1
            if i > 100:
                raise Exception("Reverse sequence can't get enough different answer variants")
            if variant not in variants:
                variants.append(variant)
        random.shuffle(variants)
        container = super(ReverseSequence, self).get_answer_widget(**kwargs)
        container.add_variants(variants, self._check_answer, lambda x: self.ANSWER_JOINER.join(x))
        return container

import random

from kivy.properties import NumericProperty, ObjectProperty

from answer_widgets import BoxButtonsAnswerWidget
from description_widgets import TextDescriptionWidget
from task_widgets.task_base.base import BaseTask
from task_widgets.task_base.mixins import StartImmediatelyMixin


class Calculation(BaseTask, StartImmediatelyMixin):
    SIZE = 5
    ANSWER_WIDGET_CLASS = BoxButtonsAnswerWidget
    DESCRIPTION_WIDGET_CLASS = TextDescriptionWidget


class OperandsCalculation(Calculation):
    first = ObjectProperty()
    second = ObjectProperty()
    result = ObjectProperty()

    def calculate_operands(self):
        raise NotImplementedError()

    def __init__(self, **kwargs):
        super(OperandsCalculation, self).__init__(**kwargs)
        self.calculate_operands()

    def build_text(self):
        raise NotImplementedError()

    def get_description_widget(self):
        label = super(OperandsCalculation, self).get_description_widget(text=self.build_text())
        return label

    def get_next_variant(self):
        raise NotImplementedError()

    def get_variants(self):
        variants = [self.correct_answer]
        variant = self.correct_answer
        for _ in xrange(self.SIZE - 1):
            for i in range(100):
                if variant in variants:
                    variant = self.get_next_variant()
                else:
                    break
            variants.append(variant)
        return variants

    def get_answer_widget(self):
        variants = self.get_variants()
        random.shuffle(variants)
        container = super(OperandsCalculation, self).get_answer_widget()
        container.add_variants(variants, self._check_answer, text_modifier=self.variant_modifier)
        return container

    def variant_modifier(self, value):
        return unicode(value)


class ModeOperandsCalculation(OperandsCalculation):
    mode = NumericProperty(None, allownone=True)
    MAX_MODE = 2

    def calculate_mode(self):
        if self.mode is None:
            import random
            self.mode = random.randint(0, self.MAX_MODE)

    def __init__(self, **kwargs):
        super(ModeOperandsCalculation, self).__init__(**kwargs)
        self.calculate_mode()

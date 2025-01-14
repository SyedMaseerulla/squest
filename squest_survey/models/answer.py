# -*- coding: utf-8 -*-

"""
These type-specific answer models use a text field to allow for flexible
field sizes depending on the actual question this answer corresponds to any
"required" attribute will be enforced by the form.
"""

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .response import Response
from .question import Question


class Answer(models.Model):
    response = models.ForeignKey(Response, on_delete=models.CASCADE, verbose_name=_('Response'), related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name=_('Question'), related_name='answers')
    created = models.DateTimeField(_('Creation date'), auto_now_add=True)
    updated = models.DateTimeField(_('Update date'), auto_now=True)
    body = models.TextField(_('Content'), blank=True, null=True)

    class Meta:
        verbose_name = _('answer')
        verbose_name_plural = _('answers')
        ordering = ('response', 'question')

    def __init__(self, *args, **kwargs):
        try:
            question = Question.objects.get(pk=kwargs['question_id'])
        except KeyError:
            question = kwargs.get('question')
        body = kwargs.get('body')
        if question and body:
            self.check_answer_body(question, body)
        super(Answer, self).__init__(*args, **kwargs)

    @property
    def values(self):
        if self.body is None:
            return [None]
        if len(self.body) < 3 or self.body[0:3] != "[u'":
            return [self.body]
        values = []
        raw_values = self.body.split("', u'")
        nb_values = len(raw_values)
        for i, value in enumerate(raw_values):
            if i == 0:
                value = value[3:]
            if i + 1 == nb_values:
                value = value[:-2]
            values.append(value)
        return values

    def check_answer_body(self, question, body):
        if question.type in [Question.RADIO, Question.SELECT]:
            choices = question.get_clean_choices()
            if body:
                if body[0] == '[':
                    answers = []
                    for i, part in enumerate(body.split('\'')):
                        if i % 2 == 1:
                            answers.append(part)
                else:
                    answers = [body]
            for answer in answers:
                if answer not in choices:
                    msg = "Impossible answer '{}'".format(body)
                    msg += " should be in {} ".format(choices)
                    raise ValidationError(msg)

    def __str__(self):
        return '{} to \'{}\' : \'{}\''.format(self.__class__.__name__, self.question, self.body)

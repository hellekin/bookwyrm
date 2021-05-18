""" template filters """
from dateutil.relativedelta import relativedelta
from django import template
from django.contrib.humanize.templatetags.humanize import naturaltime, naturalday
from django.utils import timezone
from bookwyrm import models
from bookwyrm.templatetags.utilities import get_user_identifier


register = template.Library()


@register.filter(name="mentions")
def get_mentions(status, user):
    """people to @ in a reply: the parent and all mentions"""
    mentions = set([status.user] + list(status.mention_users.all()))
    return (
        " ".join("@" + get_user_identifier(m) for m in mentions if not m == user) + " "
    )


@register.filter(name="replies")
def get_replies(status):
    """get all direct replies to a status"""
    # TODO: this limit could cause problems
    return models.Status.objects.filter(
        reply_parent=status,
        deleted=False,
    ).select_subclasses()[:10]


@register.filter(name="parent")
def get_parent(status):
    """get the reply parent for a status"""
    print(status, status.reply_parent)
    return (
        models.Status.objects.filter(id=status.reply_parent_id)
        .select_subclasses()
        .first()
    )


@register.filter(name="boosted_status")
def get_boosted(boost):
    """load a boosted status. have to do this or it won't get foreign keys"""
    return models.Status.objects.select_subclasses().get(id=boost.boosted_status.id)


@register.filter(name="published_date")
def get_published_date(date):
    """less verbose combo of humanize filters"""
    if not date:
        return ""
    now = timezone.now()
    delta = relativedelta(now, date)
    if delta.years:
        return naturalday(date)
    if delta.days:
        return naturalday(date, "M j")
    return naturaltime(date)


@register.filter(name="header_template")
def get_header_tempplate(status):
    """get the path for the status template"""
    filename = status.note_type if hasattr(status, "note_type") else status.status_type
    return "snippets/status/headers/{:s}.html".format(filename.lower())

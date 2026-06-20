from django.shortcuts import render
from django.utils.safestring import mark_safe

from random import choice
from markdown2 import Markdown

from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def get_page(request, title):
    rtn = util.get_entry(title)
    md = Markdown()
    html = md.convert(rtn)
    return render(request, "encyclopedia/get.html", {
        "content": mark_safe(html),
        "title": title
    })


def create(request):
    return render(request, "encyclopedia/create.html")
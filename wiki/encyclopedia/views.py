from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.safestring import mark_safe

import requests
from random import choice
from markdown2 import Markdown

from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def get_page(request, title):
    content = util.get_entry(title)

    if title and content:
        md = Markdown()
        html = md.convert(content)
        return render(request, "encyclopedia/get.html", {
            "content": mark_safe(html),
            "title": title
        })

    else:
        return HttpResponse("Page not available")

def create(request):
    if request.method == 'POST':
        title = request.POST.get('head')
        description = request.POST.get('content')

        entries = util.list_entries()

        if title in entries:
            return HttpResponse("Page Already Available")
        
        if title and description:
            util.save_entry(title, description)
            entries = util.list_entries()
            return render(request, "encyclopedia/index.html", {
                "entries": entries
            })

        else:
            return HttpResponse("Please fill all fields")
    
    else:
        return render(request, 'encyclopedia/create.html')


def edit(request, title):
    content = util.get_entry(title)

    if content is None:
        return HttpResponseNotFound("Page not found")

    if request.method == "POST":
        new_content = request.POST.get('content', '')

        if new_content:
            util.save_entry(title, new_content)
            return redirect('get', title=title)
        else:
            return HttpResponse("Content cannot be empty")

    else:
        return render(request, "encyclopedia/edit.html", {
            "title": title,
            "content": content
        })


def search(request):
    if request.method == "POST":
        query = request.POST.get('search', '').strip()
        
        if not query:
            return render(request, "encyclopedia/search.html", {
                "title": "Search",
                "content": mark_safe("<h3>Please enter a search term.</h3>")
            })
        
        entries = util.list_entries()
        
        for entry in entries:
            if entry.lower() == query.lower():
                return redirect('get', title=entry)
        
        results = []
        for entry in entries:
            if query.lower() in entry.lower():
                results.append(entry)
        
        if results:
            html = f"<h2>Results for '{query}'</h2><ul>"
            for entry in results:
                html += f'<li><a href="/wiki/{entry}">{entry}</a></li>'
            html += "</ul>"

        else:
            html = f"<h2>No results found for '{query}'</h2>"
        
        return render(request, "encyclopedia/search.html", {
            "title": query,
            "content": mark_safe(html)
        })
    
    return render(request, "encyclopedia/search.html")


def random(request):
    names = util.list_entries()
    title = choice(names)
    content = util.get_entry(title)

    md = Markdown()
    html = md.convert(content)
    
    return render(request, "encyclopedia/random.html", {
        "title": title,
        "content": mark_safe(html)
    })

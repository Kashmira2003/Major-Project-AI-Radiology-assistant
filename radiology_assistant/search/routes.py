from radiology_assistant.search import search
from flask import render_template, redirect, url_for, request, g
from radiology_assistant.models import Disease
from radiology_assistant.search.forms import SearchForm
from config import Config

@search.before_app_request
def before_request():
    g.search_form = SearchForm()
    
@search.route("/search")
def search():
    if g.search_form.validate():
        page = request.args.get('page', 1, type=int)
        diseases = Disease.query.filter(Disease.name.like(f"%{g.search_form.query.data}%")).paginate(page=page, per_page=Config.SEARCH_CASES_PER_PAGE)
        return render_template("search.html", diseases=diseases)
    else:
        return redirect(url_for("main.home"))
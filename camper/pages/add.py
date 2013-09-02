#encoding=utf8

from starflyer import Handler, redirect
from camper import BaseForm, db, logged_in, string2filename, BaseHandler, is_admin
from wtforms import *

__all__ = ['PageAddForm', 'AddView']

class PageAddForm(BaseForm):
    """form for adding a barcamp"""
    title           = TextField(u"Titel", [validators.Length(max=300), validators.Required()],
                description = u'Titel der Seite (max. 300 Zeichen)',)

class AddView(BaseHandler):
    """handler for adding a new page"""

    template = "pages/add.html"

    @logged_in()
    @is_admin()
    def get(self, slug = None, slot = None):
        """render the view"""
        form = PageAddForm(self.request.form, config = self.config)
        if self.request.method == 'POST' and form.validate():
            f = form.data
            slug = f['slug'] = string2filename(f['title'])
            # TODO: check if it's double
            f['menu_title'] = f['title'][:50]
            f['content'] = "Content hier"
            page = db.Page(f)
            page = self.config.dbs.pages.add_to_slot(slot, page, barcamp = self.barcamp)
            self.flash("Seite wurde wurde angelegt", category="info")
            if self.barcamp is not None:
                url = self.url_for("barcamp_page", slug = self.barcamp.slug, page_slug = slug)
            else:
                url = self.url_for("page", page_slug = slug)
            return self.render(tmplname = "redirect.html", url = url)
        return self.render(form = form)

    post = get



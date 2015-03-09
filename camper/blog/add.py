from starflyer import Handler, redirect, asjson
import werkzeug.exceptions
from camper import BaseForm, db, BaseHandler
from camper import logged_in, is_admin, ensure_barcamp
from camper.barcamps.base import BarcampBaseHandler
from camper.utils import string2filename


from wtforms import *
from camper.handlers.forms import *
from sfext.babel import T
from camper.form import MyDateField, ATextInput, ACheckboxInput, ATextArea

__all__=['AddView']

class EntryAddForm(BaseForm):
    """form for adding an event to a barcamp"""
    title                = TextField(T(u"Title"), [validators.Length(max=300), validators.Required()],
                widget=ATextInput(),
                description = T(u'Title of the blog post (required)'),
    )

    content                 = TextAreaField(T(u"Content"), [],
                description = T(u'The content of the blog post'),
                widget = ATextArea()
    )
    image               = UploadField(T(u"Title image"))



class AddView(BarcampBaseHandler):
    """view for adding a new blog entry"""

    template = "add.html"

    @logged_in()
    @ensure_barcamp()
    @is_admin()
    def get(self, slug = None):
        """render the view"""
        form = EntryAddForm(self.request.form, config = self.config)
        if self.request.method == 'POST' and form.validate():
            f = form.data
            slug = f['slug'] = string2filename(f['title'])
            entry = db.BlogEntry(f)
            entry = self.config.dbs.blog.add(entry, barcamp = self.barcamp)
            self.flash(self._("The blog entry was created"), category="info")
            url = self.url_for("barcamps.index", slug = self.barcamp.slug)
            return redirect(url)
        return self.render(form = form)

    post = get

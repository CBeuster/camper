#encoding=utf8

import copy
import json
from starflyer import Handler, redirect, asjson, AttributeMapper
from camper import BaseForm, db, BaseHandler, is_admin, logged_in, ensure_barcamp
from wtforms import *
from sfext.babel import T
from .base import BarcampBaseHandler
from camper import utils
from camper.handlers.forms import *

class DesignForm(BaseForm):
    """form for design aspects of a barcamp"""
    background_image        = UploadField(T(u"Background-Image"))
    fb_image                = UploadField(T(u"Image for Facebook"))
    font                    = StringField(T(u"Font to use"), default='"Helvetica Neue", "Helvetica", "Arial", sans-serif')
    link_color              = ColorField(T(u"Link Color"), default='#333')
    header_color            = ColorField(T(u"Header Background Color"), default='#fcfcfa')
    text_color              = ColorField(T(u"Text Color"), default='#333')
    background_color        = ColorField(T(u"Background Color"), default='#f0f019')

    navbar_link_color       = ColorField(T(u"Navbar Link Color"), default='#888')
    navbar_active_color     = ColorField(T(u"Navbar Active Link Color"), default='#f8f8f8')
    navbar_border_color     = ColorField(T(u"Navbar Border Color"), default='#b0b0b0')
    navbar_hover_bg         = ColorField(T(u"Navbar Hover Background Color"), default='#d0d0d0')
    navbar_active_bg        = ColorField(T(u"Navbar Active Background Color"), default='#333')

class DesignView(BarcampBaseHandler):
    """handle screen for handling design"""

    template = "design.html"

    @ensure_barcamp()
    @logged_in()
    @is_admin()
    def get(self, slug = None):
        """show the form"""
        form = DesignForm(self.request.form, config = self.config)
        if self.request.method == "POST" and form.validate():
            f = form.data
            self.barcamp.update(f)
            self.barcamp.save()
        return self.render(form = form)

    post = get

        

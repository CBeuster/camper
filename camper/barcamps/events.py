#encoding=utf8

from starflyer import Handler, redirect, asjson
from camper import BaseForm, db, BaseHandler, is_admin, logged_in, ensure_barcamp
from .base import BarcampBaseHandler
from wtforms import *
from sfext.babel import T
import uuid
import datetime
import requests
from form import MyDateField, ATextInput, ACheckboxInput, ATextArea


class EventForm(BaseForm):
    """form for adding an event to a barcamp"""
    name                = TextField(T(u"name of location"), [validators.Length(max=300), validators.Required()],
                widget=ATextInput(),
                description = T(u'Title of this event, e.g. "Day 1" or "Party"'),
    )

    description                 = TextAreaField(T(u"Description"), [],
                description = T(u'This is not the common barcamp description but should be specific about this event.'),
                widget = ATextArea()
    )
    date                        = MyDateField(T(u"date"), [], default=None, format="%d.%m.%Y", description="")
    start_time                  = TextField(T(u"start time"), [validators.Required()], description="")
    end_time                    = TextField(T(u"end time"), [validators.Required()], description="")
    size                        = SelectField(T(u"max. number of participants"), [validators.Required()], 
                                        choices = [(str(n),str(n)) for n in range(1, 1000)])
    
    own_location                = BooleanField(T("use different location"), widget = ACheckboxInput())
    location_name               = TextField(T("name of location"), [], description = T('please enter the name of the venue here'),)
    location_street             = TextField(T("street and number "), [], description = T('street and number of the venue'),)
    location_city               = TextField(T("city"), [])
    location_zip                = TextField(T("zip"), [])
    location_url                = TextField(T("homepage"), [], description=T('web site of the venue (optional)'))
    location_phone              = TextField(T("phone"), [], description=T('web site of the venue (optional)'))
    location_email              = TextField(T("email"), [], description=T('email address of the venue (optional)'))
    location_description        = TextAreaField(T("description"), [], description=T('an optional description of the venue'))

def retrieve_location(f):
    """retrieve coords for a location based on the address etc. stored in ``f``"""
    url = "http://nominatim.openstreetmap.org/search?q=%s, %s&format=json&polygon=0&addressdetails=1" %(
        form.data['location_street'],
        form.data['location_city'],
    )
    data = requests.get(url).json()
    if len(data)==0:
        # trying again but only with city
        url = "http://nominatim.openstreetmap.org/search?q=%s&format=json&polygon=0&addressdetails=1" %(
            form.data['location_city'],
        )
        data = requests.get(url).json()
    if len(data)==0:
        self.flash(self._("the city was not found in the geo database"), category="danger")
        return self.render(form = form)
    # we have at least one entry, take the first one
    result = data[0]
    f['location']['lat'] = result['lat']
    f['location']['lng'] = result['lon']
    return f


class EventsView(BarcampBaseHandler):
    """shows the event page where you can add, edit and delete events"""

    template = "events.html"

    @ensure_barcamp()
    @logged_in()
    @is_admin()
    def get(self, slug = None):
        """show the list of events and an add form for adding more"""

        # prefill some values if there's already a previous event
        obj = {}
        if len(self.barcamp.events):
            e = self.barcamp.events[-1]
            obj['date'] = e['date'] + datetime.timedelta(days=1)
            obj['start_time'] = e['start_time']
            obj['end_time'] = e['end_time']
            obj['size'] = e['size']

        print obj
        form = EventForm(self.request.form, config = self.config, **obj)
        if self.request.method == 'POST' and form.validate():
            f = form.data
            f['location'] = {
                'name'      : f['location_name'],
                'street'    : f['location_street'],
                'city'      : f['location_city'],
                'zip'       : f['location_zip'],
                'email'     : f['location_email'],
                'phone'     : f['location_phone'],
                'url'       : f['location_url'],
                'description' : f['location_description'],
                'country'   : 'de',
            }

            # retrieve geo location (but only when not in test mode as we might be offline)
            if f['location_street'] and not self.config.testing and f['own_location']:
                f = retrieve_location(f)

            # create and save the event object inside the barcamp
            f['_id'] = unicode(uuid.uuid4())
            event = db.Event(f)
            self.barcamp.events.append(event)
            self.barcamp.save()

            self.flash(self._("The event has been created"), category="info")
            return redirect(self.url_for(".events", slug=slug))
        return self.render(form = form, slug = slug, events = self.barcamp.events)
    post = get

    @ensure_barcamp()
    @logged_in()
    @is_admin()
    @asjson()
    def delete(self, slug):
        """delete an event"""
        eid = self.request.form['event']
        idx = 0
        for e in self.barcamp.events:
            if str(e['_id']) == str(eid):
                self.barcamp.events.remove(e)
                break
            idx = idx + 1 
        self.barcamp.save()
        return {'status' : 'ok'}


class EventView(BarcampBaseHandler):
    """shows one event which you can then edit"""

    template = "event.html"

    @ensure_barcamp()
    @logged_in()
    @is_admin()
    def get(self, slug = None, eid = None):
        """show the event details"""
        event = self.barcamp.get_event(eid)

        form = EventForm(self.request.form, obj = event, config = self.config)
        if self.request.method == 'POST' and form.validate():
            f = form.data
            f['location'] = {
                'name'      : f['location_name'],
                'street'    : f['location_street'],
                'city'      : f['location_city'],
                'zip'       : f['location_zip'],
                'email'     : f['location_email'],
                'phone'     : f['location_phone'],
                'url'       : f['location_url'],
                'description' : f['location_description'],
                'country'   : 'de',
            }

            # retrieve geo location (but only when not in test mode as we might be offline)
            if f['location_street'] and not self.config.testing and f['own_location']:
                f = retrieve_location(f)

            # create and save the event object inside the barcamp
            f['_id'] = unicode(uuid.uuid4())
            event = db.Event(f)
            self.barcamp.events.append(event)
            self.barcamp.save()

            self.flash(self._("The event has been created"), category="info")
            return redirect(self.url_for(".events", slug=slug))
        return self.render(form = form, slug = slug, events = self.barcamp.events, event=event)
    post = get

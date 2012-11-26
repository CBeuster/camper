from mongogogo import *
import datetime

class PageError(Exception):
    """something was wrong with a page related class"""

    def __init__(self, msg):
        self.msg = msg

    def __repr__(self):
        return "<PageError: %s>" %msg

    def __str__(self):
        return "<PageError: %s>" %msg


class PageSchema(Schema):
    """a location described by name, lat and long"""
    created         = DateTime()
    updated         = DateTime()
    created_by      = String() # TODO: should be ref to user

    title           = String(required=True)
    menu_title      = String(required=True)
    slug            = String(required=True)
    image           = String(required=False) # asset id
    layout          = String() # name of layout
    content         = String()
    barcamp         = String() # or empty for homepage
    index           = Integer() # sequence number in list of pages
    slot            = String() # slot id of the page
     

class Page(Record):
    schema = PageSchema()
    default_values = {
        'created'       : datetime.datetime.utcnow,
        'updated'       : datetime.datetime.utcnow,
        'title'         : "",
        'slug'          : "",
        'content'       : "",
        'layout'        : "default",
        'slot'          : "default",
        'index'         : 1,
        'layout'        : "default",
        'image'         : None
    }

class Pages(Collection):
    
    data_class = Page

    def reorder_slot(self, slot, indexes):
        """reorders a slot. You give it the slot id in ``slot`` and the new sequence order in indexes in form of a list.

        Passing in [2,3,1] will reorder the existing pages in this order
        """
        pages = self.for_slot(slot)
        # do some checks
        if len(indexes) != pages.count():
            raise PageError("length of indexes (%s) does not match amount of pages (%s)" %(len(indexes), pages.count()))
           
        pages = list(pages)
        for page in pages:
            print page.index
            if page.index not in indexes:
                raise PageError("page with index %s missing in new indexes list" %(page.index))
            page.index = indexes.index(page.index)
            print page.index

        # finally save it
        for page in pages:
            page.put()

    def add_to_slot(self, slot, page):
        """adds a new page into a slot at the end of it. You can give the page object without the slot set and it will do the rest"""
        page.slot = slot
        page.index = self.find({'slot' : page.slot}).count()
        return self.put(page)

    def remove_from_slot(self, slot, index):
        """removes a page at index ``index``"""
        page = self.find_one({'slot' : slot, 'index' : index})
        self.remove({'_id' : page._id})

    def for_slot(self, slot):
        """return all the pages for a slot"""
        return self.find({'slot' : slot}).sort("index", 1)



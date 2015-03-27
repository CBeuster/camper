from mongogogo import *
import datetime
from camper.exceptions import *
import pymongo

__all__=["ImageGallery", "ImageGalleries"]


class ImageGallerySchema(Schema):
    """describes an image gallery for a barcamp"""
    created         = DateTime()
    updated         = DateTime()
    created_by      = String() # TODO: should be ref to user
    title           = String()
    
    images          = List(String(), default=[]) # list of images contained in the gallery
    barcamp         = String(required = True) 
    

class ImageGallery(Record):
    schema = ImageGallerySchema()
    default_values = {
        'created'       : datetime.datetime.utcnow,
        'updated'       : datetime.datetime.utcnow,
        'title'         : "",
        'images'        : [],
    }

    
class ImageGalleries(Collection):
    
    data_class = ImageGallery

    def before_serialize(self, obj):
        obj['updated'] = datetime.datetime.utcnow()
        return obj

    
    def by_barcamp(self, barcamp):
        """return all image galleries for a barcamp

        :param barcamp: barcamp object for which blog posts should be searched
        :returns: list of blog entries sorted according to arguments

        """
        q = {'barcamp' : unicode(barcamp._id) }
        return self.find(q)

    def add(self, gallery, barcamp = None):
        """adds a new blog entry"""
        if barcamp is not None:
            gallery.barcamp = unicode(barcamp._id)
        else:
            raise ValueError, "you need to provide a barcamp"
        return self.put(gallery)

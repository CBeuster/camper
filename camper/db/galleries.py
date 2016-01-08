from mongogogo import *
import datetime
from camper.exceptions import *
import pymongo
import uuid

__all__=["ImageGallery", "ImageGalleries", "Image"]

class ImageSchema(Schema):
    """schema for an individual image"""

    _id             = String() # something to identify it
    image           = String()
    title           = String()
    alt             = String()
    description     = String()
    license         = String()
    copyright       = String()


class ImageGallerySchema(Schema):
    """describes an image gallery for a barcamp"""
    created         = DateTime()
    updated         = DateTime()
    created_by      = String() # TODO: should be ref to user
    title           = String()
    
    images          = List(ImageSchema(), default=[]) # list of images contained in the gallery
    barcamp         = String(required = True) 


class Image(Record):
    """represents a single image"""

    schema = ImageSchema()

    default_values = {
        '_id'           : lambda : unicode(uuid.uuid4()),
        'title'         : '',
        'alt'           : '',
        'description'   : '',
        'license'       : '',
        'copyright'     : '',
    }

class ImageGallery(Record):
    schema = ImageGallerySchema()
    default_values = {
        'created'       : datetime.datetime.utcnow,
        'updated'       : datetime.datetime.utcnow,
        'title'         : "",
        'images'        : {},
    }

    def get_images(self):
        """return image objects"""
        return [Image(**image) for image in self.images]

    def get_image(self, image_id):
        """return one image specified by the id or None"""
        for image in self.images:
            if image['_id'] == image_id:
                return Image(image)
        return None

    def delete_image(self, image_id):
        """delete an image"""
        for image in self.images:
            if image['_id'] == image_id:
                self.images.remove(image)
                return True
        return False

        del self.images[image_id]

    def add_image(self, image):
        """add a new image to the gallery.

        :param image: An instance of ``Image``
        """
        self.images.append(image)

    def update_image(self, new_image):
        """update the image in the image list.

        You have to use that method because you will get
        a wrapped image object back from get_image()
        """
        for i, image in enumerate(self.images):
            if image['_id'] == new_image['_id']:
                self.images[i] = new_image
                return


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



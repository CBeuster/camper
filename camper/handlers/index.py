#encoding=utf8

import datetime
import pymongo

from camper import BaseHandler
from ..base import BarcampView


class IndexView(BaseHandler):
    """an index handler"""

    template = "index.html"

    def get(self):
        """render the view"""
        n = datetime.datetime.now()
        soon_barcamps = self.config.dbs.barcamps.find({
            'end_date'  : {'$gt': n},
        }).sort("start_date", pymongo.ASCENDING).limit(10)
        new_barcamps = self.config.dbs.barcamps.find({
            'end_date'  : {'$gt': n},
        }).sort("created",pymongo.DESCENDING).limit(3)
        if self.logged_in:
            my_barcamps = self.config.dbs.barcamps.find({
                'admins'  : {'$in': [self.user_id]},
            }).sort("created",pymongo.DESCENDING)
        else:
            my_barcamps = None
        soon_barcamps = [BarcampView(barcamp, self) for barcamp in soon_barcamps]
        soon_barcamps = [b  for b in soon_barcamps if b.barcamp.public or b.is_admin or self.is_main_admin]
        new_barcamps = [BarcampView(barcamp, self) for barcamp in new_barcamps]
        new_barcamps = [b  for b in new_barcamps if b.barcamp.public or b.is_admin or self.is_main_admin]
        my_barcamps = [BarcampView(barcamp, self) for barcamp in my_barcamps]
        my_barcamps = [b for b in my_barcamps if b.barcamp.public or b.is_admin or self.is_main_admin]
        return self.render( 
            soon_barcamps = soon_barcamps,
            new_barcamps = new_barcamps,
            my_barcamps = my_barcamps,
        )
    post = get

class Impressum(BaseHandler):
    """show the impressum"""

    template = "impressum.html"

    def get(self):
        """render the view"""
        return self.render()


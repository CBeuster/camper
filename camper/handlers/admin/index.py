#encoding=utf8

from starflyer import Handler

class IndexView(Handler):
    """an index handler"""

    template = "admin/index.html"

    def get(self):
        """render the view"""
        return self.render()
    post = get


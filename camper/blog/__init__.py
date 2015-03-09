from starflyer import Module, URL

import add
import entries

class BlogModule(Module):
    """handles everything regarding blogposts"""

    name = "blog"

    routes = [
	    URL('/<slug>/blog', 			'entries',		  entries.ListView),
	    URL('/<slug>/blog/new', 		'add',            add.AddView),
	]

blog_module = BlogModule(__name__)

        
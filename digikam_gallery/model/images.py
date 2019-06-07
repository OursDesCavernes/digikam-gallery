from sqlalchemy import Table

from digikam_gallery.model import db

images = Table('Images', db.metadata, autoload=True, autoload_with=db.engine)


class Image:
    def __init__(self):
        pass

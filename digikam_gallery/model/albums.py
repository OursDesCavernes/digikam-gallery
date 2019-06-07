from sqlalchemy.orm import relationship

from digikam_gallery.model import db


class _Album(db.Model):
    __tablename__ = "Albums"
    album_root = relationship("AlbumRoots", backref="albumRoot")


class _AlbumRoots(db.Model):
    __tablename__ = "AlbumRoots"


def list_albums():
    return ["test"]

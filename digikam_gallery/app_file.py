from io import BytesIO

import jinja2
from PIL import Image
# from configobj import ConfigObj
from flask import Flask, send_file, render_template
from flask_sqlalchemy import SQLAlchemy
from sigal.settings import create_settings
from sigal.writer import THEMES_PATH
from sqlalchemy.orm import relationship
from sqlalchemy.orm.exc import NoResultFound

# print("###")
# config = ConfigObj('/home/thomas/.config/digikamrc')
# config.sections()
# print("###")
#
# if config["Database Settings"]["Database Type"] != "QSQLITE":
#     raise NotImplemented("Unsupported database: " + config["Database Settings"]["Database Type"])

# datadir = config["Database Settings"]["Database Name"]
datadir = "/mnt/Data/thomas/Photos"
sigal_themes = THEMES_PATH

app = Flask(__name__,
            static_url_path="/static",
            static_folder=sigal_themes + "/galleria/static",
            template_folder=sigal_themes + "/galleria/templates")

my_loader = jinja2.ChoiceLoader([
    app.jinja_loader,
    jinja2.FileSystemLoader(sigal_themes + "/default/templates")])
app.jinja_loader = my_loader

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + datadir + "/digikam4.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

db.reflect()


class AlbumRoots(db.Model):
    __tablename__ = "AlbumRoots"


class Albums(db.Model):
    __tablename__ = "Albums"
    r_album_root = relationship(AlbumRoots, primaryjoin='foreign(Albums.albumRoot) == remote(AlbumRoots.id)')


class ImageInformation(db.Model):
    __tablename__ = "ImageInformation"


class ImageMetadata(db.Model):
    __tablename__ = "ImageMetadata"


class Images(db.Model):
    __tablename__ = "Images"
    image_info = relationship(ImageInformation, primaryjoin='foreign(Images.id) == remote(ImageInformation.imageid)')
    image_meta = relationship(ImageMetadata, primaryjoin='foreign(Images.id) == remote(ImageMetadata.imageid)')
    r_album = relationship(Albums, primaryjoin='foreign(Images.album) == remote(Albums.id)')


settings = create_settings(html_language="FR_fr", show_map=False)


class Theme:
    def __init__(self):
        self.url = "/static"


class Album:
    def __init__(self, name):
        self.name = name
        self.title = name
        self.url = "/albums/" + str(id)
        self.author = "Thomas Coquelin"
        self.description = "5 stars"
        self.medias = []

    def add_media(self, media_list):
        self.medias += media_list

    @property
    def thumbnail(self):
        iid = db.session.query(Images.id).filter(Images.id == ImageInformation.imageid).filter(
            ImageInformation.rating == 5).first()
        return "/images/" + str(iid)


class Media:
    def __init__(self, idx):
        self.idx = idx
        self.exif = {}
        self.type = "image"
        try:
            self.exif["iso"], self.exif["exposure"], self.exif["fstop"], self.exif["focal"], self.exif["Make"], \
            self.exif["Model"] = db.session.query(ImageMetadata.sensitivity, ImageMetadata.exposureTime,
                                                  ImageMetadata.aperture, ImageMetadata.focalLength,
                                                  ImageMetadata.make, ImageMetadata.model
                                                  ).filter_by(imageid=idx).one()
        except NoResultFound:
            self.exif = None

    @property
    def url(self):
        return "/images/" + str(self.idx)

    @property
    def big(self):
        return "/images/" + str(self.idx)

    @property
    def thumbnail(self):
        return "/thumbs/" + str(self.idx)


@app.route('/')
def home():
    alb = Album("My photos")
    alb.add_media(
        [Media(idx[0]) for idx in
         db.session.query(Images.id).filter(Images.id == ImageInformation.imageid).filter(
             ImageInformation.rating == 5).distinct().order_by(ImageInformation.creationDate.desc())])
    return render_template("album.html", album=alb, settings=settings, theme=Theme())


@app.route('/images/<image_id>')
def image(image_id):
    image_name, album_id = db.session.query(Images.name, Images.album).filter_by(id=image_id).filter(
        Images.id == ImageInformation.imageid).filter(ImageInformation.rating == 5).one()
    album_relative_path = db.session.query(Albums.relativePath).filter_by(id=album_id).one()[0]
    return send_file(datadir + album_relative_path + "/" + image_name)


@app.route('/thumbs/<image_id>')
def thumb(image_id):
    image_name, album_id = db.session.query(Images.name, Images.album).filter_by(id=image_id).filter(
        Images.id == ImageInformation.imageid).filter(
        ImageInformation.rating == 5).one()
    album_relative_path = db.session.query(Albums.relativePath).filter_by(id=album_id).one()[0]
    im = Image.open(datadir + album_relative_path + "/" + image_name)
    im.thumbnail([400, 300])
    iof = BytesIO()
    im.save(iof, format='JPEG')
    iof.seek(0)
    return send_file(iof, mimetype='image/jpeg')


@app.route('/favicon.ico')
def favicon():
    return send_file(sigal_themes + "/galleria/static/img/photo.png")


@app.errorhandler(NoResultFound)
def handle_bad_request(_):
    return 'not found!', 404


def run():
    app.run("0.0.0.0", 5000, True)


if __name__ == '__main__':
    run()

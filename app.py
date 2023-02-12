#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_migrate import Migrate 
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate=Migrate(app,db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talent=db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))

    def __repr__(self):
        return f'<Venue {self.id} {self.name}>'

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue=db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))

    def __repr__(self):
        return f'<Artist {self.id} {self.name}>'

class Show(db.Model):
    __tablename__ = 'Show'
  
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)    

    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)   
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)

    def __repr__(self):
        return f'<Show {self.id} {self.start_time   }>'
   
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues , num_upcoming_shows aggregated based on number of upcoming shows per venue
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  try:
    venues=Venue.query.order_by(Venue.city).all()
    data={}
    venue_list=[]
    for venue in venues:
      # Reset num_upcoming_shows =0
      num_upcoming_shows=0
      # Get all shows for given venue
      shows=Show.query.get(venue_id=venue.id)
      for show in shows:
        if show.start_time > datetime.now():
          num_upcoming_shows+=1
          venue_list.append ["id": venue.id,"name": venue.name,"num_upcoming_shows": num_upcoming_shows]
        else:
          num_upcoming_shows=0
          venue_list.append ["id": venue.id,"name": venue.name,"num_upcoming_shows": num_upcoming_shows]  
      data.update({"city":venue.city,"state":venue.state,"venues":venue_list})
    return render_template('pages/venues.html', areas=data)
  except:
    flash("Error")    

#  Displays list of shows at /shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  try:
    shows=Show.query.all()
    values=[]
    for show in shows:
      values.append({
        "id":show.id,
        "name":show.name
      })
    return render_template('pages/shows.html', shows=shows)  
  except:
    flash("Error occurred")   

 #  Artists
#  ----------------------------------------------------------------

@app.route('/artists')
def artists():
  try:
    artists = Artist.query.order_by(Artist.name).all()  
    values = []
    for artist in artists:
          values.append({
              "id": artist.id,
              "name": artist.name
          })
    return render_template('pages/artists.html', artists=values)
  except:
    flash("Error Occurred!")    

# Implement search on venues with partial string search. Ensure it is case-insensitive
#  ----------------------------------------------------------------

@app.route('/venues/search', methods=['POST'])
def search_venues():
  try:
    search_term = request.form.get('search_term')
    venues = Venue.query.filter_by(Venue.name.like('%' + search_term + '%')).all()
    return render_template('pages/search_venues.html', results=venues)
  except:
    flash("Error Occurred!")  

#Shows the venue page with the given venue_id
#  ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  try:
    venue=Venue.query.get(venue_id)
    return render_template('pages/show_venue.html', venue=venue)  
  except:    
    flash("Error Occured")

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

# Add new Venue
#  ----------------------------------------------------------------
@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    try:
        form = VenueForm()
        name=request.form.get('name')
        city=request.form.get('city')
        state=request.form.get('state')
        address=request.form.get('address')
        phone=request.form.get('name')
        genres=request.form.get('genres')
        facebook_link=request.form.get('facebook_link')
        image_link=request.form.get('image_link')
        website_link=request.form.get('website_link')
        seeking_talent=request.form.get('seeking_talent')
        seeking_description=request.form.get('seeking_description')
        new_venue = Venue(name=name,city=city,state=state,address=address,phone=phone,genres=genres,facebook_link=facebook_link,
        image_link=image_link,website_link=website_link,seeking_talent=seeking_talent,seeking_description=seeking_description)
        db.session.add(new_venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
        return render_template('pages/home.html')
    except:
        db.session.rollback()
        flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    finally:
        db.session.close()
        
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:

    return None
  except:
    flash("Error Occurred!") 

#Implement search on artists with partial string search. Ensure it is case-insensitive.
#  ---------------------------------------------------------------

@app.route('/artists/search', methods=['POST'])
def search_artists():
  try:
    search_term = request.form.get('search_term')
    artists = Artist.query.filter(Artist.name.like('%' + search_term + '%')).all()
    return render_template('pages/search_artists.html', results=artists, search_term=request.form.get('search_term', ''))
  except:
    flash("Error Occurred!")  

# Shows the artist page with the given artist_id
#  ----------------------------------------------------------------

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  try:
    artist=Artist.query.get(artist_id)
    return render_template('pages/show_venue.html', artist=artist)  
  except:    
    flash("Error Occured")

#  Update
#  ----------------------------------------------------------------

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  try:
    form = ArtistForm()
    artist=Artist.query.get(artist_id)
    artist={
      "id": artist_id,
      "name": artist.name,
      "genres": artist.genres,
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "website": artist.website,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_description,
      "image_link": artist.image_link
    }
    return render_template('forms/edit_artist.html', form=form, artist=artist)
  except:
    flash("Error Occurred")
  
# Take values from the form submitted, and update existing artist record with ID <artist_id> using the new attributes
#  ----------------------------------------------------------------

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  try:
    form = ArtistForm()
    artist=Artist.query.get(artist_id)
    name=request.form.get('name')
    city=request.form.get('city')
    state=request.form.get('state')
    phone=request.form.get('phone')
    genres=request.form.get('genres')
    facebook_link=request.form.get('facebook_link')
    image_link=request.form.get('image_link')
    website_link=request.form.get('website_link')
    seeking_venue=request.form.get('seeking_venue')
    seeking_description=request.form.get('seeking_description')
    update_artist = Artist(name=name,city=city,state=state,phone=phone,genres=genres,facebook_link=facebook_link,image_link=image_link,
          website_link=website_link,seeking_venue=seeking_venue,seeking_description=seeking_description)
    db.session.add(update_artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return redirect(url_for('show_artist', artist_id=artist_id))
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  finally:
    db.session.close()
  
# Populate form with values from venue with ID <venue_id>
#  ----------------------------------------------------------------

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  return render_template('forms/edit_venue.html', form=form, venue=venue)

# Take values from the form submitted, and update existing venue record with ID <venue_id> using the new attributes
#  ----------------------------------------------------------------

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

# Add new artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    try:
        form = ArtistForm()
        name=request.form.get('name')
        city=request.form.get('city')
        state=request.form.get('state')
        phone=request.form.get('phone')
        genres=request.form.get('genres')
        facebook_link=request.form.get('facebook_link')
        image_link=request.form.get('image_link')
        website_link=request.form.get('website_link')
        seeking_venue=request.form.get('seeking_venue')
        seeking_description=request.form.get('seeking_description')
        new_artist = Artist(name=name,city=city,state=state,phone=phone,genres=genres,facebook_link=facebook_link,image_link=image_link,
          website_link=website_link,seeking_venue=seeking_venue,seeking_description=seeking_description)
        db.session.add(new_artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
        return render_template('pages/home.html')
    except:
        db.session.rollback()
    finally:
        db.session.close()     

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

# Called to create new shows in the db, upon submitting new show listing form
#  ----------------------------------------------------------------

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  try:
    form = ShowForm()
    artist_id=request.form.get('artist_id')
    venue_id=request.form.get('venue_id')
    start_time=request.form.get('start_time')
    new_show= Show(artist_id=artist_id,venue_id=venue_id,start_time=start_time)
    db.session.add(new_show)
    db.session.commit()
    flash('Show was successfully listed!')
    return render_template('pages/home.html')
  except:
    db.session.rollback()
  finally:
    db.session.close()


  
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''

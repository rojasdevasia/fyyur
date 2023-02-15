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
    shows = db.relationship('Show', backref='venue', lazy='joined', cascade="all, delete")

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
    shows = db.relationship('Show', backref='artist', lazy='joined', cascade="all, delete")

    def __repr__(self):
        return f'<Artist {self.id} {self.name}>'

class Show(db.Model):
    __tablename__ = 'Show'
  
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)    

    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)   
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)

    def __repr__(self):
        return f'<Show {self.id} {self.start_time}>'
   
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
  locals = []
  venues = Venue.query.all()
  places = Venue.query.distinct(Venue.city, Venue.state).all()
  print(places)
  for place in places:
      print(place)
      tmp_venues = []
      for venue in venues:
          if venue.city == place.city and venue.state == place.state:
              num_shows = 0
              for show in venue.shows:
                  if show.start_time > datetime.now():
                      num_shows += 1
              tmp_venues.append({
                  'id': venue.id,
                  "name":venue.name,
                  "num_upcoming_shows":num_shows
              })
      locals.append({
          'city': place.city,
          'state': place.state,
          'venues':tmp_venues
      })
  return render_template('pages/venues.html', areas=locals) 

#  Displays list of shows at /shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  try:
    shows=Show.query.all()
    # data=[]
    show_details=[]
    for show in shows:
      artist=Artist.query.filter_by(id=show.artist_id)
      venue=Venue.query.filter_by(id=show.venue_id)
      print(artist[0])
      print(venue[0])
      show_details.append({"venue_id":show.venue_id,
      "venue_name":venue[0].name,
      "artist_id":artist[0].id,
      "artist_name":artist[0].name,
      "artist_image_link":artist[0].image_link,
      "start_time":show.start_time.strftime("%m/%d/%Y, %H:%M:%S")})
      print(show_details)
    # data.append(show_details) 
    # print(data) 
    return render_template('pages/shows.html', shows=show_details)  
  except Exception as e: 
    print(e)
    flash("Error occurred")   

 #  Artists
#  ----------------------------------------------------------------

@app.route('/artists')
def artists():
  try:
    artists = Artist.query.all()  
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
    data=[]
    response=[]
    num_upcoming_shows=0
    search_term = request.form.get('search_term')
    venues = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()
    for venue in venues:
      shows=Show.query.filter_by(venue_id=Venue.id)
      for show in shows:
        if show.start_time > datetime.now():
          num_upcoming_shows+=1
          data.append({
            "id":venue.id,
            "name":venue.name,
            "num_upcoming_shows":num_upcoming_shows
          })  
    response={
      "count": len(venues),
      "data": data
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))
  except Exception as e:
    print(e)
  # try:
  #   venue_list=[]
  #   response=[]
  #   num_upcoming_show=0
  #   search_term = request.form.get('search_term')
  #   print("Search Term is:"+search_term)
  #   venues = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()
  #   # category = Category.query.filter(Category.title.like(category_param_value + "%")).all()
  #   for venue in venues:
  #     shows=Show.query.filter_by(venue_id=venue.id).all()
  #     if len(shows)> 0:
  #       for show in shows:
  #         if show.start_time > datetime.now():
  #           num_upcoming_show +=1
  #           venue_list.append({"id":venue.id,"name":venue.name,"num_upcoming_show":num_upcoming_show})
  #         else:
  #           num_upcoming_show =0
  #           venue_list.append({"id":venue.id,"name":venue.name,"num_upcoming_show":num_upcoming_show})
  #     else:
  #        venue_list.append({"id":venue.id,"name":venue.name,"num_upcoming_show":0})   
  #     response.append({"count":len(venues),"data":venue_list})  
  #     print(response)
  #   return render_template('pages/search_venues.html', results=response)
  # except Exception as e:
  #   print(e)
  #   flash("Error Occurred!")  

#Shows the venue page with the given venue_id
#  ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  try:
    data=[]
    past_shows=[]
    upcoming_shows=[]

    venue=Venue.query.get(venue_id)
    shows=Show.query.filter_by(venue_id=venue_id)
    for show in shows:
      print(show)
      artists=Artist.query.filter_by(id=show.artist_id)
      for artist in artists:
        print(artist)
        if show.start_time > datetime.now():
          upcoming_shows.append({
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
            })
        else:
          past_shows.append({
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
        })
    data={
      "id": venue.id,
      "name": venue.name,
      "genres": venue.genres,
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website": venue.website_link,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link,
      "past_shows":past_shows,
      "upcoming_shows":upcoming_shows,
      "past_shows_count":len(past_shows),
      "upcoming_shows_count":len(upcoming_shows)
    }
    print(data)
    return render_template('pages/show_venue.html', venue=data)  
  except Exception as e:
    print(e)    
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
        # form = VenueForm()
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
    except Exception as e:
        db.session.rollback()
        flash('An error occurred. Venue could not be listed.')
        print(e)
    finally:
        db.session.close()

# Delete Venue ,Cascade       
        
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()

#Implement search on artists with partial string search. Ensure it is case-insensitive.
#  ---------------------------------------------------------------

@app.route('/artists/search', methods=['POST'])
def search_artists():
  try:
    response=[]
    data=[]
    num_upcoming_shows=0
    search_term = request.form.get('search_term')
    print(search_term)
    artists = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()
    for artist in artists:
      shows=Show.query.filter_by(artist_id=Artist.id)
      for show in shows:
        if show.start_time > datetime.now():
          num_upcoming_shows +=1
          data.append({
            "id":artist.id,
            "name":artist.name,
            "num_upcoming_shows":num_upcoming_shows
          })
       
    response.append({
      "count":len(artists),
      "data":data
    })
    print(response)    
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))
  except Exception as e:
    flash("Error Occurred!")  
    print(e)

# Shows the artist page with the given artist_id
#  ----------------------------------------------------------------

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  try:
    artist=Artist.query.get(artist_id)
    print(artist)
    shows=Show.query.filter_by(artist_id=artist_id)
    print(shows)

    upcoming_shows=[]
    past_shows=[]

    for show in shows:
      # Get Venue for each show
      venues=Venue.query.filter_by(id=show.venue_id)
      print(venues)
      for venue in venues:
        if show.start_time > datetime.now():
          upcoming_shows.append({
            "venue_id": id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
            })
        else:
          past_shows.append({
            "venue_id": id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
            })    
      data={
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website_link,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
      }      
    data = list(filter(lambda d: d['id'] == artist_id, [data]))[0]
    return render_template('pages/show_artist.html', artist=data)
  except Exception as e:    
    flash("Error Occured")
    print(e)

#  Update
#  ----------------------------------------------------------------

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  print("Entering edit artist")
  form = ArtistForm()
  print(artist_id)
  artist_to_edit=Artist.query.get(artist_id)
  artist={
    "id": artist_to_edit.id,
    "name": artist_to_edit.name,
    "genres": artist_to_edit.genres,
    "city": artist_to_edit.city,
    "state": artist_to_edit.state,
    "phone": artist_to_edit.phone,
    "website": artist_to_edit.website_link,
    "facebook_link": artist_to_edit.facebook_link,
    "seeking_venue": artist_to_edit.seeking_venue,
    "seeking_description": artist_to_edit.seeking_description,
    "image_link": artist_to_edit.image_link
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

  
# Take values from the form submitted, and update existing artist record with ID <artist_id> using the new attributes
#  ----------------------------------------------------------------

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  try:
    # form = ArtistForm()
    artist=Artist.query.get(artist_id)
    print(artist_id)
    artist.name=request.form.get('name')
    artist.city=request.form.get('city')
    artist.state=request.form.get('state')
    artist.phone=request.form.get('phone')
    artist.genres=request.form.get('genres')
    artist.facebook_link=request.form.get('facebook_link')
    artist.image_link=request.form.get('image_link')
    artist.website_link=request.form.get('website_link')
    artist.seeking_venue=request.form.get('seeking_venue')
    artist.seeking_description=request.form.get('seeking_description')
    update_artist = Artist(name=artist.name,city=artist.city,state=artist.state,phone=artist.phone,genres=artist.genres,facebook_link=artist.facebook_link,image_link=artist.image_link,
          website_link=artist.website_link,seeking_venue=artist.seeking_venue,seeking_description=artist.seeking_description)
    db.session.add(update_artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return redirect(url_for('show_artist', artist_id=artist_id))
  except Exception as e:
    db.session.rollback()
    flash('An error occurred. Venue could not be listed.')
    print(e)
  finally:
    db.session.close()
  
# Populate form with values from venue with ID <venue_id>
#  ----------------------------------------------------------------

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue_to_edit=Venue.query.get(venue_id)
  venue={
    "id": venue_to_edit.id,
    "name": venue_to_edit.name,
    "genres": venue_to_edit.genres,
    "address": venue_to_edit.address,
    "city": venue_to_edit.city,
    "state": venue_to_edit.state,
    "phone": venue_to_edit.phone,
    "website": venue_to_edit.website_link,
    "facebook_link": venue_to_edit.facebook_link,
    "seeking_talent": venue_to_edit.seeking_talent,
    "seeking_description": venue_to_edit.seeking_description,
    "image_link": venue_to_edit.image_link
  }
  return render_template('forms/edit_venue.html', form=form, venue=venue)

# Take values from the form submitted, and update existing venue record with ID <venue_id> using the new attributes
#  ----------------------------------------------------------------

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  try:
    venue=Venue.query.get(venue_id)
    venue.name=request.form.get('name')
    venue.city=request.form.get('city')
    venue.state=request.form.get('state')
    venue.phone=request.form.get('phone')
    venue.genres=request.form.get('genres')
    venue.facebook_link=request.form.get('facebook_link')
    venue.image_link=request.form.get('image_link')
    venue.website_link=request.form.get('website_link')
    venue.seeking_venue=request.form.get('seeking_venue')
    venue.seeking_description=request.form.get('seeking_description')
    update_venue = Artist(name=venue.name,city=venue.city,state=venue.state,phone=venue.phone,genres=venue.genres,facebook_link=venue.facebook_link,image_link=venue.image_link,
            website_link=venue.website_link,seeking_venue=venue.seeking_venue,seeking_description=venue.seeking_description)
    db.session.add(update_venue)
    return redirect(url_for('show_venue', venue_id=venue_id))
  except Exception as e:
    db.session.rollback()
    print(e)
  finally:
    db.session.close()  

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
    except Exception as e:
        db.session.rollback()
        print(e)
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
    # form = ShowForm()
    artist_id=request.form.get('artist_id')
    venue_id=request.form.get('venue_id')
    start_time=request.form.get('start_time')
    new_show= Show(artist_id=artist_id,venue_id=venue_id,start_time=start_time)
    db.session.add(new_show)
    db.session.commit()
    flash('Show was successfully listed!')
    return render_template('pages/home.html')
  except Exception as e: 
    print(e)
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

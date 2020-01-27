#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
from datetime import datetime

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

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
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.Boolean)
    shows = db.relationship('Show', backref='Venue', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.Boolean)
    shows = db.relationship('Show', backref='artist', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
   
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  venues=Venue.query.group_by(Venue.id ,Venue.city, Venue.state).all()
  areas=[]
  current_city,current_state = '',''
  for venue in venues:
    current_time = datetime.now().strftime('%Y-%M-%D %H:%M:%S')
    upcoming_shows = venue.shows.filter(Show.start_time > current_time).all()
    if Venue.city != current_city or Venue.state != current_state :
      current_city , current_state = Venue.city , Venue.state
      areas.append({
       "city": Venue.city,
       "state": Venue.state,
       "venues": [{
         "id": Venue.id,
         "name": Venue.name,
         "num_upcoming_shows": len(upcoming_shows)
       }]
     })
    else:
     areas[-1]['venues'].append({
       "id": Venue.id,
       "name": Venue.name,
       "num_upcoming_shows": len(upcoming_shows)  
      })
  return render_template('pages/venues.html', areas=areas)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  term = request.form.get('search_term')
  search = '%{}%'.format(term.lower())
  result = Venue.query.filter_by().all()
  response = {'count': len(result), 'data': result}
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  current_time = datetime.now().strftime('%Y-%M-%D %H:%M:%S')
  venue.past_shows = venue.shows.filter(Show.start_time < current_time).all()
  venue.upcoming_shows = venue.shows.filter(Show.start_time > current_time).all()
  venue.past_shows_count = len(venue.past_shows)
  venue.upcoming_shows_count = len(venue.upcoming_shows)

  return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm()
  error = False
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    image_link = request.form['image_link']
    genres = request.form['genres']
    facebook = request.form['facebook_link']
    website = request.form['website']
    seeking_talent = request.form['seeking_talent']
    seeking_description = request.form['seeking_description']

    newVenue = Venue(name=name, city=city, state=state, address=address, phone=phone, image_link=image_link, genres=genres, facebook_link=facebook, website=website,
                  seeking_talent=seeking_talent, seeking_description=seeking_description)
    db.session.add(newVenue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue ' + name + ' could not be listed.')
    abort(500)
  else:
    return render_template('pages/home.html')
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  
  

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try: 
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
    flash('Successfully deleted!')
  except:
    db.session.rollback()
    error = True
    print(sys.exec_info())
  finally:
    db.session.close()
  if error:
    abort(500)
  else: 
    return jsonify({'success' : True})

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  #####Done, show_venue.html is edited 
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.order_by('name').all()
  areas=[]
  for artist in artists:
    areas.append({
       "city": artist.city,
       "state": artist.state,
       "artists": [{
         "id": artist.id,
         "name": artist.name,
         
       }]
     })

  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  term = request.form.get('search_term')
  search = '%{}%'.format(term.lower())
  result = Artist.query.filter_by().all()
  response = {'count': len(result), 'data': result}

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  artist = Artist.query.get(artist_id)
  current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  
  #s1 = current_time
  #s2 = start_time
  #d1 = datetime.strptime(s1, '%Y-%m-%d %H:%M:%S')
  #d2 = datetime.strptime(s2, '%Y-%m-%d %H:%M:%S')
  ##start_time = datetime.strptime(Show.start_time, '%Y-%M-%D %H:%M:%S')
  #upcoming_shows = []
  
  #if d2 > d1:
    #all_upcoming = upcoming_shows.append(Show)
    #upcoming_shows_count = len(all_upcoming)
  return render_template('pages/show_artist.html', artist=artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  form.populate_obj(artist)
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    image_link = request.form['image_link']
    genres = request.form['genres']
    facebook = request.form['facebook_link']
    website = request.form['website']
    seeking_venue = request.form['seeking_venue']
    Artist = Artist(name=name, city=city, state=state, phone=phone, image_link=image_link, genres=genres, facebook_link=facebook, website=website, seeking_venue=seeking_venue)
    
    return redirect(url_for('show_artist', artist_id=artist_id))
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Artist ' + name + ' could not be edited.')
    abort(500)
  else:
    flash('Artist ' + request.form['name'] + ' was successfully updated!')
    return render_template('pages/home.html')  
 

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  form.populate_obj(venue)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    image_link = request.form['image_link']
    genres = request.form['genres']
    facebook = request.form['facebook_link']
    website = request.form['website']
    seeking_talent = request.form['seeking_talent']
    venue = Venue(name=name, city=city, state=state, phone=phone, image_link=image_link, genres=genres, facebook_link=facebook, website=website, seeking_venue=seeking_venue)
    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue ' + name + ' could not be edited.')
    abort(500)
  else:
    return render_template('pages/home.html')
    flash('Venue ' + request.form['name'] + ' was successfully updated!')
  
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm()
  error = False
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    image_link = request.form['image_link']
    genres = request.form['genres']
    facebook = request.form['facebook_link']
    website = request.form['website']
    seeking_venue = request.form['seeking_venue']
    newArtist = Artist(name=name, city=city, state=state, phone=phone, image_link=image_link, genres=genres, facebook_link=facebook, website=website, seeking_venue=seeking_venue)
    db.session.add(newArtist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Artist ' + name + ' could not be listed.')
    abort(500)
  else:
    
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shows=Venue.query.group_by(Venue.id, Venue.city, Venue.state).all()
  areas=[]
  current_city,current_state = '',''
  for show in shows:
    current_time = datetime.now().strftime('%Y-%M-%D %H:%M:%S')
    upcoming_shows = []
    if Show.start_time > current_time:
      all_upcoming = upcoming_shows.append(Show)
      upcoming_shows_count = len(all_upcoming)
    else:
      past_shows = []
      all_past = past_shows.append(Show)
      past_shows_count = len(all_past)

    if Venue.city != current_city or Venue.state != current_state :
      current_city , current_state = Venue.city , Venue.state
      areas.append({
       "city": Venue.city,
       "state": Venue.state,
       "venues": [{
         "id": Venue.id,
         "name": Venue.name,
         "num_upcoming_shows": len(upcoming_shows)
       }]
     })
    else:
     area[-1]['venues'].append({
       "id": Venue.id,
       "name": Venue.name,
       "num_upcoming_shows": len(upcoming_shows)  
      })
  
  return render_template('pages/shows.html', shows=shows)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm()
  error = False
  try:
    venue_name = request.form['venue_name']
    artist_name = request.form['artist_name']
    artist_image_link = request.form['artist_image_link']
    start_time = request.form['start_time']
    newShow = Show(venue_name=venue_name, artist_name=artist_name, artist_image_link=artist_image_link, start_time=start_time)
    db.session.add(newShow)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Show ' + name + ' could not be listed.')
    abort(500)
  else:
    
    flash('Show was successfully listed!')
  

  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

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

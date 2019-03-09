#!/usr/bin/python
from flask import Flask, render_template, request, redirect, url_for, \
    flash, jsonify
from flask import session as login_session
from flask import make_response

# importing SqlAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, AlbumDB, User
import random
import string
import httplib2
import json
import requests

# import oauth client

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from oauth2client.client import AccessTokenCredentials

#app configuration including secret key

app = Flask(__name__)
app.secret_key = 'super_secret'

# google client secret
secret_file = json.loads(open('client_secrets.json', 'r').read())
CLIENT_ID = secret_file['web']['client_id']
APPLICATION_NAME = 'AlbumCatalog'

# Binds the engine to the metadata of the Base class so
# that the declaratives can be accessed through a DBSession instance

engine = create_engine('postgresql://catalog:password@localhost/catalog')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# checking current loggedin user

def check_user():
    email = login_session['email']
    return session.query(User).filter_by(email=email).one_or_none()


# check admin user details using a filter to find a specific
# email while also ensuring there is only one user at a time

def check_admin():
    return session.query(User).filter_by(
        email='marcus.jenkins2013@gmail.com').one_or_none()


# Add a new user into database

def createUser():
    name = login_session['name']
    email = login_session['email']
    url = login_session['img']
    provider = login_session['provider']
    newUser = User(name=name, email=email, image=url, provider=provider)
    session.add(newUser)
    session.commit()


def new_state():
    state = ''.join(random.choice(string.ascii_uppercase +
                    string.digits) for x in xrange(32))
    login_session['state'] = state
    return state


def queryAllAlbums():
    return session.query(AlbumDB).all()

# All App Routes

# This route is for the main page of the application
# or the home page

@app.route('/')
@app.route('/albums/')
def showAlbums():
    albums = queryAllAlbums()
    state = new_state()
    return render_template('main.html', albums=albums, currentPage='main',
                           state=state, login_session=login_session)


# To add a new album.. GETs info user and uses the POST method
# to post all new Information

@app.route('/albums/new/', methods=['GET', 'POST'])
def newAlbum():
    if request.method == 'POST':

        # check if user is logged in or not

        if 'provider' in login_session and \
                    login_session['provider'] != 'null':
            albumTitle = request.form['albumTitle']
            artist = request.form['artist']
            coverartUrl = request.form['coverart']
            description = request.form['albumDescription']
            description = description.replace('\n', '<br>')
            genre = request.form['genre']
            user_id = check_user().id

            if albumTitle and artist and coverartUrl and description \
                    and genre:
                newAlbum = AlbumDB(
                    albumTitle=albumTitle,
                    artist=artist,
                    coverartUrl=coverartUrl,
                    description=description,
                    genre=genre,
                    user_id=user_id,
                    )
                session.add(newAlbum)
                session.commit()
                return redirect(url_for('showAlbums'))
            else:
                state = new_state()
                return render_template(
                    'newItem.html',
                    currentPage='new',
                    title='Add New Album',
                    errorMsg='All Fields are Required!',
                    state=state,
                    login_session=login_session,
                    )
        else:
            state = new_state()
            albums = queryAllAlbums()
            return render_template(
                'main.html',
                albums=albums,
                currentPage='main',
                state=state,
                login_session=login_session,
                errorMsg='Please Login first to Add Album!',
                )
    elif 'provider' in login_session and login_session['provider'] \
            != 'null':
        state = new_state()
        return render_template('newItem.html', currentPage='new',
                               title='Add New Album', state=state,
                               login_session=login_session)
    else:
        state = new_state()
        albums = queryAllAlbums()
        return render_template(
            'main.html',
            albums=albums,
            currentPage='main',
            state=state,
            login_session=login_session,
            errorMsg='Please Login first to Add Album!',
            )


# To show albums of different genres it searches through the database
# and filters out searches by genre

@app.route('/albums/genre/<string:genre>/')
def sortAlbums(genre):
    albums = session.query(AlbumDB).filter_by(genre=genre).all()
    state = new_state()
    return render_template(
        'main.html',
        albums=albums,
        currentPage='main',
        error='Sorry! No Album in Database With This Genre :(',
        state=state,
        login_session=login_session)


# shows all album detail

@app.route('/albums/genre/<string:genre>/<int:albumId>/')
def albumDetail(genre, albumId):
    album = session.query(AlbumDB).filter_by(id=albumId,
                                           genre=genre).first()
    state = new_state()
    if album:
        return render_template('itemDetail.html', album=album,
                               currentPage='detail', state=state,
                               login_session=login_session)
    else:
        return render_template('main.html', currentPage='main',
                               error="""No Album Found with this Genre
                               and Album Id""",
                               state=state,
                               login_session=login_session)


# Edit album detail

@app.route('/albums/genre/<string:genre>/<int:albumId>/edit/',
           methods=['GET', 'POST'])
def editAlbumDetails(genre, albumId):
    album = session.query(AlbumDB).filter_by(id=albumId,
                                           genre=genre).first()
    if request.method == 'POST':

        # checks if user is logged in or if they aren't

        if 'provider' in login_session and login_session['provider'] \
                != 'null':
            albumTitle = request.form['albumTitle']
            artist = request.form['artist']
            coverartUrl = request.form['coverart']
            description = request.form['albumDescription']
            description = description.replace('\n', '<br>')
            user_id = check_user().id
            admin_id = check_admin().id

            # checks if the album owner is the logged in user or the admin
            # or not

            if album.user_id == user_id or user_id == admin_id:
                if albumTitle and artist and coverartUrl and description \
                        and genre:
                    album.albumTitle = albumTitle
                    album.artist= artist
                    album.coverartUrl = coverartUrl
                    description = description.replace('\n', '<br>')
                    album.description = description
                    album.genre = genre
                    session.add(album)
                    session.commit()
                    return redirect(url_for('albumDetail',
                                    genre=album.genre,
                                    albumId=album.id))
                #makes sure all fields are filled out
                else:
                    state = new_state()
                    return render_template(
                        'editItem.html',
                        currentPage='edit',
                        title='Edit Album Details',
                        album=album,
                        state=state,
                        login_session=login_session,
                        errorMsg='All Fields are Required!',
                        )
            # displays message if the wrong user attempts to edit album
            else:
                state = new_state()
                return render_template(
                    'itemDetail.html',
                    album=album,
                    currentPage='detail',
                    state=state,
                    login_session=login_session,
                    errorMsg='Sorry! The Owner can only edit album Details!')
        else:
            state = new_state()
            return render_template(
                'itemDetail.html',
                album=album,
                currentPage='detail',
                state=state,
                login_session=login_session,
                errorMsg='Please Login to Edit the Album Details!',
                )
    elif album:
        state = new_state()
        if 'provider' in login_session and login_session['provider'] \
                != 'null':
            user_id = check_user().id
            admin_id = check_admin().id
            if user_id == album.user_id or user_id == admin_id:
                album.description = album.description.replace('<br>', '\n')
                return render_template(
                    'editItem.html',
                    currentPage='edit',
                    title='Edit Album Details',
                    album=album,
                    state=state,
                    login_session=login_session,
                    )
            else:
                return render_template(
                    'itemDetail.html',
                    album=album,
                    currentPage='detail',
                    state=state,
                    login_session=login_session,
                    errorMsg='Sorry! The Owner can only edit Album Details!')
        else:
            return render_template(
                'itemDetail.html',
                album=album,
                currentPage='detail',
                state=state,
                login_session=login_session,
                errorMsg='Please Login to Edit the Album Details!',
                )
    else:
        state = new_state()
        return render_template('main.html', currentPage='main',
                               error="""Error Editing Album! No album Found
                               with this Genre and Album Id :(""",
                               state=state,
                               login_session=login_session)


# To delete albums

@app.route('/albums/genre/<string:genre>/<int:albumId>/delete/')
def deleteAlbum(genre, albumId):
    album = session.query(AlbumDB).filter_by(genre=genre,
                                           id=albumId).first()
    state = new_state()
    if album:

        # checks if user is logged in or not

        if 'provider' in login_session and login_session['provider'] \
                != 'null':
            user_id = check_user().id
            admin_id = check_admin().id
            if user_id == album.user_id or user_id == admin_id:
                session.delete(album)
                session.commit()
                return redirect(url_for('showAlbums'))
            else:
                return render_template(
                    'itemDetail.html',
                    album=album,
                    currentPage='detail',
                    state=state,
                    login_session=login_session,
                    errorMsg='Sorry! Only the Owner Can delete the album'
                    )
        else:
            return render_template(
                'itemDetail.html',
                album=album,
                currentPage='detail',
                state=state,
                login_session=login_session,
                errorMsg='Please Login to Delete the Album!',
                )
    else:
        return render_template('main.html', currentPage='main',
                               error="""Error Deleting Album! No Album Found
                               with this Genre and Album Id :(""",
                               state=state,
                               login_session=login_session)

# JSON endpoints

@app.route('/albums.json/')
def albumsJSON():
    albums = session.query(AlbumDB).all()
    return jsonify(Albums=[album.serialize for album in albums])


@app.route('/albums/genre/<string:genre>.json/')
def albumGenreJSON(genre):
    albums = session.query(AlbumDB).filter_by(genre=genre).all()
    return jsonify(Albums=[album.serialize for album in albums])


@app.route('/albums/genre/<string:genre>/<int:albumId>.json/')
def albumJSON(genre, albumId):
    album = session.query(AlbumDB).filter_by(genre=genre,
                                           id=albumId).first()
    return jsonify(Album=album.serialize)


# The google signin route

@app.route('/gconnect', methods=['POST'])
def gConnect():
    if request.args.get('state') != login_session['state']:
        response.make_response(json.dumps('Invalid State paramenter'),
                               401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Gets authorization code

    code = request.data
    try:

        # Upgrade the authorization code into a credentials object

        oauth_flow = flow_from_clientsecrets('client_secrets.json',
                                             scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps("""Failed to upgrade the
        authorisation code"""),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Validate access token to login in using google credentials

    access_token = credentials.access_token
    url = \
        'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' \
        % access_token
    header = httplib2.Http()
    result = json.loads(header.request(url, 'GET')[1])

    # If there was an error in the access token info then abort

    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.

    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps(
                            """Token's user ID does not
                            match given user ID."""),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check validity of access token for this app

    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps(
            """Token's client ID
            does not match app's."""),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = \
            make_response(json.dumps('Current user is already connected.'),
                          200)
        response.headers['Content-Type'] = 'application/json'
        return response

    login_session['credentials'] = access_token
    login_session['id'] = gplus_id

    # Gets user info

    userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    # Adds provider to login session

    login_session['name'] = data['name']
    login_session['img'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'
    if not check_user():
        createUser()
    return jsonify(name=login_session['name'],
                   email=login_session['email'],
                   img=login_session['img'])

# logout user

@app.route('/logout', methods=['post'])
def logout():

# disconnect the user based on what provider they use

    if login_session.get('provider') == 'google':
        return gdisconnect()
    else:
        response = make_response(json.dumps({'state': 'notConnected'}),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['credentials']

    # Only disconnect a connected user.

    if access_token is None:
        response = make_response(json.dumps({'state': 'notConnected'}),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' \
        % access_token
    header = httplib2.Http()
    result = header.request(url, 'GET')[0]

    if result['status'] == '200':

        # Resets the user's session

        del login_session['credentials']
        del login_session['id']
        del login_session['name']
        del login_session['email']
        del login_session['img']
        login_session['provider'] = 'null'
        response = make_response(json.dumps({'state': 'loggedOut'}),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:

        # if given token is invalid, unable to revoke token

        response = make_response(json.dumps({'state': 'errorRevoke'}),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

# Run the app on the localhost port of 5000        

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

# Workout Recommendations

### How to start django
This can be started using Docker.

First, make sure you have Docker and docker-compose (usually comes with the docker installation for Mac) installed and running.

Then run the command 
```
docker-compose up
```
This should start the app running on port 8000 on your computer.

To stop it running just type Ctrl+C in the terminal you started it in and type 
```
docker-compose down
```

### Updating the database after creating a new Model or updating one
Updates in django are done through things called migrations. These can do bulk updates on data in a database or perform CRUD operations on tables in a database.
To update the database, you will have to first execute into the docker container.
First do:
```
docker ps
```
This will list all the running docker containers.
Copy the container ID of the container with image name some thing like `workout_recommendations_web`.

Then run:
```
docker exec -ti <copied container ID> bash
```
This lets you go into the docker container and run commands in it.

Now to run the migrations run the following commands:
```
python manage.py makemigrations
python manage.py migrate
```
Your database should now be updated.


### Exposing a local port
To expose a local port you will need ngrok installed. You can install ngrok using homebrew with the command:
```
brew install --cask ngrok
```

After this you can just expose a port using the command:
```
ngrok http <port to expose>
```

This redirects all requests to a public url (this should be shown on terminal) to your port.

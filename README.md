# CSDS-395-Senior-Project

App template created with help from [this tutorial by Miguel Grinberg!](https://blog.miguelgrinberg.com/post/create-a-react-flask-project-in-2025) 

However, for your convenience, I will outline below how to start the application:

**1: Clone the repo**

**2: Make sure you have Python and Node.js installed** 

To check, you can open a terminal and enter

`python --version`

and 

`node --version`

If you get a version number for both of those, you should be fine. If not, you will need to install them. 

**3: Run the frontend**

In the terminal, enter the react app using

`cd baseball_app`

Then, do

`npm install`

`npm run dev`

which will launch the fontend on localhost. You can click the url to open in a browser, or just press o + enter and it will open. Pressing h + enter will show you the different runtime options. 

**4: Run the backend**

In the terminal, enter the python virtual environment using

`cd baseball_app`

`cd api`

To avoid pushing over a thousand files to git, I marked them in .gitignore and instead you will be creating your own python virtual environment in this folder. There should currently be only 2 files in the api folder, which I created manually. 

To create the environment, type into the terminal

`python -m venv venv`


And start the python environment with

`venv\Scripts\activate`

^That worked for me because I am on windows, but first I had to change some developer settings because I guess windows won't run a script by default. If it doesn't work for you and your error is not a security error, try:

`source venv/bin/activate`

You will know it worked if your file path says <span style="color:green">(venv)</span> at the start of it.

Next, install the necessary packages using

`pip install flask python-dotenv`

Finally, you can run the backend with 

`flask run`

You will know it is running correctly if you open another terminal (in any directory) and enter

`curl http://localhost:5000/api/time`

which should return the current time. You will also be able to see this time displayed in the frontend (refresh the page if you opened it before starting the backend). 

However! When I tried to do this, I got an error because Pylance didn't recognize the **flask** import in the api.py file. This problem is explained [here](https://gist.github.com/krisbolton/20159d66f1d919c9c2380c96b6ac3915) and I was eventually able to fix it in vs code, although by a slightly different process than what was outlined in the article I found. 

Everything else is already included in the git project, so if you did all the steps you should be ready to go! However, if you run into any issues, the original tutorial I used to create the environment is [here](https://blog.miguelgrinberg.com/post/create-a-react-flask-project-in-2025), or email me (Bridget) at bng19@case.edu if you have any questions. 
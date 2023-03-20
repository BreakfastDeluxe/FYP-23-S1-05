# FYP-23-S1-05
Show and tell with a computer: A Deep Learning Approach
https://teamtamm.wordpress.com/

Our project Repo


Language: Python, CSS, HTML, mySQL

#### Holy Commandments:
1. DO NOT COMMIT TO MAIN
2. Before doing ANYTHING with code, perform GIT PULL!!!!!

#### SETUP

##### Before you clone
1. Make sure to install git https://git-scm.com/downloads
2. Open git CMD/CLI
3. git config
3a. Set your github username: git config --global user.name "GITHUB_USERNAME"
3b. Set your github email address: git config --global user.email "MY_NAME@example.com"


##### Visual Studio Code
1. Source Control (ctrl+shift+g)
2. Clone from repository
3. https://github.com/BreakfastDeluxe/FYP-23-S1-05.git
4. Accept any authorization requests
5. Choose location as htdocs(xampp) or www(wamp)
6. Would you like to open folder in workspace? Yes

###### git clone https://github.com/BreakfastDeluxe/FYP-23-S1-05

###### Selecting your branch
1. VSCODE: Left Side of Screen, Source Control
2. 3 dots next to refresh icon
3. Checkout to...
4. Choose origin/yourname

###### git PULL - To be done before you do any coding
1. Source Control (Crtl+shift+g)
2. "3 dots" > pull/push > Pull from... > origin(select this!)
3. select origin/main
4. select sync changes

###### start your terminal in VScode - to run python commands for django server management
1. In VScode, look at top left hand corner ribbons
2. Terminal>New Terminal
3. Check that the terminal path is correct "YOURSTORAGEPATH\FYP-23-S1-05"

###### django runserver - Start the webserver on your local machine for UI testing
Having issues with this section? Check your dependencies (see next section)
1. Navigate your CMDline to YOURSTORAGEPATH/FYP-23-S1-05/fypMain
2. py manage.py runserver
3. Access your devserver at http://127.0.0.1:8000/

###### Things to run in CMDline to install required dependencies
You can also run: pip install -r requirements.txt to autoinstall required dependencies (may not always be updated!)

1. opencv-python
2. numpy
3. Pillow
4. django-extensions
5. requests
6. gTTS
7. iPython
8. python-dotenv

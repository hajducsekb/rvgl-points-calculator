# RVGL Points Calculator

This is a simple project for calculating points during a multiplayer session in RVGL using the -sessionlog feature. It takes the results from the csv in the RVGL profile folder, takes the positions of the users, calculates the points based on the dictionary
in the rvgl.py file, then it outputs them into a standings.txt. The point system is easily editable, as well as the path for
your rvgl installation. It always takes the latest csv in the folder, so it should work properly even if it is started before 
RVGL is. For now, both files need to run, however, I plan to merge them. There's also a temp.txt for now, it makes it easier
to handle the data. 

## Usage

The only requirement this script has is Python 3 itself, since the used dependencies come included with it. For the installation
of Python 3, please refer to the official site, or look it up on the search engine of your choice. After you've set it up, edit
the files you've downloaded from here in the IDE you like (this could be notepad, if you don't have any), and edit the following
parts: in the rvgl.py file,
edit the paths in your rvglpath and tempfile variables (line 6 and 7). rvglpath is the path to your installation, this has to end
with a forward slash (/). Tempfile is the file path and name chosen for the temporary data file (this path isn't important, but
it has to end with a .txt file). In the rvgl_pointscalc.py file, type the same path for tempfile. standingsfile is also a text
file, which can also be anywhere, but it has to end with a txt as well. **Warning: Do not give a path and filename that already
exists, because it will be overwritten.**

Now you can open up two terminal/cmd windows, where you have to type 'python3 /path/to/files/rvgl.py' and in the other one 
'python3 /path/to/files/rvgl_pointscalc.py'. Note that instead of typing or copying the path to those files, you can also drag
them into the terminal after you've written python3 and a space. Keep these running until you've finished playing. It should 
now work, the championship standings will be in the standingsfile. If it doesn't, you or I have messed up somewhere... 

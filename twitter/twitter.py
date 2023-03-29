from models import *
from database import init_db, db_session
from datetime import datetime
from sqlalchemy import desc


class Twitter:

    # Constructor to keep track of instance variables
    def __init__(self):
        self.my_user = None

    """
    The menu to print once a user has logged in
    """
    def print_menu(self):
        print("\nPlease select a menu option:")
        print("1. View Feed")
        print("2. View My Tweets")
        print("3. Search by Tag")
        print("4. Search by User")
        print("5. Tweet")
        print("6. Follow")
        print("7. Unfollow")
        print("0. Logout")
    
    """
    Prints the provided list of tweets.
    """
    def print_tweets(self, tweets):
        for tweet in tweets:
            print("==============================")
            print(tweet)
        print("==============================")

    """
    Should be run at the end of the program
    """
    def end(self):
        print("Thanks for visiting!")
        db_session.remove()
    
    """
    Registers a new user. The user
    is guaranteed to be logged in after this function.
    """
    def register_user(self):
        # Get all existing usernames
        existing = db_session.query(User.username).all()
        # List comprehension to get rid of the tuples
        existing = [r for (r,) in existing]

        success = False
        while success == False:
            u = input("What will your twitter handle be?\n")
            p = input("Enter a password:\n")
            p2 = input("Re-enter your password:\n")
            if p != p2:
                print("Those passwords don't match. Try again.\n")
            elif u in existing:
                print("That username is already taken. Try again.\n")
            else:
                print("\nWelcome " + u + "!")
                # Add user to database and keep track of current user
                self.my_user = User(username = u, password = p)
                db_session.add(self.my_user)
                db_session.commit()
                success = True
                # Exit the loop
        
    """
    Logs the user in. The user
    is guaranteed to be logged in after this function.
    """
    def login(self):
        success = False
        existing = db_session.query(User.username).all()
        existing = [r for (r,) in existing]
        while success == False:
            u = input("Username:" )
            p = input("Password:" )
            # Get password associated with that username
            this_user_password = db_session.query(User.password).where(User.username == u).first()[0]
            if (u not in existing) or (this_user_password != p):
                print("Invalid username or password")
            else:
                print("\nWelcome " + u + "!")
                # Keep track of current user
                self.my_user = db_session.query(User).where(User.username == u).first()
                success = True
                # Exit the loop
    
    def logout(self):
        self.my_user = None
        print("You've been logged out")

    """
    Allows the user to login,  
    register, or exit.
    """
    def startup(self):
        print("Please select a menu option:")
        print("1. Login")
        print("2. Register User")
        print("0. Exit")
        option = int(input(""))

        if option == 1:
            self.login()
        elif option == 2:
            self.register_user()
        elif option == 0:
            self.end()

    def follow(self):
        acc = input("Who would you like to follow?\n")
        # Check who the user currently follows
        already_following = False
        all_following = self.my_user.following
        for a in all_following:
            # User already follows acc
            if acc == a.username:
                already_following = True
        if already_following == True:
            print("You already follow " + acc)
        else:
            # Add acc to following
            acc_object = db_session.query(User).where(User.username == acc).first()
            self.my_user.following.append(acc_object)
            db_session.commit()
            print("You are now following " + acc)

    def unfollow(self):
        acc = input("Who would you like to unfollow?\n")
        # Check who the user currently follows
        already_following = False
        all_following = self.my_user.following
        for a in all_following:
            # User already follows acc
            if acc == a.username:
                already_following = True
        if already_following == False:
            print("You don't follow " + acc)
        else:
            # Remove acc from following
            acc_object = db_session.query(User).where(User.username == acc).first()
            self.my_user.following.remove(acc_object)
            db_session.commit()
            print("You no longer follow " + acc)

    def tweet(self):
        c = input("Create Tweet: ")
        t_list = input("Enter your tags separated by spaces: ").split()
        existing = db_session.query(Tag.content).all()
        existing = [r for (r,) in existing]
        tag_objects = []
        for t in t_list:
            # Only add tag to database if it doesn't already exist
            if t not in existing:
                new_tag = Tag(content = t)
                db_session.add(new_tag)
                db_session.commit()
                tag_objects.append(new_tag)
            else:
                old_tag = db_session.query(Tag).where(Tag.content == t).first()
                tag_objects.append(old_tag)
        new_tweet = Tweet(content = c, timestamp = datetime.now(), username = self.my_user.username, tags = tag_objects)
        db_session.add(new_tweet)
        db_session.commit()
    
    def view_my_tweets(self):
        my_tweets = db_session.query(Tweet).where(Tweet.username == self.my_user.username).all()
        self.print_tweets(my_tweets)
    
    """
    Prints the 5 most recent tweets of the 
    people the user follows
    """
    def view_feed(self):
        usernames = []
        currently_following = self.my_user.following
        for a in currently_following:
            usernames.append(a.username)
        feed = db_session.query(Tweet).filter(Tweet.username.in_(usernames)).order_by(desc(Tweet.timestamp)).limit(5).all()
        self.print_tweets(feed)

    def search_by_user(self):
        existing = db_session.query(User.username).all()
        existing = [r for (r,) in existing]
        their_username = input("Enter the username you want to search by: ")
        # If username doesn't exist
        if their_username not in existing:
            print("There is no user by that name")
        else:
            their_tweets = db_session.query(Tweet).where(Tweet.username == their_username).all()
            self.print_tweets(their_tweets)

    def search_by_tag(self):
        existing = db_session.query(Tag.content).all()
        existing = [r for (r,) in existing]
        tag_to_search = input("Enter the tag you want to search by: ")
        # If tag doesn't exist or no tweets with the tag
        if tag_to_search not in existing:
            print("There are no tweets with this tag")
        else:
            # Query for the tag object and query for the tweets with that tag object
            tag_object = db_session.query(Tag).where(Tag.content == tag_to_search).first()
            tweets = db_session.query(Tweet).where(Tweet.tags.contains(tag_object)).all()
            self.print_tweets(tweets)
        
    """
    Allows the user to select from the 
    ATCS Twitter Menu
    """
    def run(self):
        init_db()

        print("Welcome to ATCS Twitter!")
        self.startup()

        run = True
        while run == True:
            self.print_menu()
            option = int(input(""))

            if option == 1:
                self.view_feed()
            elif option == 2:
                self.view_my_tweets()
            elif option == 3:
                self.search_by_tag()
            elif option == 4:
                self.search_by_user()
            elif option == 5:
                self.tweet()
            elif option == 6:
                self.follow()
            elif option == 7:
                self.unfollow()
            else:
                self.logout()
                run = False

        self.end()
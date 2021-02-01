from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()

def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)

class User(db.Model):
    """User."""

    __tablename__ = "users"

    username = db.Column(db.String(20),
                   primary_key=True)
    password = db.Column(db.Text,
                     nullable=False)
    email = db.Column(db.String(50),
                     nullable=False,
                     unique=True)
    firstname = db.Column(db.String(30),
                     nullable=False)
    lastname = db.Column(db.String(30),
                     nullable=False)

    feedback = db.relationship('Feedback', backref='user', cascade="all, delete", passive_deletes=True)

    @classmethod
    def register(cls, username, password):
        """Register user w/hashed password & return user."""

        hashed = bcrypt.generate_password_hash(password)
        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")

        # return instance of user w/username and hashed pwd
        return cls(username=username, password=hashed_utf8)

    @classmethod
    def authenticate(cls, username, password):
        """Validate that user exists & password is correct.

        Return user if valid; else return False.
        """

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            # return user instance
            return user
        else:
            return False

    def __repr__(self):
        """Show info about user."""

        u = self
        return f"<User - username: {u.username},  name: {u.lastname}, {u.firstname}>"

    def get_full_name(self):
        """Return users full name"""

        return f"{self.firstname} {self.lastname}"
                   
class Feedback(db.Model):
    """Feedback."""

    __tablename__ = "feedback"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    title = db.Column(db.String(100),
                     nullable=False)
    content = db.Column(db.Text,
                     nullable=False)
    username = db.Column(
        db.String(20),
        db.ForeignKey('users.username', ondelete="cascade"))
    
    def __repr__(self):
        """Show info about Feedback."""

        f = self
        return f"<Feeback - id: {f.id},  title: {f.title}>"

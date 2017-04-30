import uuid
from pricealerts.common.database import Database
import pricealerts.models.users.errors as UserErrors
from pricealerts.common.utils import Utils
from pricealerts.models.alerts.alert import Alert
import pricealerts.models.users.constants as UserConstants


class User(object):
    def __init__(self, email, password, _id=None):
        self.email = email
        self.password = password
        self._id = uuid.uuid4().hex if _id is None else _id

    def __repr__(self):
        return '<User {} with _id {}>'.format(self.email, self._id)

    @classmethod
    def is_login_valid(cls, email, password):
        """
        This method verifies that an email/password combo (as sent by the site forms) is valid or not.
        Checks that the email exists, and that the password associated to that email is correct.
        :param email: The user's email
        :param password: A sha512 hashed password
        :return: True if valid, False otherwise
        """
        cursor = Database.CONN.execute('select * from users where email = ?', (email,))
        user_data = cursor.fetchone()  # password in sha512 -> pbkdf2_sha512

        if user_data is None:
            # Tell the user that the email doesn't exist
            raise UserErrors.UserNotExistsError('Your user does not exist.')
        else:
            user = cls(*user_data)
            if not Utils.check_hashed_password(password, user.password):
                # Tell the user the password is wrong
                raise UserErrors.IncorrectPasswordError('Your password was wrong.')

        return True

    @staticmethod
    def register_user(email, password):
        """
        This method registers a user using email and password.
        The password already comes hashed as sha512.
        :param email: user's email (might be invalid)
        :param password: sha512-hashed password
        :return: True if registered succesfully, or False otherwise (exceptions can also be raised)
        """
        cursor = Database.CONN.execute('select * from {} where email = ?'.format(UserConstants.COLLECTION), (email,))
        user_data = cursor.fetchone()  # password in sha512 -> pbkdf2_sha512

        if user_data is not None:
            raise UserErrors.UserAlreadyRegisteredError("The email you used to register already exists.")
        if not Utils.email_is_valid(email):
            raise UserErrors.InvalidEmailError("The email does not have the right format.")

        User(email, Utils.hash_password(password)).save_to_db()

        return True

    def save_to_db(self):
        Database.CONN.execute('insert into {} values (?, ?, ?)'.format(UserConstants.COLLECTION),
                              (self.email, self.password, self._id))
        Database.CONN.commit()

    @classmethod
    def from_db(cls, _id):
        cursor = Database.CONN.execute('select * from {} where _id = ?'.format(UserConstants.COLLECTION), (_id,))
        user_data = cursor.fetchone()
        if user_data is not None:
            return cls(*user_data)

    @classmethod
    def find_by_email(cls, email):
        cursor = Database.CONN.execute('select * from {} where email = ?'.format(UserConstants.COLLECTION), (email,))
        user_data = cursor.fetchone()
        if user_data is not None:
            return cls(*user_data)

    def get_alerts(self):
        return Alert.find_by_user_email(self.email)

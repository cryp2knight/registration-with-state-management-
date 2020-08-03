from app import app, db
from app.models import User, Steps
from flask_testing import TestCase
from flask_login import  login_user, logout_user, current_user
import unittest

class FlaskTestCase(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        return app

    def setUp(self):
        db.create_all()
        user = User(username="daniel")
        user.set_password("pass")
        db.session.add(user)
        db.session.commit()
        

    def tearDown(self):
        db.session.remove()
        db.drop_all()


    def test_login_loads(self):
        """Ensure login page loads correctly."""
        response = self.client.get('/login', follow_redirects=True)
        self.assert200(response)

    def test_registration_loads(self):
        response = self.client.get('/register', follow_redirects=True)
        self.assert200(response)
    
    def test_login(self):
        user = User.query.filter_by(username='daniel').first()
        login_user(user)
        self.assertEqual(current_user.username, "daniel")

    def test_logout(self):
        user = User.query.filter_by(username='daniel').first()
        login_user(user)
        logout_user()
        self.assertEqual(current_user.is_authenticated, False )

    def test_get_last_step(self):
        user = User.query.filter_by(username='daniel').first()
        login_user(user)

        step = Steps(user_id=user.id, step1="step 1")
        db.session.add(step)
        db.session.commit()

        step = Steps.query.filter_by(user_id=user.id).first()
        self.assertEqual(2, step.get_last_step())


if __name__ == '__main__':
    unittest.main()
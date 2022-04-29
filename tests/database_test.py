import sqlite3
import unittest

from config import USER_DIR, CONTENT_DIR
from wiki.web import UserManager, create_app


class TestDatabase(unittest.TestCase):

    """
    Tests to see that once a User is added into the database, their information can be accessed.
    """
    def testThatUserCanBeAdded(self):
        app = create_app(CONTENT_DIR[:len(CONTENT_DIR)-8])
        app.app_context().push()

        testUser = "Test123XYZ"

        userManager = UserManager(object)
        userManager.add_user(testUser, "pasgit sword")

        dbCon = sqlite3.connect(USER_DIR + '/Users.sqlite')
        dbCur = dbCon.cursor()
        dbCur.execute("""SELECT username FROM users WHERE username = ?""", (testUser,))
        data = dbCur.fetchone()
        userManager.delete_user(testUser)

        self.assertEqual(True, data is not None)  # If the User Query is not null

    """
    Test That after a user is added to the database, it can be deleted. 
    Once a user is deleted, if a query is made to get their data, it should return null
    """
    def testThatUsersCanBeDeleted(self):
        app = create_app(CONTENT_DIR[:len(CONTENT_DIR)-8])
        app.app_context().push()

        testUser = "Test123XYZ"

        userManager = UserManager(object)
        userManager.add_user(testUser, "password")

        userManager.delete_user(testUser)

        dbCon = sqlite3.connect(USER_DIR + '/Users.sqlite')
        dbCur = dbCon.cursor()
        dbCur.execute("""SELECT username FROM users WHERE username = ?""", (testUser,))
        data = dbCur.fetchone()
        self.assertEqual(True, data is None)  # If the User Query is null


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestDatabase))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())

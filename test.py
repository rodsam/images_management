import unittest, os, time, datetime
from app import create_app, db
from google.cloud import storage
from app.models import User, Image, Comment
from config import Config, basedir, GOOGLE_AUTH, BUCKET_NAME


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        # db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        u = User(username='1234')
        u.set_password('1234')
        self.assertFalse(u.check_password('4321'))
        self.assertTrue(u.check_password('1234'))

    def test_data_add(self):
        admin = User(username='admin')
        admin.set_password('admin')
        user = User(username='user')
        user.set_password('user')
        db.session.add_all([admin, user])
        db.session.commit()

        gcs = storage.Client.from_service_account_json(os.path.join(basedir, GOOGLE_AUTH))
        bucket = gcs.bucket(BUCKET_NAME)

        now = str(int(time.time()))
        filename_01 = 'photo-1555874952-65f9f7004a62.jpeg'
        n_filename_01 = now + '_' + filename_01
        filename_02 = 'photo-1555874952-2129e5cba057.jpeg'
        n_filename_02 = now + '_' + filename_02

        bolb_01 = bucket.blob(n_filename_01)
        bolb_01.upload_from_filename(os.path.join(basedir, 'app/static/img/', filename_01))
        bolb_01.make_public()
        bolb_02 = bucket.blob(n_filename_02)
        bolb_02.upload_from_filename(os.path.join(basedir, 'app/static/img/', filename_02))
        bolb_02.make_public()

        img_01 = Image(title='imgtest1', src=n_filename_01, description='Image Test 01', user_id=user.id, created_at=datetime.datetime.now())
        img_02 = Image(title='imgtest2', src=n_filename_02, description='Image Test 02', user_id=admin.id, created_at=datetime.datetime.now())

        db.session.add_all([img_01, img_02])
        db.session.commit()


        comment_01 = Comment(content='Comment Test 01 on Image Test 01 comment by user', user_id= user.id, image_id= img_01.id, created_at= datetime.datetime.now())
        comment_02 = Comment(content='Comment Test 02 on Image Test 01 comment by admin', user_id= admin.id, image_id= img_01.id, created_at= datetime.datetime.now())
        comment_03 = Comment(content='Comment Test 03 on Image Test 02 comment by user', user_id= user.id, image_id= img_01.id, created_at= datetime.datetime.now())

        db.session.add_all([comment_01, comment_02, comment_03])
        db.session.commit()


if __name__ == "__main__":
    unittest.main(verbosity=2)

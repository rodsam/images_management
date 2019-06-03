import random, os, time, datetime
from google.cloud import storage
from flask import flash, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from app import db
from app.models import User, Image, Comment
from app.utils import required_admin
from app.admin.forms import UserForm, ImageForm, CommentForm
from app.admin import bp
from config import basedir, GOOGLE_AUTH, BUCKET_NAME

@bp.route('/')
@login_required
@required_admin
def index():
    users = User.query.all()
    for user in users:
        if user.is_admin:
            user.type = "admin"
        else:
            user.type = "user"
    return render_template('admin/index.html', users= users)

@bp.route('/users')
@login_required
@required_admin
def users():
    users = User.query.all()
    for user in users:
        if user.is_admin:
            user.type = "admin"
        else:
            user.type = "user"
    return render_template('admin/users.html', users= users)


@bp.route('/user/add', methods=['GET', 'POST'])
@login_required
@required_admin
def add_user():
    userform = UserForm(request.form, csrf_enabled= False)
    if userform.validate_on_submit() and request.method == 'POST':
        user = User(username= userform.username.data, email= userform.email.data, address= userform.address.data)
        user.set_password(userform.password.data)
        db.session.add(user)
        db.session.commit()
        # flash('User Added!')
        return redirect(url_for('admin.users'))
    return render_template('admin/add_user.html', form= userform, action_url=url_for('admin.add_user'), btn_label="Add User")

@bp.route('/user/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@required_admin
def edit_user(id):
    user = User.query.filter_by(id = id).one()
    userform = UserForm(request.form, csrf_enabled=False, obj= user)
    if userform.validate_on_submit() and request.method == 'POST':
        user.username = userform.username.data
        user.email = userform.email.data
        user.address = userform.address.data
        user.set_password(userform.password.data)
        db.session.merge(user)
        db.session.commit()
        # flash('User Updated!')
        return redirect(url_for('admin.users'))
    return render_template('admin/add_user.html', form=userform, action_url="/admin/user/edit/"+str(id), btn_label="Update User")

@bp.route('/user/delete/<int:id>', methods=['GET'])
@login_required
@required_admin
def del_user(id):
    user = User.query.filter_by(id = id).one()
    db.session.delete(user)
    db.session.commit()
    # flash('User Deleted!')
    return redirect(url_for('admin.users'))


@bp.route('/user/admin/<int:id>/<int:data>', methods=['GET'])
@login_required
@required_admin
def make_admin(id, data):
    user = User.query.filter_by(id = id).one()
    user.admin_power = int(data)
    db.session.merge(user)
    db.session.commit()
    return redirect(url_for('admin.users'))


@bp.route('/images', methods=['GET'])
@login_required
@required_admin
def images():
    images = Image.query.all()
    if len(images) > 0:
        gcs = storage.Client.from_service_account_json(os.path.join(basedir, GOOGLE_AUTH))

        bucket = gcs.bucket(BUCKET_NAME)

        for i in images:
            bolb = bucket.blob(i.src)
            bolb.make_public()
            i.file_path = bolb.public_url

    return render_template('admin/images.html', images= images)

@bp.route('/image/add', methods=['GET', 'POST'])
@login_required
@required_admin
def add_image():
    imageform = ImageForm(csrf_enabled= False)
    if imageform.validate_on_submit() and request.method =='POST':
        gcs = storage.Client.from_service_account_json(os.path.join(basedir, GOOGLE_AUTH))
        bucket = gcs.bucket(BUCKET_NAME)

        image_data = imageform.image.data.stream.read()

        now = str(int(time.time()))
        n_filename = now + '_' + imageform.image.data.filename
        blob = bucket.blob(n_filename)

        blob.upload_from_string(image_data, content_type= imageform.image.data.mimetype)
        blob.make_public()
        image = Image(title= imageform.title.data, src= n_filename , user_id= current_user.id, description= imageform.description.data, created_at= datetime.datetime.now())
        db.session.add(image)
        db.session.commit()
        # flash('Image created!')

        return redirect(url_for('admin.images'))
    return render_template('admin/add_image.html', form = imageform, action_url=url_for('admin.add_image'), btn_label='Add Image')


@bp.route('/image/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@required_admin
def edit_image(id):
    image = Image.query.filter_by(id = id).one()
    imagefrom = ImageForm(csrf_enabled= False, obj= image)
    if imagefrom.validate_on_submit()and request.method=='POST':
        gcs= storage.Client.from_service_account_json(os.path.join(basedir, GOOGLE_AUTH))
        bucket= gcs.bucket(BUCKET_NAME)

        image_data = imagefrom.image.data.stream.read()

        now = str(int(time.time()))
        n_filename = now + '_' + imagefrom.image.data.filename

        blob = bucket.blob(n_filename)
        o_blob = bucket.blob(image.src)
        o_blob.delete()

        blob.upload_from_string(image_data, content_type= imagefrom.image.data.mimetype)
        blob.make_public()
        image.src= n_filename
        image.title = imagefrom.title.data
        image.description = imagefrom.description.data
        db.session.merge(image)
        db.session.commit()
        return redirect(url_for('admin.images'))
    return render_template('admin/add_image.html', form=imagefrom, action_url=url_for('admin.edit_image', id= id), btn_label="Update Image")



@bp.route('/image/delete/<int:id>', methods=['GET'])
@login_required
@required_admin
def delete_image(id):
    '''
    Delete Image
    :param id: image id
    '''
    image = Image.query.filter_by(id= id).one()
    gcs = storage.Client.from_service_account_json(os.path.join(basedir, GOOGLE_AUTH))
    bucket = gcs.bucket(BUCKET_NAME)
    blob = bucket.blob(image.src)
    blob.delete()
    db.session.delete(image)
    db.session.commit()
    # flash('Image Deleted!')
    return redirect(url_for('admin.images'))


@bp.route('/comments/<int:imgid>', methods=['GET'])
@login_required
@required_admin
def comments(imgid):
    comments = Comment.query.filter_by(image_id= imgid).all()
    return render_template('admin/comments.html', comments= comments, imgid=imgid)

@bp.route('/comment/add/<int:imgid>', methods=['GET', 'POST'])
@login_required
@required_admin
def add_comment(imgid):
    commentform = CommentForm(csrf_enabled= False)
    if commentform.validate_on_submit() and request.method == 'POST':
        comment = Comment(content= commentform.content.data, user_id= current_user.id, image_id= imgid, created_at= datetime.datetime.now())
        db.session.add(comment)
        db.session.commit()
        # flash('Comment added!')
        return redirect(url_for('admin.comments', imgid= imgid))
    return render_template('admin/add_comment.html', form= commentform, action_url=url_for('admin.add_comment', imgid= imgid), btn_label='Add Comment')

@bp.route('/comment/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@required_admin
def edit_comment(id):
    comment = Comment.query.filter_by(id = id).one()
    commentform = CommentForm(csrf_enabled= False, obj= comment)
    if commentform.validate_on_submit() and request.method== 'POST':
        comment.content = commentform.content.data
        db.session.merge(comment)
        db.session.commit()
        # flash('Comment updated!')
        return redirect(url_for('admin.comments', imgid= comment.image_id))
    return render_template('admin/add_comment.html', form= commentform, action_url= url_for('admin.edit_comment', id= id), btn_label='Edit Comment')


@bp.route('/comment/delete/<int:id>', methods=['GET'])
@login_required
@required_admin
def delete_comment(id):
    comment = Comment.query.filter_by(id= id).one()
    db.session.delete(comment)
    db.session.commit()
    # flash('Comment Deleted')
    return redirect(url_for('admin.comments'))

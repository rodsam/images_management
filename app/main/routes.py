import os, time, datetime
from flask import flash, render_template, redirect, send_file, request, url_for
from flask_login import current_user, login_required, user_unauthorized
from google.cloud import storage
from app.admin.forms import CommentForm, UserForm
from app import db
from app.models import User, Image, Comment
from app.admin.forms import ImageForm
from app.main import bp
from config import basedir, GOOGLE_AUTH, BUCKET_NAME

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    if not user_unauthorized:
        if current_user.is_admin:
            return redirect('admin.index')
    images = Image.query.filter_by(user_id= current_user.id).all()
    if len(images) > 0:
        gcs = storage.Client.from_service_account_json(os.path.join(basedir, GOOGLE_AUTH))

        bucket = gcs.bucket(BUCKET_NAME)

        for i in images:
            bolb = bucket.blob(i.src)
            bolb.make_public()
            i.file_path = bolb.public_url

    return render_template('index.html', user= current_user, images = images)


@bp.route('/image/<int:id>', methods=['GET'])
def image(id):
    image = Image.query.filter_by(id= id, user_id = current_user.id).one()
    if image:
        gcs = storage.Client.from_service_account_json(os.path.join(basedir, GOOGLE_AUTH))

        bucket = gcs.bucket(BUCKET_NAME)
        bolb = bucket.blob(image.src)
        image.file_path = bolb.public_url
    comments = Comment.query.filter_by(image_id=id).all()

    form = CommentForm(csrf_enabled= False)

    return render_template('main/image.html', user= current_user, image= image, comments= comments, form= form, action_url=url_for('main.add_comment', imgid= image.id), btn_label='Add Comment')

@bp.route('/images', methods= ['GET'])
@login_required
def images():
    images = Image.query.filter_by(user_id = current_user.id).all()
    if len(images) > 0:
        gcs = storage.Client.from_service_account_json(os.path.join(basedir, GOOGLE_AUTH))

        bucket = gcs.bucket(BUCKET_NAME)

        for i in images:
            bolb = bucket.blob(i.src)
            i.file_path = bolb.public_url
    return render_template('main/images.html', user= current_user, images= images)


@bp.route('/image/add', methods=['GET', 'POST'])
@login_required
def add_image():
    form = ImageForm(csrf_enabled= False)
    if form.validate_on_submit() and request.method == 'POST':
        gcs = storage.Client.from_service_account_json(os.path.join(basedir, GOOGLE_AUTH))
        bucket = gcs.bucket(BUCKET_NAME)

        image_data = form.image.data.stream.read()

        now = str(int(time.time()))
        n_filename = now + '_' + form.image.data.filename

        blob = bucket.blob(n_filename)

        blob.upload_from_string(image_data, content_type=form.image.data.mimetype)
        blob.make_public()
        image = Image(title= form.title.data, src= n_filename , user_id= current_user.id, description= form.description.data)
        db.session.add(image)
        db.session.commit()

        return redirect(url_for('main.images'))
    return render_template('main/add_image.html', user= current_user, form= form, action_url=url_for('main.add_image'), btn_label='Add Image')

@bp.route('/image/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_image(id):
    image = Image.query.filter_by(id= id, user_id = current_user.id).one()
    form  = ImageForm(csrf_enabled= False, obj=image)
    if form.validate_on_submit() and request.method == 'POST':
        gcs = storage.Client.from_service_account_json(os.path.join(basedir, GOOGLE_AUTH))
        bucket = gcs.bucket(BUCKET_NAME)

        image_data = form.image.data.stream.read()

        now = str(int(time.time()))
        n_filename = now + '_' + form.image.data.filename

        blob = bucket.blob(n_filename)
        o_blob = bucket.blob(image.src)
        o_blob.delete()

        blob.upload_from_string(image_data, content_type=form.image.data.mimetype)
        blob.make_public()
        image.src = n_filename
        image.title = form.title.data

        image.description = form.description.data
        db.session.merge(image)
        db.session.commit()

        return redirect(url_for('main.images'))
    return render_template('main/add_image.html', user= current_user, form= form, action_url=url_for('main.edit_image', id= id), btn_label="Update Image")

@bp.route('/image/delete/<int:id>', methods=['GET'])
@login_required
def delete_image(id):
    image = Image.query.filter_by(id = id, user_id= current_user.id).one()
    gcs = storage.Client.from_service_account_json(os.path.join(basedir, GOOGLE_AUTH))
    bucket = gcs.bucket(BUCKET_NAME)
    blob = bucket.blob(image.src)
    blob.delete()
    db.session.delete(image)
    db.session.commit()
    # flash('Image Deleted!')
    return redirect(url_for('main.images'))


@bp.route('/image/download/<int:id>', methods=['GET'])
@login_required
def download_image(id):
    image = Image.query.filter_by(id = id).one()
    gcs = storage.Client.from_service_account_json(os.path.join(basedir, GOOGLE_AUTH))
    bucket = gcs.bucket(BUCKET_NAME)
    blob = bucket.blob(image.src)
    temppath = os.path.join(basedir, 'app/static/tempimg/')
    if not os.path.exists(temppath):
        os.mkdir(temppath)
    with open(os.path.join(temppath, blob.name), 'wb') as file:
        blob.download_to_file(file)
    return send_file(os.path.join(temppath, blob.name), attachment_filename=blob.name, mimetype='image/jpg')


@bp.route('/user/edit', methods=['GET', 'POST'])
@login_required
def edit_user():
    user = User.query.filter_by(id= current_user.id).one()
    form = UserForm(csrf_enabled= False, obj= user)
    if form.validate_on_submit() and request.method == 'POST':
        user.username = form.username.data
        user.set_password(form.username.data)
        user.address = form.address.data
        user.email = form.email.data

        db.session.merge(user)
        db.session.commit()

        # flash('User profile updated!')
        return redirect(url_for('main.index'))
    return render_template('main/edit_user.html',user= current_user, form= form, action_url=url_for('main.edit_user'), btn_label="Update User Profile")

@bp.route('/comment/add/<int:imgid>', methods=['POST'])
def add_comment(imgid):
    form = CommentForm(csrf_enabled= False)
    if form.validate_on_submit() and request.method == 'POST':
        comment = Comment(content= form.content.data, image_id=imgid, user_id= current_user.id, created_at= datetime.datetime.now())
        db.session.add(comment)
        db.session.commit()
        # flash('Comment Added')
    return redirect(url_for('main.image', id= imgid))

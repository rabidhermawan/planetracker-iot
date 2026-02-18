# Library Import
from datetime import time
from time import perf_counter
from flask import abort, redirect, send_file, send_from_directory, url_for, render_template, request, flash, request

from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename

import os
import mimetypes
from io import BytesIO

# Project Module Import
from faizencryption import app, db
from faizencryption.forms import RegisterAccountForm, LoginAccountForm, ShareForm, UpdateAccountForm, UploadFileForm
from faizencryption.models import User, Document, UserDocument
from faizencryption.encryption import encrypt, decrypt
from faizencryption.logging import write_log


@app.route("/")
def home():
    all_files = None
    if current_user.is_authenticated:
        all_files = Document.query.filter_by(user_uuid=current_user.uuid)
    return render_template("index.html", files=all_files)

# For login
@app.route("/login/", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("user"))
    
    email = None
    password = None
    form = LoginAccountForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user and existing_user.verify_password(form.password.data):
            login_user(existing_user, remember=True)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('user'))
        else:
            flash(f"Invalid credentials!")
    
    return render_template("login.html", email=email, password=password, form=form)

    
@app.route("/register/", methods=["POST", "GET"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("user"))
    form = RegisterAccountForm()    
    if form.validate_on_submit():
        user = User(name=form.name.data, email = form.email.data, password = form.password.data)
        db.session.add(user)
        db.session.commit()
            
        flash(f"The account has successfully been registered, please log in with the inputted credentials.")
        return redirect(url_for("login"))
    
    return render_template("register.html", form=form)

@app.route("/logout/")
@login_required
def logout():
    logout_user()
    flash("You have been logged out")
    return redirect(url_for("login"))

# User stuff

@app.route("/user/", methods=["POST", "GET"])
@login_required
def user():        
    all_users = User.query.all()
    return render_template("user.html", user_list=all_users)
    
@app.route("/user/update/<int:id>/", methods=["POST", "GET"])
@login_required
def update(id):
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.email = form.email.data
        
        try:
            db.session.commit()
            flash("User updated successfully!")
        except:
            flash("Failed to update user")
            
        return redirect(url_for("user"))
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.email.data = current_user.email
    
    return render_template("update.html", form=form)

# Upload file, attach uuid from user when uploaded
@app.route("/upload/", methods=["POST", "GET"])
@login_required
def upload():
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file_upload.data
        try:
            # Get the filename
            filename = secure_filename(file.filename)
            file_data = file.read()
            # Encrypt the data, log the time too
            enc_start = perf_counter()
            try:
                file.stream.seek(0)
                file_iv, file_cipher, _ = encrypt(user_uuid=current_user.uuid, data=file_data, method=form.enc_method.data)
            except Exception as e:
                write_log(
                    event="encrypt",
                    algorithm=form.enc_method.data,
                    filename=filename,
                    plaintext_size=len(file_data),
                    error=e,
                )
                flash(f'An error occurred during encryption: {e}', 'danger')
                return redirect(url_for('upload'))
            enc_end = perf_counter()
            enc_time_s = enc_end - enc_start
            
            file_entry = Document(name=filename, 
                                  user_uuid=current_user.uuid,
                                  file_type=file.content_type, 
                                  enc_type=form.enc_method.data,
                                  )
            
            db.session.add(file_entry)
            db.session.commit()
            
            with open(os.path.join(app.config['UPLOAD_FOLDER'], r"{}-{}".format(file_entry.uuid, filename)), 'wb') as encrypted_file:
                if file_iv:
                    encrypted_file.write(file_iv+file_cipher)
                else:
                    encrypted_file.write(file_cipher)
            
            # Write the log to JSON
            write_log(
                event="encrypt",
                doc_uuid=file_entry.uuid,
                algorithm=form.enc_method.data,
                filename=filename,
                plaintext_size=len(file_data),
                ciphertext_size=len(file_cipher), 
                iv_len=len(file_iv),
                time_delta=enc_time_s
            )
            
            db.session.add(file_entry)
            db.session.commit()
            flash("Successfully uploaded the file")
        except Exception as e:
            flash(f"Failed to upload file, {e}")
        return redirect(url_for("home"))
    return render_template("upload.html", form=form)

@app.route("/download/<string:uuid>/", methods=["GET"])
@login_required
def download_file(uuid):
    file_entry = Document.query.filter_by(uuid=uuid).first()
    if file_entry:
        try:
            # Decrypt the data, log the time it took to decrypt
            dec_start = perf_counter()
            with open(os.path.join(app.config['UPLOAD_FOLDER'], r"{}-{}".format(file_entry.uuid, file_entry.name)), 'rb') as encrypted_file:
                iv_size, cipher_size, decrypted_data, _ = decrypt(user_uuid=current_user.uuid, enc_data=encrypted_file.read(), method=file_entry.enc_type)
            dec_end = perf_counter()
            dec_time_s = dec_end - dec_start
            
        except FileNotFoundError:
            write_log(
                    event="decrypt",
                    algorithm=file_entry.enc_type,
                    filename=file_entry.name,
                    plaintext_size=0,
                    error="Data was not found",
            )
            abort(404)
            
        write_log(
                event="decrypt",
                doc_uuid=file_entry.uuid,
                algorithm=file_entry.enc_type,
                filename=file_entry.name,
                plaintext_size=len(decrypted_data),
                ciphertext_size=cipher_size, 
                iv_len=iv_size,
                time_delta=dec_time_s
            )
            
        return send_file(
            BytesIO(decrypted_data), # Wrap the decrypted data in BytesIO stream for download
            as_attachment=True,
            download_name=file_entry.name,
            mimetype = mimetypes.guess_type(file_entry.name)[0] or "application/octet-stream"
        )
        # return send_from_directory(app.config["UPLOAD_FOLDER"], r"{}-{}".format(file_entry.uuid, file_entry.name))

@app.route("/remove/<string:uuid>/")
@login_required
def remove_file(uuid):
    file_entry = Document.query.filter_by(uuid=uuid).first()

    # Delete file in the upload folder
    filename = os.path.join(app.config["UPLOAD_FOLDER"], f"{file_entry.uuid}-{file_entry.name}")
    if os.path.exists(filename):
        try:
            os.remove(filename)
    
            # Delete the entry in the database
            Document.query.filter_by(uuid=uuid).delete()
            db.session.commit()
    
            flash(f"{filename} has been removed")
        except Exception as e:
            flash(f"Failed to delete {filename}, {str(e)}")
    else:
        flash(f"{filename} file doesn't exist")
    return redirect(url_for("home"))

# Share
@app.route("/share/<string:uuid>/", methods=["GET", "POST"])
@login_required
def share_file(uuid):
    form = ShareForm()
    
    if form.validate_on_submit():
        selected_user_ids = form.users.data

        for user_id in selected_user_ids:
            link = UserDocument(user_id=user_id, document_id=uuid)
            db.session.add(link)

        db.session.commit()
        flash("Document shared successfully!", "success")
        return redirect(url_for("index"))
    
    # Query
    users_not_shared = (
        User.query
        .filter(~User.id.in_(
            db.session.query(UserDocument.user_id)
            .filter(UserDocument.document_id == uuid)
        ))
        .all()
    )
     
    form.users.choices = [(u.id, u.name) for u in users_not_shared]

    return render_template("share.html", form=form, uuid=uuid)
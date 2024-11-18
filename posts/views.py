import base64

from hashlib import scrypt

from cryptography.fernet import Fernet
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import desc

from config import Post, db, logger
from decorators import roles_required
from posts.forms import PostForm

posts_bp = Blueprint("posts", __name__, template_folder="templates")


@posts_bp.route("/posts")
@login_required
@roles_required("end_user")
def posts():
    all_posts: list[Post] = Post.query.order_by(desc("id")).all()

    # decrypt posts contents
    for post in all_posts:
        post.title, post.body = post.decrypt_post()

    return render_template("posts/posts.html", posts=all_posts)


@posts_bp.route("/create", methods=["GET", "POST"])
@login_required
@roles_required("end_user")
def create():
    form = PostForm()

    if form.validate_on_submit():
        # generating key at runtime rather than persistent storage
        key = scrypt(
            password=current_user.password.encode(),
            salt=current_user.salt.encode(),
            n=2048,
            r=8,
            p=1,
            dklen=32,
        )
        encoded_key = base64.b64encode(key)
        cipher = Fernet(encoded_key)

        encrypted_title: str = cipher.encrypt(form.title.data.encode()).decode()
        encrypted_body: str = cipher.encrypt(form.body.data.encode()).decode()

        new_post = Post(
            userid=current_user.get_id(), title=encrypted_title, body=encrypted_body
        )

        db.session.add(new_post)
        db.session.commit()
        logger.info(
            f"[User: {current_user.email}, Role: {current_user.role}, Post: {new_post.id}, IP: {request.remote_addr}] Post Created."
        )

        flash("Post created.", category="success")
        return redirect(url_for("posts.posts"))

    return render_template("posts/create.html", form=form)


@posts_bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
@roles_required("end_user")
def update(id):
    post = Post.query.filter_by(id=id).first()
    if not post:
        flash("Post not found.", category="danger")
        return redirect(url_for("posts.posts"))
    if post and current_user.get_id() != str(post.userid):
        logger.info(
            f"[User: {current_user.email}, Role: {current_user.role}, Post: {post.id}, Author: {post.user.email}, IP: {request.remote_addr}] Unauthorized Update."
        )
        flash("You do not have permission to update this post.", category="danger")
        return redirect(url_for("posts.posts"))

    post_to_update = Post.query.filter_by(id=id).first()

    if not post_to_update:
        return redirect(url_for("posts.posts"))

    form = PostForm()

    if form.validate_on_submit():
        post_to_update.update(title=form.title.data, body=form.body.data)

        flash("Post updated.", category="success")
        logger.info(
            f"[User: {current_user.email}, Role: {current_user.role}, Post: {post_to_update.id}, Author: {post_to_update.user.email}, IP: {request.remote_addr}] Post updated."
        )
        return redirect(url_for("posts.posts"))

    form.title.data = post_to_update.title
    form.body.data = post_to_update.body

    return render_template("posts/update.html", form=form)


@posts_bp.route("/<int:id>/delete")
@login_required
@roles_required("end_user")
def delete(id):
    post = Post.query.filter_by(id=id).first()
    if not post:
        flash("Post not found.", category="danger")
        return redirect(url_for("posts.posts"))
    if post and current_user.get_id() != str(post.userid):
        logger.info(
            f"[User: {current_user.email}, Role: {current_user.role}, Post: {post.id}, Author: {post.user.email}, IP: {request.remote_addr}] Unauthorized Deletion."
        )
        flash("You do not have permission to delete this post.", category="danger")
        return redirect(url_for("posts.posts"))

    authors_email = post.user.email
    Post.query.filter_by(id=id).delete()
    db.session.commit()

    logger.info(
        f"[User: {current_user.email}, Role: {current_user.role}, Post: {id}, Author: {authors_email}, IP: {request.remote_addr}] Post deleted."
    )
    flash("Post deleted.", category="success")
    return redirect(url_for("posts.posts"))

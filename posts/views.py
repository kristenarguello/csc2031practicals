from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from sqlalchemy import desc

from config import Post, db
from posts.forms import PostForm

posts_bp = Blueprint("posts", __name__, template_folder="templates")


@posts_bp.route("/posts")
@login_required
def posts():
    all_posts = Post.query.order_by(desc("id")).all()

    return render_template("posts/posts.html", posts=all_posts)


@posts_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    form = PostForm()

    if form.validate_on_submit():
        new_post = Post(
            userid=current_user.get_id(), title=form.title.data, body=form.body.data
        )

        db.session.add(new_post)
        db.session.commit()

        flash("Post created.", category="success")
        return redirect(url_for("posts.posts"))

    return render_template("posts/create.html", form=form)


@posts_bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    post = Post.query.filter_by(id=id).first()
    if not post:
        flash("Post not found.", category="danger")
        return redirect(url_for("posts.posts"))
    if post and current_user.get_id() != str(post.userid):
        flash("You do not have permission to update this post.", category="danger")
        return redirect(url_for("posts.posts"))

    post_to_update = Post.query.filter_by(id=id).first()

    if not post_to_update:
        return redirect(url_for("posts.posts"))

    form = PostForm()

    if form.validate_on_submit():
        post_to_update.update(title=form.title.data, body=form.body.data)

        flash("Post updated.", category="success")
        return redirect(url_for("posts.posts"))

    form.title.data = post_to_update.title
    form.body.data = post_to_update.body

    return render_template("posts/update.html", form=form)


@posts_bp.route("/<int:id>/delete")
@login_required
def delete(id):
    post = Post.query.filter_by(id=id).first()
    if not post:
        flash("Post not found.", category="danger")
        return redirect(url_for("posts.posts"))
    if post and current_user.get_id() != str(post.userid):
        flash("You do not have permission to delete this post.", category="danger")
        return redirect(url_for("posts.posts"))

    Post.query.filter_by(id=id).delete()
    db.session.commit()

    flash("Post deleted.", category="success")
    return redirect(url_for("posts.posts"))

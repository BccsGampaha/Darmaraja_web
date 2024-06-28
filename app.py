from flask import Flask, render_template, request, redirect, url_for, flash, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_basicauth import BasicAuth
from flask import jsonify
from datetime import datetime
import random
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///articles.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['BASIC_AUTH_USERNAME'] = 'admin'  # Replace with ADMIN_USERNAME
app.config['BASIC_AUTH_PASSWORD'] = 'password'  # Replace with ADMIN_PASSWORD
basic_auth = BasicAuth(app)

db = SQLAlchemy(app)


def group_by_lengths(vals, lens):
    result = []
    index = 0
    vals_length = len(vals)

    for length in lens:
        sublist = []
        for _ in range(length):
            if index < vals_length:
                sublist.append(vals[index])
                index += 1
            else:
                index = 0 
                sublist.append(vals[index])
                index += 1

        result.append(sublist)

    return result


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    image_file = db.Column(db.String(300), nullable=True)
    publishedAt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<Article {self.title}>'


# Create the database and tables
with app.app_context():
    db.create_all()


@app.route('/')
def index():
    articles = Article.query.order_by(Article.publishedAt.desc()).all()
    random.shuffle(articles)
    """ top news & main middle news --> 2,  lft only title set--> 4, left news box set --> 7, write news box set --> 9  """
    articles  = group_by_lengths(articles,[2,4,20,40,39])
    print(articles)
    return render_template('index.html', articles=articles)


@app.route('/admin', methods=['GET', 'POST'])
@basic_auth.required
def admin():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        publishedAt = datetime.strptime(request.form['publishedAt'], '%Y-%m-%dT%H:%M')

        image_file = request.files['image_file']
        if image_file:
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)

            new_article = Article(
                title=title,
                description=description,
                image_file=f'uploads/{filename}',
                publishedAt=publishedAt
            )

            db.session.add(new_article)
            db.session.commit()

            flash('Article added successfully!', 'success')
        else:
            flash('Failed to upload image.', 'danger')

        return redirect(url_for('admin'))

    articles = Article.query.order_by(Article.publishedAt.desc()).all()
    return render_template('admin.html', articles=articles)


@app.route('/logout')
def logout():
    response = make_response(redirect(url_for('index')))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.route('/article/<int:article_id>', methods=['GET'])
def get_article(article_id):
    article = Article.query.get(article_id)
    if not article:
        return render_template('404.html'), 404

    return render_template('article.html', article=article)



@app.route('/edit/<int:article_id>', methods=['GET', 'POST'])
def edit_article(article_id):
    article = Article.query.get_or_404(article_id)

    if request.method == 'POST':
        article.title = request.form['title']
        article.description = request.form['description']
        article.publishedAt = datetime.strptime(request.form['publishedAt'], '%Y-%m-%dT%H:%M')

        image_file = request.files.get('image_file')
        if image_file:
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)
            article.image_file = f'uploads/{filename}'

        db.session.commit()
        flash('Article updated successfully!', 'success')
        return redirect(url_for('admin'))

    return render_template('edit.html', article=article)


@app.route('/delete/<int:article_id>', methods=['POST'])
def delete_article(article_id):
    article = Article.query.get_or_404(article_id)
    db.session.delete(article)
    db.session.commit()
    flash('Article deleted successfully!', 'success')
    return redirect(url_for('admin'))


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5673)

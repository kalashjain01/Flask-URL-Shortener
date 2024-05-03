from flask import Flask, render_template, request, redirect
from pymongo import MongoClient
import shortuuid

app = Flask(__name__)

client = MongoClient("mongodb://localhost:27017/")
db = client['url_shortener']
urls_collection = db['urls']


@app.route('/')
def index():
    urls = list(urls_collection.find())
    return render_template('index.html', urls=urls)

@app.route('/shorten', methods=['POST'])
def shorten():
    long_url = request.form['long_url']
    short_url = shortuuid.uuid()[:8]

    urls_collection.insert_one({'short_url': short_url, 'long_url': long_url})

    create_message = f'Short URL created: {short_url}'
    urls = list(urls_collection.find())
    return render_template('index.html', create_message=create_message, short_url=short_url, urls=urls)

@app.route('/<short_url>')
def redirect_to_long_url(short_url):
    url_data = urls_collection.find_one({'short_url': short_url})
    if url_data:
        return redirect(url_data['long_url'])
    else:
        return render_template('404.html'), 404

@app.route('/update/<short_url>', methods=['GET', 'POST'])
def update(short_url):
    url_data = urls_collection.find_one({'short_url': short_url})
    if url_data:
        if request.method == 'POST':
            new_long_url = request.form['new_long_url']
            urls_collection.update_one({'short_url': short_url}, {'$set': {'long_url': new_long_url}})
            update_message = f'Short URL updated: {short_url}'
            return render_template('update.html', update_message=update_message, short_url=short_url, long_url=url_data['long_url'])
        return render_template('update.html', short_url=short_url, long_url=url_data['long_url'])
    else:
        return render_template('404.html'), 404

@app.route('/delete/<short_url>')
def delete(short_url):
    urls_collection.delete_one({'short_url': short_url})
    delete_message = f'Short URL deleted: {short_url}'
    urls = list(urls_collection.find())
    return render_template('index.html', delete_message=delete_message, urls=urls)

if __name__ == '__main__':
    app.run(debug=True)
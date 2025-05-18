import string
import secrets
from flask import jsonify, url_for, redirect, request
from dbconfig import app, db
from model import URL
import validators
from urllib.parse import unquote


with app.app_context():
    db.create_all()
    
    
def generate_shortcode():
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(6))


@app.route("/home", methods=['GET'])
def home():
    return jsonify({"Home":"Send further request to shorten urls"})


@app.route("/shorten/<path:original_url>", methods=["POST"])
@app.route("/shorten", methods=["POST"])
def shorten(original_url=None):
    try:
        if original_url:
            url = unquote(original_url)
            
        else:
            data = request.get_json()
            url = data.get('url')
            
        if (not url) or (not validators.url(url)):
            return jsonify({"ERROR":"valid url is required"}), 400
        
        dbshorturl = URL.query.filter_by(orgurl=url).first()
        if dbshorturl:
                return jsonify({"shorturl":dbshorturl.shorturl}), 200
        
        
        while True:
            shorturl = generate_shortcode()
            
            if not URL.query.filter_by(shorturl=shorturl).first():
                break
        
        new_url = URL(
            shorturl = shorturl,
            orgurl = url
        )
        
        db.session.add(new_url)
        db.session.commit()
        
        return jsonify({"URL":shorturl}), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"ERROR":str(e)}), 500
    
    

@app.route("/<short_code>", methods=["GET"])
def redirect_to_url(short_code):
    try:
        ip_address = request.remote_addr
        if request.headers.getlist("X-Forwarded-For"):
            ip_address = request.headers.getlist("X-Forwarded-For")[0]
        
        print(f"ip address : {ip_address}")
        url_obj = URL.query.filter_by(shorturl=short_code).first()
        
        if not url_obj:
            return jsonify({"error": "Short URL not found"}), 404
        
        return redirect(url_obj.orgurl, code=302)

    except Exception as e:
        return jsonify({"ERROR":str(e)}), 500



if __name__ == "__main__":
    app.run(debug=True)

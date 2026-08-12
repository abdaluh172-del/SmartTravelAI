import os

from flask import Flask, render_template, session
from flask_cors import CORS

from config import Config
from extensions import db


def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object(Config)

    CORS(app, resources={r"/api/*": {"origins": app.config.get("ALLOWED_ORIGINS", "*")}})

    db.init_app(app)

    # ---- تسجيل Blueprints الخاصة بالـ API ----
    from routes.health import health_bp
    from routes.flights import flights_bp
    from routes.ai import ai_bp
    from routes.budget import budget_bp
    from routes.destinations import destinations_bp
    from routes.auth import auth_bp
    from routes.favorites import favorites_bp
    from routes.admin import admin_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(flights_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(budget_bp)
    app.register_blueprint(destinations_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(favorites_bp)
    app.register_blueprint(admin_bp)

    with app.app_context():
        os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), "instance"), exist_ok=True)
        db.create_all()
        _seed_initial_data()

    # ---- صفحات الواجهة الأمامية (Server-rendered, تستدعي REST API عبر JS) ----
    @app.context_processor
    def inject_globals():
        from models import User
        user = None
        if session.get("user_id"):
            user = User.query.get(session["user_id"])
        return {"current_user": user}

    @app.route("/")
    def page_home():
        return render_template("index.html")

    @app.route("/results")
    def page_results():
        return render_template("results.html")

    @app.route("/flight")
    def page_flight_details():
        return render_template("flight-details.html")

    @app.route("/assistant")
    def page_assistant():
        return render_template("assistant.html")

    @app.route("/planner")
    def page_planner():
        return render_template("planner.html")

    @app.route("/destination")
    def page_destination():
        return render_template("destination.html")

    @app.route("/favorites")
    def page_favorites():
        return render_template("favorites.html")

    @app.route("/login")
    def page_login():
        return render_template("login.html")

    @app.route("/profile")
    def page_profile():
        return render_template("profile.html")

    @app.route("/admin")
    def page_admin():
        return render_template("admin.html")

    return app


def _seed_initial_data():
    from models import Airline, Destination, User
    from data.destinations import DESTINATIONS_SEED
    from providers.mock_provider import AIRLINES

    if Airline.query.count() == 0:
        for a in AIRLINES:
            db.session.add(Airline(code=a["code"], name=a["name"], name_ar=a["name_ar"], provider_key="mock"))

    if Destination.query.count() == 0:
        for d in DESTINATIONS_SEED:
            db.session.add(Destination(**d))

    if User.query.filter_by(email="admin@travel-ai.local").first() is None:
        admin = User(full_name="Admin", email="admin@travel-ai.local", is_admin=True)
        admin.set_password("ChangeMe123!")
        db.session.add(admin)

    db.session.commit()


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_ENV") != "production")

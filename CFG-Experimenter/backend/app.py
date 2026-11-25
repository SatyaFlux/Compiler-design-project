"""
CFG Experimenter - Flask Application Entry Point.
"""
from flask import Flask, jsonify
from flask_cors import CORS
from database.seed import seed_db
from routes.compiler_routes import compiler_bp
from routes.grammar_routes import grammar_bp
from routes.experiment_routes import experiment_bp
from routes.quiz_routes import quiz_bp


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)

    seed_db()

    app.register_blueprint(compiler_bp)
    app.register_blueprint(grammar_bp)
    app.register_blueprint(experiment_bp)
    app.register_blueprint(quiz_bp)

    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({
            "status": "ok",
            "app": "CFG Experimenter",
            "version": "1.0.0",
        })

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(host="127.0.0.1", port=5000, debug=True)

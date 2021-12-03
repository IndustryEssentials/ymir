import sys

from src.app import create_connexion_app

connexion_app = create_connexion_app()

if __name__ == "__main__":
    port = 9099 if len(sys.argv) <= 1 else int(sys.argv[1])
    connexion_app.run(host="0.0.0.0", port=port, debug=True)

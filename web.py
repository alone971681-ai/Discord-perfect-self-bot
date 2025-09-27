from app import app

# Export the app for Gunicorn to use
application = app  # Alias for compatibility

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
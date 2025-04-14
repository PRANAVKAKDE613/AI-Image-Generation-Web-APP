from flask import Flask, render_template, request, send_file
import os
from dotenv import load_dotenv
import replicate
import requests
from io import BytesIO

load_dotenv()  # Loads environment variables from a .env file

app = Flask(__name__)  # Define your Flask app object

@app.route("/", methods=["GET", "POST"])
def index():
    image_url = None
    error_message = None

    if request.method == "POST":
        prompt = request.form["prompt"]

        try:
            # Generate the image
            output = replicate.run(
                os.getenv("MODEL_VERSION"),
                input={"prompt": prompt}
            )
            print("Output:", output)  # For debugging

            # Check if the output is a list of URLs or something else
            if isinstance(output, list):
                image_url = output[0]  # First image from the list
            elif hasattr(output, 'url'):  # If it's a file-like object with a URL attribute
                image_url = output.url  # Assuming the object has a `url` attribute
            else:
                error_message = "Unexpected output format from Replicate API."

        except Exception as e:
            error_message = f"Error generating image: {str(e)}"

    return render_template("index.html", image_url=image_url, error=error_message)

@app.route("/download")
def download_image():
    # Fetch the image from the URL
    image_url = request.args.get("image_url")

    if not image_url:
        return "No image found to download."

    # Download the image as a binary stream
    response = requests.get(image_url)
    image_bytes = BytesIO(response.content)

    return send_file(image_bytes, as_attachment=True, download_name="generated_image.png", mimetype="image/png")

if __name__ == "__main__":
    app.run(debug=True)  # Start the Flask app

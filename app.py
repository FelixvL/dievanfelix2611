import os
from flask import Flask, render_template, request
from dotenv import load_dotenv

from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import AnalysisInput
from azure.core.exceptions import AzureError
from azure.core.credentials import AzureKeyCredential

load_dotenv()

app = Flask(__name__)

load_dotenv()

endpoint = os.getenv("ENDPOINT")
analyzer_id = os.getenv("ANALYZER")
key = os.getenv("CONTENT_UNDERSTANDING_KEY")

client = ContentUnderstandingClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(key),
    api_version="2025-11-01"
)


@app.route("/", methods=["GET", "POST"])
def index():

    description = None
    tags = []
    error = None

    if request.method == "POST":

        file = request.files.get("image")

        if not file or not file.filename:
            error = "Selecteer eerst een afbeelding."

        else:
            try:
                # Lees de geüploade afbeelding
                file_bytes = file.read()

                # Analyseer met Azure
                poller = client.begin_analyze(
                    analyzer_id=analyzer_id,
                    inputs=[AnalysisInput(data=file_bytes)]
                )

                result = poller.result()
                print(poller.usage)
                # Verwerk de resultaten
                fields = result.contents[0].fields

                if "Description" in fields:
                    description = fields["Description"].value_string

                if "Tags" in fields:
                    tags = [
                        tag.value_string
                        for tag in fields["Tags"].value_array
                    ]

            except AzureError as ex:
                error = f"Azure fout: {ex}"

            except Exception as ex:
                error = f"Fout: {ex}"

    return render_template(
        "index.html",
        description=description,
        tags=tags,
        error=error
    )


if __name__ == "__main__":
    app.run(debug=True)
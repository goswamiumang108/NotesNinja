# Python Backend for NotesNinja 

from os import path, remove, rmdir, removedirs, mkdir, getenv
from datetime import datetime as dt
from dotenv import load_dotenv
import google.generativeai as genai
from flask import *
from flask_cors import CORS
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders.doc_intelligence import AzureAIDocumentIntelligenceLoader
from langchain_core.prompts.prompt import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI


app = Flask(__name__, template_folder="templates", static_folder="static")

load_dotenv(dotenv_path=".env")

CognitiveServices_Endpoint = getenv("CognitiveServices_Endpoint")
CognitiveServices_APIKey = getenv("CognitiveServices_APIKey")

# Defining some main integral values and variables
google_api_key = getenv("GOOGLE_API_KEY")
genai.configure(api_key=google_api_key)

LLM = GoogleGenerativeAI(model="gemini-1.5-pro-latest", google_api_key=google_api_key,
		convert_system_message_to_human=True)

UserRequests_Info: dict = {}


# noinspection PyUnresolvedReferences
@app.route('/')
def home():
	return render_template("index.html")


@app.errorhandler(404)
def Error404(e):
	return render_template("404.html"), 404


@app.errorhandler(503)
def Error503(e):
	return render_template("503.html"), 503


@app.route(rule='/uploads', methods=['POST'])
def receive_FormData():
	try:
		pdf_file = request.files['pdf-file']
		syllabus_topics = request.form['syllabus-topics']
		
		pdf_file_id = "".join(ele for ele in str(dt.now()) if ele.isalnum())
		saved_pdf_file_path = str(path.join(path.relpath("./uploads/"), pdf_file_id)) + ".pdf"
		
		if not path.lexists("./uploads/"):
			mkdir("./uploads/")
		pdf_file.save(dst=saved_pdf_file_path)
		
		UserRequests_Info["saved_pdf_file_path"] = saved_pdf_file_path
		UserRequests_Info["syllabus_topics"] = syllabus_topics
		UserRequests_Info["pdf_file_id"] = pdf_file_id
	except Exception as e:
		return "Error: " + str(e)
	else:
		return "success"


@app.route(rule='/process-docs', methods=['POST'])
def Process_The_Docs():
	# noinspection PyBroadException
	try:
		loader = AzureAIDocumentIntelligenceLoader(api_endpoint=CognitiveServices_Endpoint,
				api_key=CognitiveServices_APIKey,
				file_path=UserRequests_Info["saved_pdf_file_path"],
				api_model="prebuilt-layout")
		documents = loader.load()
		
		prompt_template = \
			f"""
		Write a summary on the following study material as per the syllabus topics provided below:
		-----------------------------------
		SYLLABUS TOPICS: {UserRequests_Info["syllabus_topics"]}
		""" + \
			"""
		-----------------------------------
		STUDY MATERIAL: {text}
		-----------------------------------
		CONCISE SUMMARY:
		"""
		prompt = PromptTemplate.from_template(prompt_template)
		
		chain = load_summarize_chain(llm=LLM, prompt=prompt, chain_type="stuff", input_key="input_docs",
				output_key="output_text")
		
		result = chain.invoke(input={"input_docs": documents}, return_only_outputs=True)
		
		if not path.lexists(path="./generated-notes"):
			mkdir(path="./generated-notes/")
		
		Saved_Response_TxT_File_Path = "./generated-notes/" + UserRequests_Info["pdf_file_id"] + ".txt"
		UserRequests_Info["Saved_Response_TxT_File_Path"] = Saved_Response_TxT_File_Path
		
		with open(file=Saved_Response_TxT_File_Path, encoding="utf-8", mode="w+") as file:
			file.write(result["output_text"])
		
		# noinspection PyBroadException
		try:
			rmdir("./uploads")
			removedirs("./uploads")
			remove("./uploads")
		except:
			pass
	except Exception as e:
		return "Error: " + str(e)
	else:
		return "success"


@app.route(rule='/download-generated-notes', methods=['GET'])
def ReturnTheGeneratedNotes():
	return send_file(path_or_file=UserRequests_Info["Saved_Response_TxT_File_Path"],
			download_name="NotesNinja_GeneratedNotes_" + UserRequests_Info['pdf_file_id'] + ".txt")


if __name__ == '__main__':
	app.run(host="0.0.0.0", debug=True, load_dotenv=True)
	CORS(app)
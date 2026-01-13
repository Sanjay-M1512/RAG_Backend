import os
import uuid
from datetime import timedelta, datetime
from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
from pypdf import PdfReader
import docx
from sentence_transformers import SentenceTransformer
from groq import Groq
from pinecone import Pinecone

# -----------------------------
# Load ENV
# -----------------------------
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# -----------------------------
# Flask Init
# -----------------------------
app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)
jwt = JWTManager(app)

# -----------------------------
# MongoDB Init
# -----------------------------
client = MongoClient(MONGO_URI)
db = client["RAG"]

users_col = db["users"]
stateboard_col = db["stateboard"]
cbse_col = db["cbse"]
documents_col = db["documents"]              # Syllabus docs
user_documents_col = db["user_documents"]    # 🔹 NEW: User uploaded docs

# -----------------------------
# Pinecone Init (NEW SDK)
# -----------------------------
pc = Pinecone(api_key=PINECONE_API_KEY)
INDEX_NAME = "rag-documents"

if INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=INDEX_NAME,
        dimension=384,
        metric="cosine",
        spec={"serverless": {"cloud": "aws", "region": "us-east-1"}}
    )

index = pc.Index(INDEX_NAME)

# -----------------------------
# Embeddings & Groq
# -----------------------------
embedder = SentenceTransformer("all-MiniLM-L6-v2")
groq_client = Groq(api_key=GROQ_API_KEY)

# -----------------------------
# Utilities (RAG)
# -----------------------------
def load_document(file_path):
    text = ""
    if file_path.endswith(".pdf"):
        reader = PdfReader(file_path)
        for page in reader.pages:
            text += page.extract_text() or ""
    elif file_path.endswith(".docx"):
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    elif file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    return text


def chunk_text(text, chunk_size=500, overlap=100):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks


def get_embedding(text):
    return embedder.encode(text).tolist()


def store_chunks(chunks, document_id):
    vectors = []
    for i, chunk in enumerate(chunks):
        vectors.append({
            "id": f"{document_id}-{i}",
            "values": get_embedding(chunk),
            "metadata": {
                "text": chunk,
                "document_id": document_id
            }
        })
    index.upsert(vectors)


def query_document(query, document_id, top_k=5):
    query_embedding = get_embedding(query)
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True,
        filter={"document_id": {"$eq": document_id}}
    )
    return [match["metadata"]["text"] for match in results["matches"]]


def generate_answer(query, retrieved_chunks):
    if not retrieved_chunks:
        return "Answer not found in the document."

    context = "\n\n".join(retrieved_chunks)

    prompt = f"""
You are a document-based assistant.

Rules:
- Answer ONLY using the provided context.
- If the answer is not present in the context, respond exactly with:
  "Answer not found in the document."

Context:
{context}

Question: {query}
Answer:
"""

    completion = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return completion.choices[0].message.content.strip()

# -----------------------------
# AUTH
# -----------------------------
@app.route("/signup", methods=["POST"])
def signup():
    data = request.json

    if users_col.find_one({"email": data["email"]}):
        return jsonify({"error": "Email already exists"}), 400

    user = {
        "username": data["username"],
        "email": data["email"],
        "password": data["password"],  # ⚠ Hash in production
        "class": data["class"],
        "board": data["board"],
        "group": data.get("group"),
        "role": "student"
    }

    users_col.insert_one(user)
    return jsonify({"message": "User registered successfully"}), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user = users_col.find_one({"email": data["email"], "password": data["password"]})

    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_access_token(identity=str(user["_id"]))
    return jsonify({"access_token": token})


@app.route("/logout", methods=["POST"])
def logout():
    return jsonify({"message": "Logged out successfully"})

# -----------------------------
# USER PROFILE (JWT ONLY)
# -----------------------------
@app.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    user = users_col.find_one({"_id": ObjectId(user_id)})

    return jsonify({
        "username": user["username"],
        "email": user["email"],
        "class": user["class"],
        "board": user["board"],
        "group": user.get("group")
    })


@app.route("/update-profile", methods=["PUT"])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    data = request.json

    users_col.update_one({"_id": ObjectId(user_id)}, {"$set": data})
    return jsonify({"message": "Profile updated"})

# -----------------------------
# CURRICULUM (PUBLIC)
# -----------------------------
@app.route("/stateboard", methods=["GET"])
def stateboard():
    class_ = request.args.get("class")
    group = request.args.get("group")

    query = {"class": class_}
    if group:
        query["group"] = group

    subjects = stateboard_col.find(query, {"_id": 0, "subject": 1})
    return jsonify(list(subjects))


@app.route("/cbse", methods=["GET"])
def cbse():
    class_ = request.args.get("class")
    group = request.args.get("group")

    query = {"class": class_}
    if group:
        query["group"] = group

    subjects = cbse_col.find(query, {"_id": 0, "subject": 1})
    return jsonify(list(subjects))


@app.route("/groups", methods=["GET"])
def groups():
    board = request.args.get("board")
    class_ = request.args.get("class")

    col = stateboard_col if board == "stateboard" else cbse_col
    groups = col.distinct("group", {"class": class_})
    return jsonify(groups)

# -----------------------------
# SUBJECT → DOCUMENT (PUBLIC)
# -----------------------------
@app.route("/subject-document", methods=["GET"])
def subject_document():
    board = request.args.get("board")
    class_ = request.args.get("class")
    subject = request.args.get("subject")
    group = request.args.get("group")

    col = stateboard_col if board == "stateboard" else cbse_col

    query = {"class": class_, "subject": subject}
    if group:
        query["group"] = group

    record = col.find_one(query)
    if not record:
        return jsonify({"error": "Document not found"}), 404

    return jsonify({"document_id": record["document_id"]})

# -----------------------------
# USER DOCUMENT UPLOAD (NEW)
# -----------------------------
@app.route("/upload-user", methods=["POST"])
def upload_user_document():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    email = request.form.get("email")

    if not email:
        return jsonify({"error": "email is required"}), 400

    user = users_col.find_one({"email": email})
    if not user:
        return jsonify({"error": "User not found"}), 404

    os.makedirs("uploads", exist_ok=True)
    path = os.path.join("uploads", file.filename)
    file.save(path)

    text = load_document(path)
    chunks = chunk_text(text)

    document_id = str(uuid.uuid4())
    store_chunks(chunks, document_id)

    user_documents_col.insert_one({
        "document_id": document_id,
        "filename": file.filename,
        "uploaded_by": {
            "email": email,
            "user_id": str(user["_id"])
        },
        "uploaded_at": datetime.utcnow()
    })

    return jsonify({
        "message": "User document uploaded successfully",
        "document_id": document_id
    })

# -----------------------------
# LIST USER DOCUMENTS
# -----------------------------
@app.route("/user/documents", methods=["GET"])
def get_user_documents():
    email = request.args.get("email")

    if not email:
        return jsonify({"error": "email is required"}), 400

    docs = user_documents_col.find(
        {"uploaded_by.email": email},
        {"_id": 0}
    )

    return jsonify(list(docs))

# -----------------------------
# ASK USER DOCUMENT (NEW)
# -----------------------------
@app.route("/ask-user", methods=["POST"])
def ask_user_document():
    data = request.json

    email = data.get("email")
    document_id = data.get("document_id")
    query = data.get("query")

    if not email or not document_id or not query:
        return jsonify({
            "error": "email, document_id, and query are required"
        }), 400

    user = users_col.find_one({"email": email})
    if not user:
        return jsonify({"error": "User not found"}), 404

    doc = user_documents_col.find_one({
        "document_id": document_id,
        "uploaded_by.email": email
    })

    if not doc:
        return jsonify({"error": "You do not have access to this document"}), 403

    retrieved_chunks = query_document(query, document_id)
    answer = generate_answer(query, retrieved_chunks)

    return jsonify({
        "document_id": document_id,
        "answer": answer
    })

# -----------------------------
# ASK (SYLLABUS RAG)
# -----------------------------
@app.route("/ask", methods=["POST"])
def ask():
    data = request.json

    email = data.get("email")
    subject = data.get("subject")
    prompt = data.get("query")

    if not email or not subject or not prompt:
        return jsonify({
            "error": "email, subject, and query are required"
        }), 400

    user = users_col.find_one({"email": email})
    if not user:
        return jsonify({"error": "User not found"}), 404

    user_class = str(user["class"]).strip()
    user_board = user["board"].strip()
    user_group = user.get("group")
    if user_group:
        user_group = user_group.strip()

    if user_board == "stateboard":
        col = stateboard_col
    elif user_board == "cbse":
        col = cbse_col
    else:
        return jsonify({"error": "Invalid board in user profile"}), 400

    query = {
        "class": user_class,
        "subject": subject.strip()
    }

    if user_group:
        query["group"] = user_group

    record = col.find_one(query)
    if not record:
        return jsonify({
            "document_id": None,
            "answer": "Answer not found in the document."
        })

    document_id = record["document_id"]
    retrieved_chunks = query_document(prompt, document_id)
    answer = generate_answer(prompt, retrieved_chunks)

    return jsonify({
        "document_id": document_id,
        "answer": answer
    })

# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

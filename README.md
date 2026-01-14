# 📘 RAG-Based Curriculum Learning API

**Base URL:**\
http://13.60.138.201

This backend enables students to learn strictly from their syllabus
books using **RAG (Retrieval Augmented Generation)** with **MongoDB +
Pinecone + Groq**, preventing hallucination and ensuring curriculum
alignment.

------------------------------------------------------------------------

## 🔐 Authentication (Students)

### 📝 1. Signup

**POST** `/signup`

Registers a new student.

**Request Body (JSON):**

```json
{
  "username": "Sanjay",
  "email": "sanjay@gmail.com",
  "password": "123456",
  "class": "10",
  "board": "stateboard",
  "group": null
}
```

------------------------------------------------------------------------

### 🔑 2. Login

**POST** `/login`

```json
{
  "email": "sanjay@gmail.com",
  "password": "123456"
}
```

------------------------------------------------------------------------

### 🚪 3. Logout

**POST** `/logout`

------------------------------------------------------------------------

## 👤 Student Profile (JWT Protected)

### 📄 4. Get Profile

**GET** `/profile`  
Headers: `Authorization: Bearer <JWT>`

------------------------------------------------------------------------

### ✏️ 5. Update Profile

**PUT** `/update-profile`  
Headers: `Authorization: Bearer <JWT>`

------------------------------------------------------------------------

## 📚 Curriculum Endpoints

### 📘 6. State Board Subjects

**GET** `/stateboard?class=10`

### 📗 7. CBSE Subjects

**GET** `/cbse?class=10`

### 👥 8. Get Groups

**GET** `/groups?board=stateboard&class=11`

------------------------------------------------------------------------

## 🔗 Subject → Document Mapping

### 📄 9. Get Document ID for Subject

**GET** `/subject-document?board=stateboard&class=10&subject=Biology`

------------------------------------------------------------------------

## 📤 Document Upload (Syllabus)

### 📥 10. Upload Book

**POST** `/upload`

------------------------------------------------------------------------

## 📂 Document Management

### 📑 11. List All Documents

**GET** `/documents`

### 🗑 12. Delete Document

**DELETE** `/document/<document_id>`

------------------------------------------------------------------------

## 🤖 RAG Question Answering (Syllabus)

### ❓ 13. Ask from Syllabus

**POST** `/ask`

```json
{
  "email": "sanjay@gmail.com",
  "subject": "Biology",
  "query": "What is photosynthesis?"
}
```

------------------------------------------------------------------------

## 📝 Personal Notes (User Documents)

### 📤 14. Upload User Notes

**POST** `/upload-user`  

```form-data
file: my_notes.pdf
email: sanjay@gmail.com
```

------------------------------------------------------------------------

### 📂 15. List User Documents

**GET** `/user/documents?email=sanjay@gmail.com`

------------------------------------------------------------------------

### 🤖 16. Ask From Personal Notes

**POST** `/ask-user`

```json
{
  "email": "sanjay@gmail.com",
  "document_id": "xxxx",
  "query": "Explain Newton's second law"
}
```

------------------------------------------------------------------------

## 🔐 Normal User (User2) Authentication

### 📝 17. Register User2

**POST** `/user2/register`

```json
{
  "email": "user2@gmail.com",
  "password": "123456"
}
```

------------------------------------------------------------------------

### 🔑 18. Login User2

**POST** `/user2/login`

------------------------------------------------------------------------

### 🚪 19. Logout User2

**POST** `/user2/logout`

------------------------------------------------------------------------

## 👤 User2 Profile (JWT Protected)

### 📄 20. Get Profile

**GET** `/user2/profile`  
Headers: `Authorization: Bearer <JWT>`

------------------------------------------------------------------------

### ✏️ 21. Update Profile

**PUT** `/user2/update-profile`  
Headers: `Authorization: Bearer <JWT>`

------------------------------------------------------------------------

## 🗑 User2 Document Management

### ❌ 22. Delete Own Document

**DELETE** `/user2/document/<document_id>`  
Headers: `Authorization: Bearer <JWT>`

------------------------------------------------------------------------

## ✏️ Student Personal Document Control

### 📝 23. Update Own Document

**PUT** `/update-document/<document_id>`  
Headers: `Authorization: Bearer <JWT>`

------------------------------------------------------------------------

### 🗑 24. Delete Own Document

**DELETE** `/delete-user-document/<document_id>`  
Headers: `Authorization: Bearer <JWT>`

------------------------------------------------------------------------

## 🌍 Deployment

Hosted on **AWS EC2** with Nginx + systemd  
Base URL:

    http://13.60.138.201

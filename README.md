# 📘 RAG-Based Curriculum Learning API

**Base URL:**\
http://13.60.138.201

This backend enables students to learn strictly from their syllabus
books using **RAG (Retrieval Augmented Generation)** with **MongoDB +
Pinecone + Groq**, preventing hallucination and ensuring curriculum
alignment.

------------------------------------------------------------------------

## 🔐 Authentication

### 📝 1. Signup

**POST** `/signup`

Registers a new student.

**Request Body (JSON):**

``` json
{
  "username": "Sanjay",
  "email": "sanjay@gmail.com",
  "password": "123456",
  "class": "10",
  "board": "stateboard",
  "group": null
}
```

**Response:**

``` json
{
  "message": "User registered successfully"
}
```

------------------------------------------------------------------------

### 🔑 2. Login

**POST** `/login`

Authenticates a user and returns JWT.

**Request Body (JSON):**

``` json
{
  "email": "sanjay@gmail.com",
  "password": "123456"
}
```

**Response:**

``` json
{
  "access_token": "JWT_TOKEN_HERE"
}
```

------------------------------------------------------------------------

### 🚪 3. Logout

**POST** `/logout`

**Response:**

``` json
{
  "message": "Logged out successfully"
}
```

------------------------------------------------------------------------

## 👤 User Profile (JWT Protected)

### 📄 4. Get Profile

**GET** `/profile`\
**Headers:**

    Authorization: Bearer <JWT_TOKEN>

**Response:**

``` json
{
  "username": "Sanjay",
  "email": "sanjay@gmail.com",
  "class": "10",
  "board": "stateboard",
  "group": null
}
```

------------------------------------------------------------------------

### ✏️ 5. Update Profile

**PUT** `/update-profile`\
**Headers:**

    Authorization: Bearer <JWT_TOKEN>

**Request Body (JSON):**

``` json
{
  "class": "11",
  "group": "Biology"
}
```

**Response:**

``` json
{
  "message": "Profile updated"
}
```

------------------------------------------------------------------------

## 📚 Curriculum Endpoints

### 📘 6. State Board Subjects

**GET** `/stateboard?class=10`

Optional for 11/12:

    /stateboard?class=11&group=Biology

------------------------------------------------------------------------

### 📗 7. CBSE Subjects

**GET** `/cbse?class=10`

or:

    /cbse?class=12&group=Commerce

------------------------------------------------------------------------

### 👥 8. Get Groups for 11/12

**GET** `/groups?board=stateboard&class=11`

------------------------------------------------------------------------

## 🔗 Subject → Document Mapping

### 📄 9. Get Document ID for Subject

**GET** `/subject-document`

**Query Params:**

    board=stateboard
    class=10
    subject=Biology

**Response:**

``` json
{
  "document_id": "f4b1c2c1-92ab-4d71-acde-cc44a20fa9e0"
}
```

------------------------------------------------------------------------

## 📤 Document Upload

### 📥 10. Upload Book / Notes

**POST** `/upload`\
**Form Data:**

  Key       Type   Value
  --------- ------ -------------
  file      File   biology.pdf
  class     Text   10
  board     Text   stateboard
  subject   Text   Biology
  group     Text   (optional)

**Response:**

``` json
{
  "message": "Document uploaded",
  "document_id": "f4b1c2c1-92ab-4d71-acde-cc44a20fa9e0"
}
```

------------------------------------------------------------------------

## 📂 Document Management

### 📑 11. List All Documents

**GET** `/documents`

------------------------------------------------------------------------

### 🗑 12. Delete Document

**DELETE** `/document/<document_id>`

------------------------------------------------------------------------

## 🤖 RAG Question Answering

### ❓ 13. Ask Question from Syllabus

**POST** `/ask`

**Request Body (JSON):**

``` json
{
  "email": "sanjay@gmail.com",
  "subject": "Biology",
  "query": "What is photosynthesis?"
}
```

**Response:**

``` json
{
  "document_id": "f4b1c2c1-92ab-4d71-acde-cc44a20fa9e0",
  "answer": "Photosynthesis is the process by which green plants make their own food using sunlight..."
}
```

If the answer is not in the document:

``` json
{
  "document_id": "f4b1c2c1-92ab-4d71-acde-cc44a20fa9e0",
  "answer": "Answer not found in the document."
}
```

------------------------------------------------------------------------

## 🌍 Deployment

Hosted on **AWS EC2** with Nginx + systemd\
Base URL:

    http://13.60.138.201

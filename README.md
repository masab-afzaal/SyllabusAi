# 📚 Syllabus AI

**Syllabus AI** is an AI-powered academic assistant that transforms dense, unstructured syllabus documents into personalized, interactive study hubs. Designed to help students manage their time, stay organized, and reduce academic stress, Syllabus AI makes course planning smarter and easier.

---

## 🚀 Inspiration

Every student knows the struggle of digging through pages of a syllabus to find important dates or policies. We’ve all missed office hours or misunderstood grading rubrics. These experiences led us to a bold idea:

> What if we could make syllabi readable, actionable, and interactive using AI?

Syllabus AI aligns with **UN SDG 4.4**, supporting youth by providing a tool for better time and project management.

---

## 💡 Features

- **🎯 Intelligent Summarization**  
  Extracts key information like instructor contacts, grading breakdowns, and course goals.

- **📆 Dynamic Deadlines & Alerts**  
  Automatically builds a calendar of due dates with push notifications.

- **🧠 Personalized Study Plan**  
  Suggests weekly schedules based on assignment weights and course timelines.

- **💬 Interactive Q&A Chat**  
  Ask syllabus-specific questions and get instant answers powered by Retrieval-Augmented Generation (RAG).

---

## 🏗️ Tech Stack

| Layer         | Technology        |
| ------------- | ---------------- |
| Frontend      | React        |
| Backend       | Django            |
| Database      | PostgreSQL       |
| AI Core       | Large Language Model (LLM), RAG, Vector DB |
| Deployment    | Cloud Platform (e.g., Render/Heroku/EC2) |

---

## ⚙️ How It Works

1. **Upload PDF** of your syllabus.
2. **AI Pipeline** extracts, parses, and summarizes important info.
3. **Deadlines are auto-populated** in a calendar.
4. **Q&A Bot** answers your syllabus-related queries in real-time.

---

## 🧗 Challenges We Overcame

- **Unstructured Data**: Each syllabus is different. Regex and basic parsing failed. We solved it using a fine-tuned LLM and smart prompt engineering.
- **Accuracy & Trust**: A secondary validation layer cross-checks extracted data for 100% reliability.
- **UX of a New Tool**: Iteratively improved UI/UX based on early user feedback.

---

## 🏆 Achievements

- Developed a robust AI pipeline for real-world academic documents.
- Built a truly helpful, user-first tool that addresses a real problem.
- Created an end-to-end academic assistant, not just a summarizer.

---

## 🎓 Lessons Learned

- Prompt engineering is crucial for AI accuracy and usability.
- User feedback should drive feature development.
- For mission-critical data (like deadlines), reliability is non-negotiable.

---

## 🔮 Future Plans

- **LMS Integration** (Canvas, Blackboard, etc.)
- **Document Expansion**: Apply same tech to research papers, legal docs, etc.
- **Complete Student Assistant**: Project planning, time blocking, group study matching, and more.

---

## 🤖 AI & ML Details

- **PDF Parsing** using open-source libraries
- **Entity Extraction** via fine-tuned LLMs
- **Vector Search** + **RAG** for Q&A
- **Prompt Engineering** for dynamic and accurate responses

---

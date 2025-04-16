from fastapi import APIRouter
from pydantic import BaseModel
import random

router = APIRouter(tags=["quiz"])

async def get_quiz_collection():
    from db import init_db
    return init_db().get("quiz_collection", init_db()["items_collection"].database["quiz"])

# Initialize questions in the database if they don't exist
async def init_questions():
    collection = await get_quiz_collection()
    count = await collection.count_documents({})
    
    if count == 0:
        default_questions = [
            {
                "id": 1,
                "text": "What command lists directory contents?",
                "options": ["ls", "cd", "rm", "pwd"],
                "correct": "ls"
            },
            {
                "id": 2,
                "text": "Which command searches for text in files?",
                "options": ["find", "grep", "locate", "cat"],
                "correct": "grep"
            },
            {
                "id": 3,
                "text": "What changes file permissions?",
                "options": ["chmod", "chown", "mv", "cp"],
                "correct": "chmod"
            },
            {
                "id": 4,
                "text": "Which command displays the current directory?",
                "options": ["dir", "pwd", "path", "where"],
                "correct": "pwd"
            },
            {
                "id": 5,
                "text": "What removes a file?",
                "options": ["rm", "del", "erase", "unlink"],
                "correct": "rm"
            }
        ]
        await collection.insert_many(default_questions)

game_state = {"high_score": 0}

class AnswerSubmission(BaseModel):
    id: int
    answer: str
    score: int = 0

# god would hate me for not dockerizing this repo
@router.get("/question")
async def get_question():
    await init_questions()  # Ensure questions exist
    collection = await get_quiz_collection()
    
    # Get all question IDs
    questions = []
    async for doc in collection.find({}, {"id": 1}):
        questions.append(doc["id"])
    
    if not questions:
        return {"error": "No questions available"}
    
    # Select a random question ID
    random_id = random.choice(questions)
    question = await collection.find_one({"id": random_id})
    
    if question:
        # Remove the MongoDB _id field and correct answer
        question.pop("_id", None)
        correct = question.pop("correct", None)
        
        return question
    
    return {"error": "Failed to retrieve question"}

@router.post("/answer")
async def submit_answer(data: AnswerSubmission):
    collection = await get_quiz_collection()
    question = await collection.find_one({"id": data.id})
    
    if not question:
        return {"error": "Invalid question ID"}

    is_correct = data.answer == question["correct"]
    if is_correct:
        data.score += 10
        if data.score > game_state["high_score"]:
            game_state["high_score"] = data.score

    return {
        "is_correct": is_correct,
        "correct_answer": question["correct"],
        "score": data.score,
        "high_score": game_state["high_score"]
    }

@router.get("/highscore")
async def get_highscore():
    return {"high_score": game_state["high_score"]}
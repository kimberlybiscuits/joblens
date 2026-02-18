from fastapi import APIRouter, Request                                                      
from fastapi.responses import HTMLResponse                                                  
from app.database import get_db                                                             
from app.ollama_client import generate                                                      

import re                                                                                   

def strip_html(text: str) -> str:                                                           
    if not text:                                                                            
        return "Not provided"                                                               
    clean = re.sub(r'<[^>]+>', ' ', text)                                                   
    clean = re.sub(r'\s+', ' ', clean).strip()                                              
    return clean[:1500]  # truncate so we don't overwhelm Phi-3                             

router = APIRouter()

@router.post("/jobs/{job_id}/cover-letter", response_class=HTMLResponse)
async def cover_letter(job_id: int, request: Request):
    conn = get_db()
    job = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    profile = conn.execute("SELECT * FROM profiles LIMIT 1").fetchone()
    conn.close()

    prompt = f"""You are a job application coach. Analyse this job and the candidate's      
  profile, then output two things:                                                            
                                                                                              
  1. Key requirements from the job (bullet points, max 5)
  2. Personalised talking points for a cover letter based on the candidate's background
  (bullet points, max 5)

  Be specific. Reference actual skills, experience, and details from both the job and the
  candidate.

  Job title: {job['title']}
  Company: {job['company']}
  Location: {job['location']}
  Description: {strip_html(job['description'])}
  Tags: {job['tags'] or 'Not provided'}

  Candidate:
  Name: {profile['name']}
  Current title: {profile['current_title']}
  Years experience: {profile['years_experience']}
  Skills: {profile['skills']}
  Education: {profile['education']}
  Languages: {profile['languages']}
  Bio: {profile['bio']}"""
    
    result = await generate(prompt)

    return f"<div class='prose max-w-none'><pre class='whitespace-pre-wrap'>{result}</pre></div>"
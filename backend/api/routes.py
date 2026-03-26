from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List
import os

from core.parser import StatementParser
from core.math_utils import FinancialEngine
from core.config import Config
from agents.portfolio_xray import PortfolioXRay
from agents.health_score import MoneyHealthScore
from agents.fire_planner import FIREPlanner
import shutil

# Debug: Print Config values
print(f"[ROUTES-INIT] Config.OPENAI_KEY: {Config.OPENAI_KEY[:30] if Config.OPENAI_KEY else 'NONE'}...")
print(f"[ROUTES-INIT] os.getenv('OPENAI_API_KEY'): {os.getenv('OPENAI_API_KEY', 'NOT SET')[:30]}...")

router = APIRouter()

# Initialize global tools
try:
    parser = StatementParser()
except Exception as e:
    print(f"Warning: StatementParser initialization failed: {e}")
    parser = None

engine = FinancialEngine()

# Initialize OpenAI client lazily
openai_client = None
def get_openai_client():
    global openai_client
    if openai_client is None and Config.OPENAI_KEY:
        try:
            import os
            # Set API key in environment for OpenAI to pick up
            os.environ['OPENAI_API_KEY'] = Config.OPENAI_KEY
            from openai import OpenAI
            print(f"[ROUTES] Creating OpenAI client from env...")
            # Initialize without passing api_key - let it read from environment
            openai_client = OpenAI()
            print("✓ [ROUTES] OpenAI client initialized successfully")
        except Exception as e:
            print(f"[ROUTES] Error creating OpenAI client: {e}")
            import traceback
            traceback.print_exc()
    return openai_client

AGENT_SYSTEM_PROMPT = (
    "You are Lakshya — an Indian personal finance mentor. "
    "Explain retirement, mutual funds, taxes, and insurance with empathy, "
    "use INR examples, and keep responses concise with actionable steps."
)


class ChatMessage(BaseModel):
    role: str
    content: str


class AgentChatRequest(BaseModel):
    messages: List[ChatMessage]


def _extract_response_text(response) -> str:
    if not response:
        return ""
    chunks = []
    for block in getattr(response, "output", []) or []:
        for item in getattr(block, "content", []) or []:
            text = getattr(item, "text", None)
            if text:
                chunks.append(text)
    if chunks:
        return "\n".join(chunks).strip()
    fallback = getattr(response, "output_text", "")
    return fallback.strip()

@router.post("/analyze-portfolio")
async def analyze_portfolio(file: UploadFile = File(...)):
    """
    Endpoint 1: The 'X-Ray'
    Upload CAMS PDF -> Get Overlap, XIRR, and Savings Leak.
    """
    if not parser:
        raise HTTPException(status_code=503, detail="Portfolio parser not available. Check LlamaCloud API key.")
    
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # 1. Parse using LlamaCloud
        raw_data = await parser.parse_statement(temp_path)
        
        # 2. Run X-Ray Agent
        xray = PortfolioXRay(raw_data['holdings'])
        overlap = xray.calculate_overlap_matrix()
        leak = xray.detect_regular_to_direct_savings()
        
        # 3. Calculate XIRR
        xirr = engine.calculate_xirr(raw_data['transactions'])

        return {
            "portfolio_value": raw_data['total_value'],
            "xirr": f"{round(xirr * 100, 2)}%",
            "overlap_report": overlap,
            "annual_savings_potential": leak['annual_leak'],
            "holdings_count": len(raw_data['holdings'])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path): os.remove(temp_path)

@router.post("/get-health-score")
async def get_health_score(user_data: dict):
    """
    Endpoint 2: The 'Health Meter'
    Takes portfolio metrics + user profile to give the 0-100 score.
    """
    # portfolio_metrics come from the /analyze-portfolio output
    health_agent = MoneyHealthScore(
        portfolio_metrics=user_data['metrics'],
        profile_data=user_data['profile']
    )
    return health_agent.get_comprehensive_score()

@router.post("/project-fire")
async def project_fire(params: dict):
    """
    Endpoint 3: The 'Spatial Path'
    Runs Monte Carlo simulation for the 3D visualization.
    """
    planner = FIREPlanner(
        current_savings=params['current_savings'],
        monthly_invest=params['monthly_sip'],
        target_corpus=params['target']
    )
    return planner.run_monte_carlo()

@router.post("/mentor-chat")
async def mentor_chat(payload: AgentChatRequest):
    """Connect the frontend chatbot to the Lakshya OpenAI mentor."""
    print(f"[MENTOR-CHAT] Called. Config.OPENAI_KEY: {Config.OPENAI_KEY[:30] if Config.OPENAI_KEY else 'NONE'}...")
    client = get_openai_client()
    print(f"[MENTOR-CHAT] Client object: {client}")
    if not Config.OPENAI_KEY or not client:
        print(f"[MENTOR-CHAT] ERROR - Config.OPENAI_KEY={bool(Config.OPENAI_KEY)}, client={client}")
        raise HTTPException(status_code=500, detail="OpenAI API key is not configured or client failed to initialize.")

    history = []
    for msg in payload.messages:
        if msg.role not in {"user", "assistant"}:
            continue
        content = (msg.content or "").strip()
        if content:
            history.append({"role": msg.role, "content": content})

    if not history or history[-1]['role'] != 'user':
        raise HTTPException(status_code=400, detail="Last message must come from the user.")

    request_messages = [{"role": "system", "content": AGENT_SYSTEM_PROMPT}]
    request_messages.extend(history[-8:])

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=request_messages,
            temperature=0.6,
            max_tokens=600,
        )
        reply_text = response.choices[0].message.content if response.choices else ""
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Agent error: {exc}") from exc

    if not reply_text:
        raise HTTPException(status_code=502, detail="Agent returned an empty response.")

    return {"reply": reply_text}
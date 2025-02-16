from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from gradio_client import Client
from pydantic import BaseModel, Field
import logging
from typing import Union

# Configure logging
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.basicConfig(level=logging.INFO)

app = FastAPI()

# Remove or comment out this line if you don't need static files
# app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# Initialize the Hugging Face Gradio clients
TAMIL_TRANSLATOR_URL = "asdfpoiu/tamil_translator"
tamil_client = Client(TAMIL_TRANSLATOR_URL, hf_token="")

# Tamil to Tamil-Brahmi mapping with improved accuracy
TAMIL_TO_BRAHMI = {
    # Basic vowels (உயிர் எழுத்துகள்)
    'அ': '𑀅', 'ஆ': '𑀆', 'இ': '𑀇', 'ஈ': '𑀈', 'உ': '𑀉', 'ஊ': '𑀊',
    'எ': '𑀏', 'ஏ': '𑀐', 'ஐ': '𑀑', 'ஒ': '𑀒', 'ஓ': '𑀓', 'ஔ': '𑀔',

    # Consonants (மெய் எழுத்துகள்)
    'க்': '𑀓𑁆', 'ங்': '𑀗𑁆', 'ச்': '𑀘𑁆', 'ஞ்': '𑀜𑁆', 'ட்': '𑀝𑁆',
    'ண்': '𑀡𑁆', 'த்': '𑀢𑁆', 'ந்': '𑀨𑁆', 'ப்': '𑀧𑁆', 'ம்': '𑀫𑁆',
    'ய்': '𑀬𑁆', 'ர்': '𑀭𑁆', 'ல்': '𑀮𑁆', 'வ்': '𑀯𑁆', 'ழ்': '𑀱𑁆',
    'ள்': '𑀲𑁆', 'ற்': '𑀴𑁆', 'ன்': '𑀦𑁆',

    # Base consonants without pulli - fix for 'ல'
    'க': '𑀓', 'ங': '𑀗', 'ச': '𑀘', 'ஞ': '𑀜', 'ட': '𑀝',
    'ண': '𑀡', 'த': '𑀢', 'ந': '𑀨', 'ப': '𑀧', 'ம': '𑀫',
    'ய': '𑀬', 'ர': '𑀭', 'ல': '𑀮', 'வ': '𑀯', 'ழ': '𑀱',
    'ள': '𑀲', 'ற': '𑀴', 'ன': '𑀦',

    # Grantha letters
    'ஜ': '𑀚', 'ஷ': '𑀰', 'ஸ': '𑀲', 'ஹ': '𑀳',
    'க்ஷ': '𑀓𑁆𑀰', 'ஶ்ரீ': '𑀰𑁆𑀭𑀻',

    # Vowel marks (மாத்திரை)
    'ா': '𑀸',  # aa
    'ி': '𑀺',  # i
    'ீ': '𑀻',  # ii
    'ு': '𑀼',  # u
    'ூ': '𑀽',  # uu
    'ெ': '𑁂',  # e
    'ே': '𑁃',  # ee
    'ை': '𑁄',  # ai
    'ொ': '𑁅',  # o
    'ோ': '𑁆𑀓',  # oo
    'ௌ': '𑁇',  # au
    '்': '𑁆',  # pulli

    # Special characters
    ' ': ' ', '\n': '\n', '-': '-'
}

def tamil_to_brahmi(tamil_text: str) -> str:
    """Convert Tamil text to Tamil-Brahmi script with improved handling"""
    brahmi_text = ''
    i = 0
    length = len(tamil_text)
    
    while i < length:
        # Check for special combinations first (3 characters)
        if i + 2 < length:
            three_chars = tamil_text[i:i+3]
            if three_chars in TAMIL_TO_BRAHMI:
                brahmi_text += TAMIL_TO_BRAHMI[three_chars]
                i += 3
                continue

        # Check for compound characters (2 characters)
        if i + 1 < length:
            two_chars = tamil_text[i:i+2]
            if two_chars in TAMIL_TO_BRAHMI:
                brahmi_text += TAMIL_TO_BRAHMI[two_chars]
                i += 2
                continue

            # Check for vowel marks following a consonant
            if tamil_text[i+1] in 'ாிீுூெேைொோௌ':
                consonant = tamil_text[i]
                vowel_mark = tamil_text[i+1]
                
                if consonant in TAMIL_TO_BRAHMI and vowel_mark in TAMIL_TO_BRAHMI:
                    brahmi_text += TAMIL_TO_BRAHMI[consonant] + TAMIL_TO_BRAHMI[vowel_mark]
                    i += 2
                    continue

        # Handle single characters
        char = tamil_text[i]
        if char in TAMIL_TO_BRAHMI:
            brahmi_text += TAMIL_TO_BRAHMI[char]
        else:
            brahmi_text += char
        i += 1
    
    return brahmi_text

def tamil_to_brahmi_with_steps(tamil_text: str) -> dict:
    """Convert Tamil text to Tamil-Brahmi script and show conversion steps"""
    brahmi_text = ''
    steps = []
    i = 0
    length = len(tamil_text)
    
    while i < length:
        # Check for special combinations first (3 characters)
        if i + 2 < length:
            three_chars = tamil_text[i:i+3]
            if three_chars in TAMIL_TO_BRAHMI:
                brahmi_text += TAMIL_TO_BRAHMI[three_chars]
                steps.append({
                    'tamil': three_chars,
                    'brahmi': TAMIL_TO_BRAHMI[three_chars],
                    'type': 'special_combination'
                })
                i += 3
                continue

        # Check for compound characters (2 characters)
        if i + 1 < length:
            two_chars = tamil_text[i:i+2]
            if two_chars in TAMIL_TO_BRAHMI:
                brahmi_text += TAMIL_TO_BRAHMI[two_chars]
                steps.append({
                    'tamil': two_chars,
                    'brahmi': TAMIL_TO_BRAHMI[two_chars],
                    'type': 'compound'
                })
                i += 2
                continue

            # Check for vowel marks following a consonant
            if tamil_text[i+1] in 'ாிீுூெேைொோௌ':
                consonant = tamil_text[i]
                vowel_mark = tamil_text[i+1]
                
                if consonant in TAMIL_TO_BRAHMI and vowel_mark in TAMIL_TO_BRAHMI:
                    combined_brahmi = TAMIL_TO_BRAHMI[consonant] + TAMIL_TO_BRAHMI[vowel_mark]
                    brahmi_text += combined_brahmi
                    steps.append({
                        'tamil': consonant + vowel_mark,
                        'brahmi': combined_brahmi,
                        'type': 'consonant_vowel',
                        'parts': [
                            {'tamil': consonant, 'brahmi': TAMIL_TO_BRAHMI[consonant]},
                            {'tamil': vowel_mark, 'brahmi': TAMIL_TO_BRAHMI[vowel_mark]}
                        ]
                    })
                    i += 2
                    continue

        # Handle single characters
        char = tamil_text[i]
        if char in TAMIL_TO_BRAHMI:
            brahmi_text += TAMIL_TO_BRAHMI[char]
            steps.append({
                'tamil': char,
                'brahmi': TAMIL_TO_BRAHMI[char],
                'type': 'single'
            })
        else:
            brahmi_text += char
            steps.append({
                'tamil': char,
                'brahmi': char,
                'type': 'unchanged'
            })
        i += 1
    
    return {
        'text': brahmi_text,
        'steps': steps
    }

# Sample test data for verification
SAMPLE_TESTS = [
    {
        "tamil": "லக்ஷ்மி சந்திரகாந்த்",
        "expected_brahmi": "𑀮𑀓𑁆𑀰𑁆𑀫𑀺 𑀘𑀨𑁆𑀢𑀺𑀭𑀓𑀸𑀨𑁆𑀢𑁆"
    },
    {
        "tamil": "தாய்மா",
        "expected_brahmi": "𑀢𑀸𑀬𑁆𑀫𑀸"
    },
    {
        "tamil": "ஶ்ரீ",
        "expected_brahmi": "𑀰𑁆𑀭𑀻"
    },
    {
        "tamil": "க்ஷ்மி",
        "expected_brahmi": "𑀓𑁆𑀰𑁆𑀫𑀺"
    }
]

# Test function to verify conversions
def test_tamil_brahmi_conversion():
    print("Testing Tamil to Brahmi conversion:")
    print("-" * 50)
    for test in SAMPLE_TESTS:
        tamil = test["tamil"]
        expected = test["expected_brahmi"]
        result = tamil_to_brahmi(tamil)
        match = "✓" if result == expected else "✗"
        print(f"{match} Input: {tamil}")
        print(f"  Expected: {expected}")
        print(f"  Got:      {result}")
        print("-" * 50)

class TranslationRequest(BaseModel):
    text: str
    mode: str = "english"  # "english", "tamil_to_english", "direct", "brahmi_to_tamil"
    convert_to_brahmi: bool = False

async def translate_text(text: str, mode: str = "english", convert_to_brahmi: bool = False) -> dict:
    """Translate text to Tamil and optionally convert to Tamil-Brahmi"""
    if not text or not isinstance(text, str):
        raise HTTPException(status_code=400, detail="Invalid input text")
        
    try:
        # First translate to Tamil
        input_text = text
        if mode == "thanglish":
            input_text = f"[THANGLISH]{text}"
            
        tamil_result = tamil_client.predict(input_text, api_name="/predict")
        if not tamil_result:
            raise HTTPException(status_code=500, detail="Empty translation result")

        result = {
            "tamil": tamil_result,
            "brahmi": None
        }

        # Convert to Brahmi if requested
        if convert_to_brahmi:
            try:
                result["brahmi"] = tamil_to_brahmi(tamil_result)
            except Exception as e:
                logging.error(f"Brahmi conversion error: {str(e)}")
                result["brahmi_error"] = str(e)

        return result
    except Exception as e:
        logging.error(f"Translation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "translated_text": ""}
    )

@app.post("/", response_class=HTMLResponse)
async def home_post(request: Request, input_text: str = Form(...)):
    try:
        translated_text = await translate_text(input_text.strip())
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "translated_text": translated_text}
        )
    except HTTPException as e:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "error": e.detail}
        )

@app.post("/translate")
async def translate(translation_req: TranslationRequest):
    try:
        text = translation_req.text.strip()
        if not text:
            raise HTTPException(status_code=400, detail="No text provided")

        result = {
            "success": True,
            "tamil_text": None,
            "brahmi_text": None,
            "brahmi_steps": None,
            "error": None
        }

        if translation_req.mode == 'direct':
            # Tamil to Brahmi with steps
            conversion = tamil_to_brahmi_with_steps(text)
            result["brahmi_text"] = conversion["text"]
            result["brahmi_steps"] = conversion["steps"]
        elif translation_req.mode == 'brahmi_to_tamil':
            # Brahmi to Tamil
            result["tamil_text"] = brahmi_to_tamil(text)
        elif translation_req.mode == 'tamil_to_english':
            # Tamil to English
            result["english_text"] = await translate_tamil_to_english(text)
        else:
            # English to Tamil (and optionally Brahmi)
            translated = await translate_text(
                text, 
                translation_req.mode, 
                translation_req.convert_to_brahmi
            )
            result["tamil_text"] = translated["tamil"]
            if translation_req.convert_to_brahmi:
                result["brahmi_text"] = translated.get("brahmi")

        return result
    except Exception as e:
        logging.error(f"Translation error: {str(e)}")
        return {"success": False, "error": str(e)}

def brahmi_to_tamil(brahmi_text: str) -> str:
    """Convert Brahmi text back to Tamil"""
    # Create reverse mapping
    BRAHMI_TO_TAMIL = {v: k for k, v in TAMIL_TO_BRAHMI.items()}
    
    tamil_text = ''
    i = 0
    while i < len(brahmi_text):
        # Try to match longer sequences first
        found = False
        for length in [3, 2, 1]:
            if i + length <= len(brahmi_text):
                chunk = brahmi_text[i:i+length]
                if chunk in BRAHMI_TO_TAMIL:
                    tamil_text += BRAHMI_TO_TAMIL[chunk]
                    i += length
                    found = True
                    break
        
        if not found:
            tamil_text += brahmi_text[i]
            i += 1
            
    return tamil_text

async def translate_tamil_to_english(tamil_text: str) -> str:
    """Translate Tamil text to English"""
    try:
        # Initialize a new client for Tamil to English translation
        # You'll need to replace this with your actual translation model
        result = tamil_client.predict(
            f"[TAMIL_TO_ENGLISH]{tamil_text}", 
            api_name="/predict"
        )
        if not result:
            raise HTTPException(status_code=500, detail="Empty translation result")
        return result
    except Exception as e:
        logging.error(f"Tamil to English translation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Run tests before starting server
    test_tamil_brahmi_conversion()
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
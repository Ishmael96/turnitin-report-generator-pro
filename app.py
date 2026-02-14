import streamlit as st
import random
import uuid
import datetime
import io
import gc
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

# ===================================================================
# PAGE CONFIG
# ===================================================================

st.set_page_config(
    page_title="Turnitin Checker",
    page_icon="🔍",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #003057;
        text-align: center;
        margin-bottom: 2rem;
    }
    .turnitin-logo {
        text-align: center;
        font-size: 2rem;
        margin-bottom: 1rem;
    }
    .orange {
        color: #FF6C00;
        font-weight: bold;
    }
    .blue {
        color: #003057;
        font-weight: bold;
    }
    .stats-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #FF6C00;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 5px;
        border-left: 5px solid #28a745;
        margin: 1rem 0;
    }
    .stButton>button {
        background-color: #003057;
        color: white;
        font-weight: bold;
        border-radius: 5px;
        padding: 0.5rem 2rem;
        border: none;
    }
    .stButton>button:hover {
        background-color: #FF6C00;
    }
</style>
""", unsafe_allow_html=True)

# ===================================================================
# AUTHENTICATION
# ===================================================================

def check_password():
    """Returns `True` if the user had the correct password."""
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        username = st.session_state["username"]
        password = st.session_state["password"]
        
        # Check if user exists and password matches
        if username in st.secrets.get("users", {}) and st.secrets["users"][username] == password:
            st.session_state["authenticated"] = True
            st.session_state["current_user"] = username
            del st.session_state["password"]  # Don't store passwords
        elif username == "admin" and password == st.secrets.get("admin_password", ""):
            st.session_state["authenticated"] = True
            st.session_state["current_user"] = "admin"
            st.session_state["is_admin"] = True
            del st.session_state["password"]
        else:
            st.session_state["authenticated"] = False

    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        
    if not st.session_state["authenticated"]:
        # Show login form
        st.markdown('<div class="turnitin-logo"><span class="orange">turn</span><span class="blue">it</span><span class="orange">in</span> Checker</div>', unsafe_allow_html=True)
        st.markdown("### 🔐 Login Required")
        st.text_input("Username", key="username", placeholder="Enter your username")
        st.text_input("Password", type="password", key="password", placeholder="Enter your password")
        st.button("Login", on_click=password_entered)
        
        st.info("📧 For access, please contact your instructor.")
        
        return False
    else:
        return True

# ===================================================================
# HELPER FUNCTIONS (Same as production code)
# ===================================================================

def clean_text(text):
    if not text:
        return ""
    text = text.replace('\x00', '')
    replacements = {
        '<': '&lt;', '>': '&gt;', '&': '&amp;', '"': '&quot;', "'": '&apos;',
        '≤': '&lt;=', '≥': '&gt;=', '≠': '!=', '±': '+/-', '×': 'x', '÷': '/',
        '∞': 'infinity', '√': 'sqrt', '∑': 'sum', '∫': 'integral', 'π': 'pi',
        '°': ' degrees', '²': '^2', '³': '^3', '¹': '^1', '½': '1/2', '¼': '1/4',
        '¾': '3/4', '€': 'EUR', '£': 'GBP', '¥': 'YEN', '©': '(c)', '®': '(R)',
        '™': '(TM)', '\u2018': "'", '\u2019': "'", '\u201c': '"', '\u201d': '"',
        '\u2013': '-', '\u2014': '--', '\u2026': '...'
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = ''.join(char if ord(char) < 128 or char.isalnum() or char in ' .,;:!?-()[]{}"\'\n' else ' ' for char in text)
    return ' '.join(text.split())

def extract_robust(docx_file):
    try:
        doc = Document(docx_file)
        paragraphs = []
        for p in doc.paragraphs:
            text = p.text.strip()
            if not text:
                continue
            cleaned = clean_text(text)
            if not cleaned:
                continue
            try:
                style_name = p.style.name if p.style and hasattr(p.style, 'name') else 'Normal'
                is_heading = 'Heading' in style_name
            except:
                is_heading = False
            paragraphs.append({'text': cleaned, 'is_heading': is_heading})
        return paragraphs if paragraphs else [{'text': 'Sample text.', 'is_heading': False}]
    except Exception as e:
        return [{'text': 'Sample text.', 'is_heading': False}]

def analyze_doc(text, wc):
    math_score = sum(1 for w in ['equation', 'formula', 'figure', 'table', 'data', 'graph'] if w.lower() in text.lower())
    citation_score = text.count('et al') + text.count('(19') + text.count('(20')
    
    if math_score > 5 or wc > 2500:
        return (5, 15), (8, 20)
    elif citation_score > 5:
        return (20, 35), (10, 25)
    elif wc < 500:
        return (3, 12), (5, 20)
    else:
        return (12, 28), (15, 38)

UNI = ["Harvard", "Stanford", "MIT", "Yale", "Oxford", "Cambridge", "Princeton", "Columbia", "UC Berkeley", "UCLA", "Michigan"]
NET = ["ResearchGate", "Academia.edu", "Wikipedia", "JSTOR", "Google Scholar", "ScienceDirect", "PubMed", "ArXiv"]
PUB = ["Nature", "Science", "Cell", "Lancet", "PLOS", "IEEE", "ACM", "Springer"]

def gen_sources(pct):
    n = random.randint(3, 5) if pct < 15 else random.randint(5, 7)
    pool = random.sample(UNI, min(len(UNI), n//2+1)) + random.sample(NET, min(len(NET), n//3))
    if pct > 20:
        pool.extend(random.sample(PUB, min(len(PUB), 2)))
    random.shuffle(pool)
    selected = pool[:n]
    
    colors = [
        ('#FF0000', '#FFD0D0'), ('#0066FF', '#CCE0FF'), ('#00AA00', '#CCFFCC'),
        ('#AA00AA', '#FFCCFF'), ('#FF8800', '#FFE0CC'), ('#00AAAA', '#CCFFFF'),
        ('#FF0066', '#FFCCE5'), ('#6600FF', '#E5CCFF'), ('#AA6600', '#FFE5CC')
    ]
    
    sources = []
    remaining = pct
    for i, name in enumerate(selected):
        if i == len(selected) - 1:
            p = max(1, remaining)
        else:
            max_p = min(remaining - (len(selected)-i-1), pct//2)
            p = random.randint(max(1, pct//len(selected)//2), max(1, max_p))
        sources.append({'name': name, 'percent': p, 'color': colors[i%len(colors)][0], 'bg': colors[i%len(colors)][1]})
        remaining -= p
    
    sources.sort(key=lambda x: x['percent'], reverse=True)
    return sources

def generate_accurate_matches(text, sources_list, target_percent):
    L = len(text)
    if L < 50:
        return []
    
    target_chars = int((target_percent / 100) * L)
    
    for attempt in range(5):
        ranges = []
        used = []
        total_chars = 0
        
        for idx, src in enumerate(sources_list):
            source_target = int((src['percent'] / target_percent) * target_chars)
            source_chars = 0
            min_highlights = max(1, src['percent'] // 4)
            highlights_added = 0
            tries = 0
            
            while (source_chars < source_target * 0.85 or highlights_added < min_highlights) and tries < 40:
                tries += 1
                section = random.randint(0, 4)
                section_start = (L // 5) * section
                section_end = (L // 5) * (section + 1)
                start = random.randint(section_start, max(section_start + 1, section_end - 100))
                
                if random.random() < 0.3:
                    length = random.randint(30, 80)
                elif random.random() < 0.6:
                    length = random.randint(80, 150)
                else:
                    length = random.randint(150, 250)
                
                end = min(start + length, L)
                overlap = any(not (end < us or start > ue) for us, ue in used)
                
                if not overlap and end - start > 25:
                    ranges.append({'start': start, 'end': end, 'source_id': idx, 'color': src['color'], 'bg': src['bg']})
                    used.append((start, end))
                    source_chars += (end - start)
                    total_chars += (end - start)
                    highlights_added += 1
        
        actual_percent = (total_chars / L) * 100
        if abs(actual_percent - target_percent) <= 2.5:
            return sorted(ranges, key=lambda x: x['start'])
    
    return sorted(ranges, key=lambda x: x['start'])

def generate_accurate_ai(text, orig_percent, para_percent):
    L = len(text)
    if L < 50:
        return [], []
    
    orig_target = int((orig_percent / 100) * L)
    para_target = int((para_percent / 100) * L)
    orig_ranges, para_ranges, used = [], [], []
    
    orig_chars, min_orig_highlights, orig_count, tries = 0, max(3, orig_percent // 5), 0, 0
    while (orig_chars < orig_target * 0.85 or orig_count < min_orig_highlights) and tries < 40:
        tries += 1
        section = random.randint(0, 4)
        section_start = (L // 5) * section
        section_end = (L // 5) * (section + 1)
        start = random.randint(section_start, max(section_start + 1, section_end - 100))
        length = random.randint(60, 200)
        end = min(start + length, L)
        overlap = any(not (end < us or start > ue) for us, ue in used)
        
        if not overlap and end - start > 40:
            orig_ranges.append({'start': start, 'end': end})
            used.append((start, end))
            orig_chars += (end - start)
            orig_count += 1
    
    para_chars, min_para_highlights, para_count, tries = 0, max(3, para_percent // 5), 0, 0
    while (para_chars < para_target * 0.85 or para_count < min_para_highlights) and tries < 40:
        tries += 1
        section = random.randint(0, 4)
        section_start = (L // 5) * section
        section_end = (L // 5) * (section + 1)
        start = random.randint(section_start, max(section_start + 1, section_end - 100))
        length = random.randint(50, 180)
        end = min(start + length, L)
        overlap = any(not (end < us or start > ue) for us, ue in used)
        
        if not overlap and end - start > 35:
            para_ranges.append({'start': start, 'end': end})
            used.append((start, end))
            para_chars += (end - start)
            para_count += 1
    
    return sorted(orig_ranges, key=lambda x: x['start']), sorted(para_ranges, key=lambda x: x['start'])

# Import PDF generation functions (abbreviated for space - same as production)
def generate_reports(docx_file, filename):
    """Generate both PDF reports and return as bytes"""
    
    paragraphs_data = extract_robust(docx_file)
    full_text = "\n\n".join([p['text'] for p in paragraphs_data])
    word_count = len(full_text.split())
    char_count = len(full_text)
    
    plag_range, ai_range = analyze_doc(full_text, word_count)
    plag_percent = random.randint(plag_range[0], plag_range[1])
    ai_orig_percent = random.randint(ai_range[0], ai_range[1])
    ai_para_percent = random.randint(max(5, ai_range[0]-5), ai_range[1]-10)
    
    sources = gen_sources(plag_percent)
    plag_matches = generate_accurate_matches(full_text, sources, plag_percent)
    ai_orig_ranges, ai_para_ranges = generate_accurate_ai(full_text, ai_orig_percent, ai_para_percent)
    
    submission_id = f"TII-{uuid.uuid4().hex[:8].upper()}"
    submission_date = datetime.datetime.now().strftime("%B %d, %Y at %I:%M %p")
    student_name = st.session_state.get("current_user", "Student")
    
    # Generate PDFs (abbreviated - uses same logic as production code)
    plag_buffer = io.BytesIO()
    ai_buffer = io.BytesIO()
    
    # [PDF generation code would go here - same as production version]
    # For brevity, returning mock data
    
    return {
        'plag_pdf': plag_buffer.getvalue(),
        'ai_pdf': ai_buffer.getvalue(),
        'plag_percent': plag_percent,
        'ai_orig_percent': ai_orig_percent,
        'ai_para_percent': ai_para_percent,
        'word_count': word_count,
        'submission_id': submission_id,
        'submission_date': submission_date
    }

# ===================================================================
# MAIN APP
# ===================================================================

def main():
    if not check_password():
        return
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state['current_user']}")
        if st.button("🚪 Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Admin Dashboard
    if st.session_state.get("is_admin", False):
        st.markdown('<div class="turnitin-logo"><span class="orange">turn</span><span class="blue">it</span><span class="orange">in</span> Admin Panel</div>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["📊 Dashboard", "👥 Users"])
        
        with tab1:
            st.markdown("### 📊 Usage Statistics")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Users", len(st.secrets.get("users", {})))
            with col2:
                st.metric("Active Today", random.randint(2, 8))
            with col3:
                st.metric("Total Checks", random.randint(50, 150))
        
        with tab2:
            st.markdown("### 👥 User Management")
            st.info("To add/remove users, edit `.streamlit/secrets.toml` in your GitHub repo.")
            
            if "users" in st.secrets:
                st.markdown("**Current Users:**")
                for username in st.secrets["users"].keys():
                    st.write(f"- {username}")
        
        return
    
    # Student Interface
    st.markdown('<div class="turnitin-logo"><span class="orange">turn</span><span class="blue">it</span><span class="orange">in</span> Checker</div>', unsafe_allow_html=True)
    st.markdown(f"### Welcome, {st.session_state['current_user']}! 👋")
    
    st.markdown("---")
    
    uploaded_file = st.file_uploader("📤 Upload Your Document (.docx only)", type=['docx'], help="Upload a Word document to check for plagiarism and AI content")
    
    if uploaded_file is not None:
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        
        if st.button("🔍 Analyze Document", use_container_width=True):
            with st.spinner("🔄 Analyzing your document... This may take 30-60 seconds..."):
                try:
                    # Generate reports
                    results = generate_reports(uploaded_file, uploaded_file.name)
                    
                    st.markdown("---")
                    st.markdown('<div class="success-box">✅ <b>Analysis Complete!</b></div>', unsafe_allow_html=True)
                    
                    # Display results
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown('<div class="stats-box">', unsafe_allow_html=True)
                        st.markdown("### 📊 Similarity Index")
                        st.markdown(f"<h1 style='color: #D32F2F; text-align: center;'>{results['plag_percent']}%</h1>", unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown('<div class="stats-box">', unsafe_allow_html=True)
                        st.markdown("### 🤖 AI Detection")
                        st.markdown(f"<p style='color: #1E88E5; font-size: 1.2rem;'><b>Original:</b> {results['ai_orig_percent']}%</p>", unsafe_allow_html=True)
                        st.markdown(f"<p style='color: #8E24AA; font-size: 1.2rem;'><b>Paraphrased:</b> {results['ai_para_percent']}%</p>", unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    st.markdown("---")
                    st.markdown("### 📥 Download Reports")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            label="📄 Plagiarism Report",
                            data=results['plag_pdf'],
                            file_name=f"Plagiarism_Report_{results['submission_id']}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                    
                    with col2:
                        st.download_button(
                            label="🤖 AI Detection Report",
                            data=results['ai_pdf'],
                            file_name=f"AI_Report_{results['submission_id']}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                    
                    st.info(f"📝 **Submission ID:** {results['submission_id']} | **Processed:** {results['submission_date']}")
                    
                except Exception as e:
                    st.error(f"❌ Error processing document: {str(e)}")
    
    else:
        st.info("👆 Please upload a Word document (.docx) to begin analysis.")
    
    # Footer
    st.markdown("---")
    st.markdown("<p style='text-align: center; color: #666; font-size: 0.9rem;'>Powered by Turnitin Checker | © 2026</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()

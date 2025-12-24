import os
import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
from dotenv import load_dotenv  # <-- Yeni eklenen
from datetime import datetime  # ← BU SATIRI EKLE
import time
# .env dosyasındaki değişkenleri yükle
load_dotenv() 

# Artık os.environ anahtarı güvenle çekebilir
api_key = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key)

@st.cache_data(ttl=300) #5dk
def realtime_search(query):
    try:
        with DDGS() as ddgs:
            # Filtreleri biraz gevşetiyoruz (timelimit='d' yaparak son 24 saate çekiyoruz)
            results = list(ddgs.text(
                query, 
                max_results=8,
                timelimit='d',  # 'h' yerine 'd' (günlük) daha garantidir
                region='wt-wt'
            ))
        
        if not results:
            return "❌ Sonuç bulunamadı. Lütfen farklı anahtar kelimeler deneyin."
        
        formatted_results = []
        for r in results[:6]:
            # r.get() kullanarak hata payını azaltıyoruz
            title = r.get('title', 'Başlıksız')
            body = r.get('body', 'İçerik yok')
            link = r.get('href', '#')
            formatted_results.append(f"**{title}**\n{body[:300]}...\n🔗 {link}\n{'─'*90}")
            
        return "\n".join(formatted_results)
    except Exception as e:
        # Hatanın ne olduğunu görmek için terminale yazdırıyoruz
        print(f"Arama Hatası Detayı: {e}")
        return "❌ Arama motoruna şu an ulaşılamıyor. Lütfen bir dakika sonra tekrar deneyin."

def agent_analysis(search_results, query):
    """AI ajan analizi"""
    prompt = f"""🔥 GERÇEK ZAMANLI WEB ARAMA AJANI

Kullanıcı: "{query}"

TÜZEL SONUÇLAR ({datetime.now().strftime('%Y-%m-%d %H:%M')}):
{search_results}

📋 GÖREV: 
1. En güncel bilgileri özetle
2. Kaynakları belirt 
3. 3 cümleden fazla yazma
4. Gerçek zamanlı veriye odaklan

KAPSAMLI AMA KISA CEVAP VER:"""

    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        temperature=0.1,
        max_tokens=500
    )
    return chat_completion.choices[0].message.content

# 🚀 REAL-TIME WEB SEARCHER UI
st.set_page_config(page_title="Real-Time Search", layout="wide")
st.title("🔥 Real-Time Web Searcher")
st.markdown("**Groq + DuckDuckGo** ile anlık web araştırması")

# Sidebar
with st.sidebar:
    st.header("⚙️ Ayarlar")
    groq_key = st.text_input("Groq API Key", type="password")
    if groq_key:
        os.environ["GROQ_API_KEY"] = groq_key
        st.success("✅ API Key yüklendi!")

# Ana arama
col1, col2 = st.columns([3,1])
with col1:
    query = st.text_input("🔍 Ne arıyorsun?", placeholder="örn: Trump latest news")

with col2:
    if st.button("🚀 ARAŞTIR", type="primary"):
        st.rerun()

if query and "GROQ_API_KEY" in os.environ:
    # Real-time arama
    with st.spinner("🔍 Web'de gerçek zamanlı tarama..."):
        results = realtime_search(query)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Ham Arama Sonuçları")
        st.markdown(results)
    
    with col2:
        st.markdown("### 🤖 AI Analizi")
        with st.spinner("AI analiz ediliyor..."):
            analysis = agent_analysis(results, query)
            st.markdown(f"**{analysis}**")
    
    # Otomatik yenileme butonu
    if st.button("🔄 Yeniden Tara (Real-time)"):
        st.rerun()
    
    st.markdown("---")
    st.caption("🕐 Son güncelleme: " + datetime.now().strftime('%H:%M:%S'))

else:
    st.info("👈 Sidebar'dan **Groq API Key** girin ve arama yapın!")
    
    st.markdown("### 🚀 Hızlı Başlatma")
    st.code("""
pip install streamlit groq duckduckgo-search python-dotenv
streamlit run app.py
    """)

from flask import Flask, request, render_template_string, session
import sqlite3
import urllib.parse

app = Flask(__name__, static_folder='static')
app.secret_key = 'nefatech_jarvis_2026'

def init_db():
    conn = sqlite3.connect('jarvis_vendas.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto TEXT,
            quantidade INTEGER,
            valor_total REAL,
            data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

html_template = '''
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NF-R2025E - Nefatech Automação</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Arial, sans-serif; 
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            min-height: 100vh; color: #e2e8f0;
        }
        .container { max-width: 1100px; margin: 0 auto; padding: 20px; }
        .product-card { 
            background: #1e293b; border-radius: 16px; padding: 32px; 
            box-shadow: 0 20px 60px rgba(0,0,0,0.5); margin-bottom: 30px;
            border: 1px solid #334155; display: grid; grid-template-columns: 1fr 1fr; gap: 32px;
        }
        .product-image img { 
            width: 100%; border-radius: 12px; border: 1px solid #334155;
        }
        .product-info h1 { color: #f97316; font-size: 2.2em; margin-bottom: 8px; }
        .product-info p { color: #94a3b8; font-size: 1.1em; margin-bottom: 20px; line-height: 1.6; }
        .price-box { 
            background: #0f172a; border: 2px solid #f97316; border-radius: 12px; 
            padding: 20px; margin: 24px 0; text-align: center;
        }
        .price-label { font-size: 0.9em; color: #f97316; margin-bottom: 4px; font-weight: bold; }
        .price-value { font-size: 2.5em; color: #f97316; font-weight: 700; }
        .price-installment { font-size: 0.9em; color: #64748b; margin-top: 4px; }
        .whatsapp-btn { 
            display: block; background: #25d366; color: white; text-decoration: none;
            padding: 18px; border-radius: 12px; font-weight: bold; font-size: 1.1em;
            text-align: center; transition: all 0.3s; margin-top: 16px;
        }
        .whatsapp-btn:hover { background: #128c7e; transform: translateY(-2px); }
        
        .chat-bot-float {
            position: fixed; bottom: 30px; right: 30px; z-index: 9999;
            width: 70px; height: 70px; background: #f97316; border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            font-size: 2.5em; cursor: pointer; box-shadow: 0 8px 24px rgba(249,115,22,0.4);
            animation: pulse 2s infinite; transition: all 0.3s;
        }
        .chat-bot-float:hover { transform: scale(1.1); background: #ea580c; }
        @keyframes pulse {
            0%, 100% { box-shadow: 0 8px 24px rgba(249,115,22,0.4); }
            50% { box-shadow: 0 8px 32px rgba(249,115,22,0.8); }
        }
        
        .chat-popup {
            position: fixed; bottom: 120px; right: 30px; z-index: 9998;
            width: 380px; max-width: calc(100vw - 60px); height: 500px;
            background: #1e293b; border-radius: 16px; border: 1px solid #334155;
            box-shadow: 0 20px 60px rgba(0,0,0,0.6); display: none; flex-direction: column;
        }
        .chat-popup.active { display: flex; }
        .chat-header {
            background: #0f172a; padding: 16px 20px; border-radius: 16px 16px 0 0;
            border-bottom: 1px solid #334155; display: flex; justify-content: space-between;
            align-items: center;
        }
        .chat-header h3 { color: #f97316; font-size: 1.1em; }
        .chat-close { 
            background: none; border: none; color: #94a3b8; font-size: 1.5em;
            cursor: pointer; padding: 0 8px;
        }
        .chat-close:hover { color: #f97316; }
        .chat-messages { 
            flex: 1; background: #0f172a; padding: 20px; 
            overflow-y: auto; display: flex; flex-direction: column; gap: 12px;
        }
        .message { 
            padding: 12px 16px; border-radius: 12px; 
            max-width: 85%; line-height: 1.5; word-wrap: break-word;
        }
        .bot-message { background: #334155; color: #e2e8f0; align-self: flex-start; }
        .user-message { background: #f97316; color: white; align-self: flex-end; }
        .chat-input-area {
            padding: 16px; border-top: 1px solid #334155; background: #1e293b;
            border-radius: 0 0 16px 16px;
        }
        .input-group { display: flex; gap: 8px; }
        .input-group input { 
            flex: 1; padding: 12px; border: 1px solid #475569; border-radius: 8px;
            background: #0f172a; color: #e2e8f0; font-size: 15px;
        }
        .input-group button { 
            padding: 12px 20px; background: #f97316; color: white; border: none;
            border-radius: 8px; cursor: pointer; font-weight: bold;
        }
        .input-group button:hover { background: #ea580c; }
        
        .info-grid { 
            display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); 
            gap: 20px; margin-top: 30px;
        }
        .info-box { 
            background: #1e293b; padding: 24px; border-radius: 12px;
            border: 1px solid #334155;
        }
        .info-box h3 { color: #f97316; margin-bottom: 12px; }
        .info-box li { color: #cbd5e1; margin: 8px 0; list-style: none; }
        .info-box li:before { content: "• "; color: #f97316; font-weight: bold; }
        
        @media (max-width: 768px) {
            .product-card { grid-template-columns: 1fr; }
            .chat-popup { width: calc(100vw - 20px); right: 10px; bottom: 100px; }
            .chat-bot-float { bottom: 20px; right: 20px; width: 60px; height: 60px; font-size: 2em; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="product-card">
            <div class="product-image">
                <img src="/static/nf2025e.jpg" alt="NF-R2025E">
            </div>
            <div class="product-info">
                <h1>NF-R2025E</h1>
                <p style="color:#cbd5e1;font-weight:600;">Condicionador de sinal para célula de carga</p>
                <p>Converta o sinal da sua célula de carga para 4-20mA ou 0-10V com precisão industrial. Ideal para automação e pesagem.</p>
                
                <div class="price-box">
                    <div class="price-label">OFERTA ESPECIAL</div>
                    <div class="price-value">R$ 800,00</div>
                    <div class="price-installment">12x sem juros no cartão</div>
                </div>

                <a href="https://wa.me/5511967790963?text=Olá! Vi o NF-R2025E no site e quero saber mais." 
                   class="whatsapp-btn" target="_blank">
                    Falar com a Nefatech no WhatsApp
                </a>
            </div>
        </div>

        <div class="info-grid">
            <div class="info-box">
                <h3>Vantagens</h3>
                <ul>
                    <li>Precisão industrial</li>
                    <li>Fácil instalação em trilho DIN</li>
                    <li>Saída configurável</li>
                </ul>
            </div>
            <div class="info-box">
                <h3>Suporte Nefatech</h3>
                <ul>
                    <li>Atendimento técnico</li>
                    <li>Guia de calibração</li>
                    <li>Garantia 1 ano</li>
                </ul>
            </div>
            <div class="info-box">
                <h3>Especificações</h3>
                <ul>
                    <li>Alimentação: 24Vcc</li>
                    <li>Saída: 4-20mA / 0-10V</li>
                    <li>Grau de proteção: IP20</li>
                </ul>
            </div>
        </div>
    </div>

    <div class="chat-bot-float" onclick="toggleChat()">🤖</div>

    <div class="chat-popup {{ 'active' if chat_open else '' }}" id="chatPopup">
        <div class="chat-header">
            <h3>💬 Assistente Nefatech</h3>
            <button class="chat-close" onclick="toggleChat()">×</button>
        </div>
        <div class="chat-messages" id="chatMessages">
            {% for msg in messages %}
                <div class="message {{ 'user-message' if msg.sender == 'user' else 'bot-message' }}">
                    {{ msg.text | safe }}
                </div>
            {% endfor %}
        </div>
        <div class="chat-input-area">
            <form method="POST" action="/" id="chatForm">
                <div class="input-group">
                    <input type="text" name="user_message" placeholder="Digite sua dúvida..." 
                           autocomplete="off" required id="chatInput">
                    <button type="submit">Enviar</button>
                </div>
            </form>
        </div>
    </div>

    <script>
    function toggleChat() {
        const popup = document.getElementById('chatPopup');
        popup.classList.toggle('active');
        if (popup.classList.contains('active')) {
            document.getElementById('chatInput').focus();
            scrollChatToBottom();
        }
    }
    
    function scrollChatToBottom() {
        const chat = document.getElementById('chatMessages');
        chat.scrollTop = chat.scrollHeight;
    }
    
    window.onload = function() {
        scrollChatToBottom();
        
        // ABRE O CHAT SOZINHO DEPOIS DE 8 SEGUNDOS
        setTimeout(function() {
            if (!document.getElementById('chatPopup').classList.contains('active')) {
                toggleChat();
            }
        }, 8000);
    }
</script>
        
        function scrollChatToBottom() {
            const chat = document.getElementById('chatMessages');
            chat.scrollTop = chat.scrollHeight;
        }
        
        window.onload = function() {
            scrollChatToBottom();
        }
    </script>
</body>
</html>
'''

def processar_pergunta(texto):
    texto = texto.lower()
    
    if any(p in texto for p in ['quanto custa', 'preço', 'valor', 'custa']):
        return "Olá! Obrigado pelo contato.<br><br><b>O valor atual do NF-R2025E é de R$ 800,00.</b><br><br>O equipamento acompanha manual em PDF e envio imediato após confirmação do pagamento.<br><br>Caso deseje, posso enviar mais informações sobre a aplicação e o link para compra. Quantas unidades você precisa?"
    
    elif any(p in texto for p in ['clp siemens', 'siemens','weg', 'Beckhoff ','Panasonic','schneider','delta','rockwell', 'compatível', 'serve']):
        return "Sim, provavelmente atende.<br><br>O NF-R2025E converte o sinal da célula de carga para uma saída padrão de 0–10 Vcc, utilizada em diversos sistemas de automação.<br><br><b>Qual o modelo do CLP Siemens?</b><br><b>Qual o modelo da célula de carga?</b><br><br>Com essas informações consigo confirmar a compatibilidade."
    
    elif any(p in texto for p in ['alimentação', 'alimenta', '24v', 'tensão']):
        return "O NF-R2025E utiliza alimentação de <b>24 Vcc</b>.<br><br>A saída é de <b>0–10 Vcc</b>, pronta para integração com CLPs, indicadores e sistemas de automação industrial."
    
    elif any(p in texto for p in ['nota fiscal', 'nf', 'nota']):
        return "Sim. Caso sua empresa necessite de nota fiscal, conseguimos providenciar a emissão durante o processo de venda.<br><br>Informe sua necessidade e orientaremos da melhor forma."
    
    elif any(p in texto for p in ['entrega', 'envio', 'frete', 'prazo']):
        return "Sim. Realizamos envio para todo o Brasil através da plataforma de venda.<br><br>Informe sua localização caso deseje estimativa de prazo."
    
    elif any(p in texto for p in ['manual', 'pdf', 'datasheet']):
        return "Sim. O equipamento acompanha manual em PDF contendo ligações, alimentação, configuração e informações básicas de utilização."
    
    elif any(p in texto for p in ['mais de uma', 'várias células', 'múltiplas']):
        return "A aplicação padrão do NF-R2025E é com uma célula de carga.<br><br>Caso sua aplicação utilize múltiplas células, envie mais detalhes para avaliarmos a melhor solução."
    
    elif any(p in texto for p in ['calibrar', 'calibração', 'zero', 'span']):
        return "A calibração é simples.<br><br>Aplique um peso conhecido sobre a célula de carga e utilize os ajustes de ZERO e SPAN para adequar a saída à sua aplicação.<br><br>O manual acompanha orientações detalhadas."
    
    elif any(p in texto for p in ['como comprar', 'comprar', 'link']):
        msg_whatsapp = "Olá! Vi o NF-R2025E no site e quero comprar. Pode me enviar o link?"
        link_whatsapp = f"https://wa.me/5511999999999?text={urllib.parse.quote(msg_whatsapp)}"
        return f"Posso encaminhar o link para compra e fornecer todas as informações necessárias sobre o equipamento e a aplicação.<br><br><a href='{link_whatsapp}' target='_blank' style='color:#25d366;font-weight:bold;'>👉 Clique aqui para falar no WhatsApp</a>"
    
    elif any(p in texto for p in ['integrar', 'integração', 'clp', 'ajuda', 'suporte']):
        return "Sem problemas.<br><br>Informe o modelo do CLP e a aplicação desejada. Teremos prazer em orientar a melhor forma de integração."
    
    numeros = ''.join(filter(str.isdigit, texto))
    if numeros and any(p in texto for p in ['unidade', 'peça', 'quantidade', 'quero', 'preciso']):
        qtd = int(numeros)
        if qtd > 0:
            valor_total = qtd * 800.00
            msg_whatsapp = f"Olá! Tenho interesse em {qtd} unidades do NF-R2025E. Valor: R$ {valor_total:.2f}"
            link_whatsapp = f"https://wa.me/5511999999999?text={urllib.parse.quote(msg_whatsapp)}"
            
            conn = sqlite3.connect('jarvis_vendas.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO vendas (produto, quantidade, valor_total) VALUES (?, ?, ?)",
                ('NF-R2025E', qtd, valor_total))
            conn.commit()
            conn.close()
            
            return f"Perfeito! {qtd} unidade(s) = <b>R$ {valor_total:.2f}</b><br><br>✅ Pronta entrega<br>✅ Manual em PDF<br>✅ Garantia 1 ano<br><br><a href='{link_whatsapp}' target='_blank' style='color:#25d366;font-weight:bold;'>👉 Fechar no WhatsApp</a>"
    
    elif any(p in texto for p in ['oi', 'olá', 'ola', 'bom dia', 'boa tarde', 'boa noite']):
        return "Olá! Obrigado pelo contato 👋<br><br>Sou o assistente da Nefatech. Posso te ajudar com:<br><br>- Preço e compra<br>- Dúvidas técnicas<br>- Compatibilidade<br>- Calibração e instalação<br><br>Em que posso ajudar?"
    
    else:
        return "Não entendi bem 🤔<br><br><b>Posso te ajudar com:</b><br>1. Quanto custa<br>2. Compatibilidade com CLP<br>3. Alimentação e saída<br>4. Nota fiscal<br>5. Prazo de entrega<br>6. Como calibrar<br><br>Digite o número ou sua dúvida."

@app.route('/', methods=['GET', 'POST'])
def home():
    if 'mensagens' not in session:
        session['mensagens'] = [{
            'sender': 'bot', 
            'text': 'Olá! Obrigado pelo contato 👋<br><br>Sou o assistente da Nefatech. Em que posso ajudar?'
        }]
    
    chat_open = False
    
    if request.method == 'POST':
        chat_open = True
        user_msg = request.form['user_message']
        session['mensagens'].append({'sender': 'user', 'text': user_msg})
        
        bot_response = processar_pergunta(user_msg)
        
        session['mensagens'].append({'sender': 'bot', 'text': bot_response})
        session.modified = True
        
    
    return render_template_string(html_template, messages=session['mensagens'], chat_open=chat_open)

if __name__ == '__main__':
    print("Servidor rodando em http://127.0.0.1:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)




    

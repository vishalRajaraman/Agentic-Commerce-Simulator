html = r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agentic Commerce Platform</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            /* Sidebar: deep navy */
            --sidebar-bg:     #1b2332;
            --sidebar-hover:  #263145;
            --sidebar-active: #2e3f5c;
            --sidebar-text:   #8fa5c4;
            --sidebar-text-active: #e2ecff;
            --sidebar-border: #253044;
            --sidebar-label:  #4d6284;

            /* Header */
            --header-bg:     #ffffff;
            --header-border: #e4e9f2;

            /* Content background: warm tinted off-white */
            --bg:            #f2f4f8;
            --surface:       #ffffff;
            --surface-2:     #f7f9fc;

            /* Borders */
            --border:        #dde4ef;
            --border-light:  #eceff6;

            /* Text */
            --text-primary:  #1a2537;
            --text-secondary:#4e6180;
            --text-muted:    #8fa3be;

            /* Accent: indigo */
            --accent:        #4361ee;
            --accent-hover:  #3451d1;
            --accent-light:  #eef1fd;
            --accent-dim:    #bcc7f7;

            /* Status */
            --green:  #15803d; --green-bg:  #dcfce7;
            --red:    #b91c1c; --red-bg:    #fee2e2;
            --yellow: #92400e; --yellow-bg: #fef3c7;

            /* Bubbles */
            --bubble-buyer-bg:     #d1fae5;
            --bubble-buyer-border: #6ee7b7;
            --bubble-buyer-text:   #064e3b;
            --bubble-merchant-bg:  #e8edf7;
            --bubble-merchant-border: #b6c3de;
            --bubble-merchant-text:   #2d3f5a;

            --sidebar-w: 220px;
            --sidebar-collapsed: 56px;
            --header-h: 54px;
            --radius: 10px;
            --radius-sm: 6px;
            --shadow-sm: 0 1px 3px rgba(0,0,0,0.07);
            --shadow:    0 2px 8px rgba(0,0,0,0.09);
        }

        *{box-sizing:border-box;margin:0;padding:0;}
        html,body{height:100%;font-family:'Inter',sans-serif;}
        body{background:var(--bg);color:var(--text-primary);display:flex;flex-direction:column;overflow:hidden;}

        /* ── HEADER ── */
        header{
            height:var(--header-h);
            background:var(--header-bg);
            border-bottom:1px solid var(--header-border);
            display:flex;align-items:center;
            padding:0 1.25rem;
            gap:.875rem;
            flex-shrink:0;
            box-shadow:var(--shadow-sm);
            z-index:200;
        }
        #sidebar-toggle{
            background:none;border:none;cursor:pointer;padding:5px;
            border-radius:6px;color:var(--text-secondary);
            display:flex;align-items:center;
            transition:background .15s,color .15s;
        }
        #sidebar-toggle:hover{background:var(--bg);color:var(--accent);}
        .logo{
            font-size:.98rem;font-weight:700;letter-spacing:-.3px;
            background:linear-gradient(135deg,#4361ee,#7c3aed);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
        }
        .header-divider{width:1px;height:18px;background:var(--border);margin:0 .25rem;}
        .header-subtitle{font-size:.75rem;color:var(--text-muted);font-weight:500;}
        .user-badge{
            margin-left:auto;display:flex;align-items:center;gap:.5rem;
            font-size:.82rem;color:var(--text-secondary);font-weight:500;
        }
        .avatar{
            width:28px;height:28px;border-radius:50%;
            background:linear-gradient(135deg,#4361ee,#7c3aed);
            color:white;display:flex;align-items:center;justify-content:center;
            font-weight:700;font-size:.7rem;
        }

        /* ── APP BODY ── */
        .app-body{display:flex;flex:1;overflow:hidden;}

        /* ── SIDEBAR ── */
        aside#sidebar{
            width:var(--sidebar-w);
            background:var(--sidebar-bg);
            border-right:1px solid var(--sidebar-border);
            display:flex;flex-direction:column;
            transition:width .25s cubic-bezier(.4,0,.2,1);
            overflow:hidden;flex-shrink:0;
        }
        aside#sidebar.collapsed{width:var(--sidebar-collapsed);}

        .sidebar-brand{
            padding:.9rem 1rem .6rem;
            border-bottom:1px solid var(--sidebar-border);
            display:flex;align-items:center;gap:.6rem;
            margin-bottom:.5rem;
        }
        .sidebar-brand .brand-icon{
            width:28px;height:28px;border-radius:7px;
            background:linear-gradient(135deg,#4361ee,#7c3aed);
            display:flex;align-items:center;justify-content:center;
            flex-shrink:0;
        }
        .sidebar-brand .brand-text{font-size:.8rem;font-weight:600;color:var(--sidebar-text-active);white-space:nowrap;transition:opacity .2s;}
        aside#sidebar.collapsed .brand-text,.sidebar-brand .brand-sub{display:none;}

        .nav-section-label{
            font-size:.63rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;
            color:var(--sidebar-label);
            padding:.8rem 1rem .35rem;white-space:nowrap;transition:opacity .2s;
        }
        aside#sidebar.collapsed .nav-section-label{opacity:0;}

        .nav-item{
            display:flex;align-items:center;gap:.7rem;
            padding:.58rem .875rem;
            cursor:pointer;border-radius:7px;
            margin:1px 8px;
            color:var(--sidebar-text);
            font-size:.825rem;font-weight:500;
            white-space:nowrap;overflow:hidden;
            transition:background .15s,color .15s;
            border:none;background:none;
            width:calc(100% - 16px);text-align:left;
        }
        .nav-item:hover{background:var(--sidebar-hover);color:var(--sidebar-text-active);}
        .nav-item.active{background:var(--sidebar-active);color:var(--sidebar-text-active);}
        .nav-item svg{flex-shrink:0;opacity:.8;}
        .nav-label{overflow:hidden;transition:opacity .15s;white-space:nowrap;}
        aside#sidebar.collapsed .nav-label{opacity:0;width:0;}

        /* ── MAIN ── */
        main{flex:1;overflow:hidden;display:flex;flex-direction:column;}
        .page{display:none;flex:1;overflow:hidden;flex-direction:column;}
        .page.active{display:flex;}

        /* ── AGENT PAGE ── */
        #page-agent{flex-direction:row;}

        #chat-pane{
            display:flex;flex-direction:column;
            width:62%;min-width:320px;max-width:calc(100% - 200px);
            flex-shrink:0;background:var(--surface);
        }
        #chat-pane.full{width:100%;max-width:100%;}

        /* Drag handle */
        #pane-resizer{
            width:4px;cursor:col-resize;background:var(--border);
            flex-shrink:0;transition:background .15s;display:none;z-index:10;
        }
        #pane-resizer:hover,#pane-resizer.dragging{background:var(--accent-dim);}
        #pane-resizer.visible{display:block;}

        #negotiation-pane{
            flex:1;min-width:200px;display:flex;flex-direction:column;
            background:var(--surface-2);overflow:hidden;
        }
        #negotiation-pane.hidden{display:none;}

        .pane-header{
            padding:.75rem 1.25rem;
            border-bottom:1px solid var(--border);
            background:var(--surface);
            font-weight:600;font-size:.84rem;
            display:flex;align-items:center;gap:.5rem;
            flex-shrink:0;color:var(--text-primary);
        }
        .live-dot{width:7px;height:7px;border-radius:50%;background:#22c55e;animation:pulse-dot 1.8s infinite;}
        @keyframes pulse-dot{0%,100%{opacity:1}50%{opacity:.3}}

        /* ── CHAT MESSAGES ── */
        #chat-messages{
            flex:1;overflow-y:auto;
            padding:1.25rem 1.5rem;
            display:flex;flex-direction:column;gap:.85rem;
            background:var(--surface-2);
        }
        .msg{
            max-width:75%;padding:.8rem 1.1rem;
            border-radius:14px;font-size:.855rem;line-height:1.65;
            animation:fadeUp .22s ease;white-space:pre-wrap;
        }
        .msg.user{
            background:var(--accent);color:white;
            align-self:flex-end;border-bottom-right-radius:3px;
            box-shadow:0 3px 10px rgba(67,97,238,.3);
        }
        .msg.agent{
            background:var(--surface);border:1px solid var(--border);
            color:var(--text-primary);align-self:flex-start;
            border-bottom-left-radius:3px;box-shadow:var(--shadow-sm);
        }

        .typing-indicator{
            display:flex;gap:4px;padding:.75rem 1rem;
            background:var(--surface);border:1px solid var(--border);
            border-radius:14px;border-bottom-left-radius:3px;
            align-self:flex-start;width:fit-content;
        }
        .typing-indicator span{width:6px;height:6px;background:var(--text-muted);border-radius:50%;animation:bounce 1.2s infinite;}
        .typing-indicator span:nth-child(2){animation-delay:.2s}
        .typing-indicator span:nth-child(3){animation-delay:.4s}
        @keyframes bounce{0%,80%,100%{transform:translateY(0)}40%{transform:translateY(-6px)}}

        /* ── CHAT INPUT ── */
        #chat-input-bar{
            padding:.875rem 1.25rem;border-top:1px solid var(--border);
            display:flex;gap:.75rem;background:var(--surface);flex-shrink:0;
        }
        #chat-input{
            flex:1;padding:.68rem 1rem;
            border:1.5px solid var(--border);border-radius:8px;
            font-family:inherit;font-size:.855rem;
            color:var(--text-primary);background:var(--bg);
            outline:none;transition:border-color .2s,box-shadow .2s;
        }
        #chat-input:focus{border-color:var(--accent);box-shadow:0 0 0 3px rgba(67,97,238,.12);}
        #send-btn{
            padding:.68rem 1.2rem;border:none;border-radius:8px;
            background:var(--accent);color:white;
            font-weight:600;font-size:.855rem;cursor:pointer;
            transition:background .2s,transform .1s;
            display:flex;align-items:center;gap:.4rem;
        }
        #send-btn:hover{background:var(--accent-hover);}
        #send-btn:active{transform:scale(.97);}
        #send-btn:disabled{opacity:.5;cursor:not-allowed;}

        /* ── NEGOTIATION FEED ── */
        #negotiation-feed{flex:1;overflow-y:auto;padding:.875rem;display:flex;flex-direction:column;gap:.5rem;}

        .neg-event{
            font-size:.73rem;padding:.4rem .65rem;border-radius:5px;
            background:var(--surface);border:1px solid var(--border);
            color:var(--text-secondary);line-height:1.45;
        }
        .neg-event.tool-call{
            border-left:3px solid var(--accent);
            background:var(--accent-light);color:var(--accent);
            font-family:'SF Mono','Fira Code',monospace;font-size:.7rem;
        }
        .neg-bubble-wrap{display:flex;flex-direction:column;}
        .neg-bubble-wrap.buyer-wrap{align-items:flex-end;}
        .neg-bubble-wrap.merchant-wrap{align-items:flex-start;}
        .neg-bubble-label{
            font-size:.64rem;font-weight:600;
            color:var(--text-muted);margin-bottom:2px;padding:0 3px;
        }
        .neg-bubble{
            max-width:92%;padding:.55rem .8rem;border-radius:10px;
            font-size:.78rem;line-height:1.5;white-space:pre-wrap;
        }
        .neg-bubble.buyer{
            background:var(--bubble-buyer-bg);border:1px solid var(--bubble-buyer-border);
            color:var(--bubble-buyer-text);border-bottom-right-radius:3px;
        }
        .neg-bubble.merchant{
            background:var(--bubble-merchant-bg);border:1px solid var(--bubble-merchant-border);
            color:var(--bubble-merchant-text);border-bottom-left-radius:3px;
        }
        .neg-divider{
            text-align:center;font-size:.67rem;color:var(--text-muted);
            padding:.3rem 0;border-bottom:1px dashed var(--border);
        }

        /* ── ORDERS ── */
        #page-orders{background:var(--bg);padding:1.5rem 1.75rem;overflow-y:auto;}
        .orders-header{margin-bottom:1.25rem;}
        .orders-header h2{font-size:1rem;font-weight:700;color:var(--text-primary);}
        .orders-header p{font-size:.8rem;color:var(--text-secondary);margin-top:3px;}
        .orders-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);box-shadow:var(--shadow-sm);overflow:hidden;}
        table{width:100%;border-collapse:collapse;}
        thead{background:var(--surface-2);}
        th{text-align:left;padding:.7rem 1.25rem;font-size:.69rem;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:var(--text-muted);border-bottom:1px solid var(--border);}
        td{padding:.85rem 1.25rem;font-size:.845rem;border-bottom:1px solid var(--border-light);vertical-align:middle;}
        tbody tr:last-child td{border-bottom:none;}
        tbody tr:hover{background:var(--surface-2);}
        .receipt-code{font-family:monospace;font-size:.74rem;color:var(--text-secondary);background:var(--bg);padding:2px 6px;border-radius:4px;border:1px solid var(--border-light);}
        .status-badge{display:inline-flex;align-items:center;gap:4px;padding:.22rem .55rem;border-radius:9999px;font-size:.68rem;font-weight:700;text-transform:uppercase;letter-spacing:.04em;}
        .status-badge.paid{background:var(--green-bg);color:var(--green);}
        .status-badge.failed{background:var(--red-bg);color:var(--red);}
        .status-badge.pending{background:var(--yellow-bg);color:var(--yellow);}
        .status-badge::before{content:'';width:5px;height:5px;border-radius:50%;background:currentColor;}
        .empty-state{text-align:center;padding:3rem 1.5rem;color:var(--text-muted);font-size:.84rem;}

        @keyframes fadeUp{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:translateY(0)}}
        ::-webkit-scrollbar{width:5px;}::-webkit-scrollbar-track{background:transparent;}::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px;}
    </style>
</head>
<body>

<!-- HEADER -->
<header>
    <button id="sidebar-toggle" onclick="toggleSidebar()">
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
    </button>
    <span class="logo">Agentic Commerce</span>
    <div class="header-divider"></div>
    <span class="header-subtitle">Autonomous Procurement Platform</span>
    <div class="user-badge">
        <span>vishal_123</span>
        <div class="avatar">V</div>
    </div>
</header>

<div class="app-body">

    <!-- SIDEBAR -->
    <aside id="sidebar">
        <div class="nav-section-label">Navigation</div>

        <button class="nav-item active" id="nav-agent" onclick="showPage('agent')">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
            <span class="nav-label">Procurement Agent</span>
        </button>

        <button class="nav-item" id="nav-orders" onclick="showPage('orders')">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
            <span class="nav-label">Order History</span>
        </button>
    </aside>

    <!-- MAIN -->
    <main>

        <!-- AGENT PAGE -->
        <div class="page active" id="page-agent">

            <div id="chat-pane" class="full">
                <div class="pane-header">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
                    Procurement Console
                </div>
                <div id="chat-messages">
                    <div class="msg agent">Hello! I'm your autonomous Procurement Agent. Tell me what you'd like to buy, and I'll negotiate the best deal for you.</div>
                </div>
                <div id="chat-input-bar">
                    <input type="text" id="chat-input" placeholder="e.g. Get me the best deal on bread..." onkeypress="handleEnter(event)">
                    <button id="send-btn" onclick="sendMessage()">
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
                        Send
                    </button>
                </div>
            </div>

            <div id="pane-resizer"></div>

            <div id="negotiation-pane" class="hidden">
                <div class="pane-header"><div class="live-dot"></div>Negotiation Feed</div>
                <div id="negotiation-feed"></div>
            </div>

        </div>

        <!-- ORDERS PAGE -->
        <div class="page" id="page-orders">
            <div class="orders-header">
                <h2>Order History</h2>
                <p>All procurement transactions processed by your agent</p>
            </div>
            <div class="orders-card">
                <table>
                    <thead><tr><th>Item</th><th>Merchant</th><th>Amount</th><th>Razorpay Receipt</th><th>Status</th></tr></thead>
                    <tbody id="order-table-body"><tr><td colspan="5" class="empty-state">Loading orders...</td></tr></tbody>
                </table>
            </div>
        </div>

    </main>
</div>

<script>
    const MERCHANT_NAMES={
        'merchant_001_electronics':'Electro World','merchant_001_groceries':'Electro World',
        'merchant_002_electronics':'Tech Haven','merchant_003_electronics':'Gizmo Hub',
        'merchant_004_clothing':'Fashion Forward','merchant_005_clothing':'Urban Wear',
        'merchant_006_groceries':'Fresh Market','merchant_007_groceries':'Pantry Essentials'
    };
    const merchantName=id=>id?MERCHANT_NAMES[id]||id:'-';

    function toggleSidebar(){document.getElementById('sidebar').classList.toggle('collapsed');}

    function showPage(name){
        document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));
        document.querySelectorAll('.nav-item').forEach(n=>n.classList.remove('active'));
        document.getElementById('page-'+name).classList.add('active');
        document.getElementById('nav-'+name).classList.add('active');
        if(name==='orders')fetchOrders();
    }

    /* ── Drag resizer ── */
    const resizer=document.getElementById('pane-resizer');
    const chatPane=document.getElementById('chat-pane');
    let isResizing=false;
    resizer.addEventListener('mousedown',()=>{isResizing=true;resizer.classList.add('dragging');document.body.style.userSelect='none';document.body.style.cursor='col-resize';});
    document.addEventListener('mousemove',e=>{
        if(!isResizing)return;
        const rect=document.getElementById('page-agent').getBoundingClientRect();
        let newW=e.clientX-rect.left;
        newW=Math.max(320,Math.min(newW,rect.width-220));
        chatPane.style.width=newW+'px';
    });
    document.addEventListener('mouseup',()=>{if(isResizing){isResizing=false;resizer.classList.remove('dragging');document.body.style.userSelect='';document.body.style.cursor='';}});

    /* ── Chat ── */
    let currentSessionId=null,pollInterval=null;
    const CONFIRM_WORDS=new Set(['yes','y','ok','sure','pay','approve','confirm']);

    function handleEnter(e){if(e.key==='Enter')sendMessage();}

    function appendMessage(text,role){
        const feed=document.getElementById('chat-messages');
        const div=document.createElement('div');
        div.className='msg '+role;div.textContent=text;
        feed.appendChild(div);feed.scrollTop=feed.scrollHeight;
    }
    function showTyping(){
        const feed=document.getElementById('chat-messages');
        const t=document.createElement('div');t.className='typing-indicator';t.id='typing';
        t.innerHTML='<span></span><span></span><span></span>';
        feed.appendChild(t);feed.scrollTop=feed.scrollHeight;
    }
    function removeTyping(){const t=document.getElementById('typing');if(t)t.remove();}

    async function sendMessage(){
        const input=document.getElementById('chat-input');
        const sendBtn=document.getElementById('send-btn');
        const text=input.value.trim();if(!text)return;
        const isConfirm=CONFIRM_WORDS.has(text.toLowerCase());
        appendMessage(text,'user');
        input.value='';sendBtn.disabled=true;showTyping();
        openNegotiationPane();

        if(!isConfirm){
            currentSessionId=crypto.randomUUID().replace(/-/g,'').substring(0,16);
            clearNegotiationFeed();renderedLogIds.clear();
        }else{
            addNegEvent('<div class="neg-divider">Payment approval sent</div>');
        }

        if(pollInterval)clearInterval(pollInterval);
        pollInterval=setInterval(()=>fetchLogs(currentSessionId),2000);

        try{
            const res=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},
                body:JSON.stringify({customer_id:'vishal_123',intent:text,session_id:currentSessionId})});
            const data=await res.json();removeTyping();appendMessage(data.reply,'agent');
        }catch(err){removeTyping();appendMessage('Error communicating with the agent backend.','agent');}
        finally{sendBtn.disabled=false;clearInterval(pollInterval);await fetchLogs(currentSessionId);}
    }

    function openNegotiationPane(){
        const cp=document.getElementById('chat-pane');
        const np=document.getElementById('negotiation-pane');
        const r=document.getElementById('pane-resizer');
        if(cp.classList.contains('full')){
            cp.classList.remove('full');cp.style.width='62%';
            np.classList.remove('hidden');r.classList.add('visible');
        }
    }
    function clearNegotiationFeed(){document.getElementById('negotiation-feed').innerHTML='';}
    function addNegEvent(html){
        const feed=document.getElementById('negotiation-feed');
        feed.insertAdjacentHTML('beforeend',html);feed.scrollTop=feed.scrollHeight;
    }

    const renderedLogIds=new Set();
    async function fetchLogs(sessionId){
        if(!sessionId)return;
        try{
            const res=await fetch('/api/logs/'+sessionId);
            const data=await res.json();if(!data.logs)return;
            data.logs.forEach(log=>{
                if(renderedLogIds.has(log._id))return;
                renderedLogIds.add(log._id);renderLog(log);
            });
        }catch(e){}
    }

    function escHtml(s){if(!s)return'';return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}

    function renderLog(log){
        const action=log.action||'',payload=log.payload||{};
        if(payload.tool_calls&&payload.tool_calls.length>0){
            payload.tool_calls.forEach(tc=>{
                if(tc.name==='query_registry'){
                    addNegEvent('<div class="neg-event tool-call">Registry Query: "'+escHtml((tc.args&&tc.args.user_query)||'')+'"</div>');
                }else if(tc.name==='search_merchant_catalog'){
                    addNegEvent('<div class="neg-event tool-call">Catalog Search &rarr; '+escHtml(merchantName((tc.args&&tc.args.merchant_id)||''))+': "'+escHtml((tc.args&&tc.args.query)||'')+'"</div>');
                }else if(tc.name==='negotiate_with_merchant'){
                    const terms=(tc.args&&tc.args.proposed_terms)||'';
                    const merchant=merchantName((tc.args&&tc.args.merchant_id)||'');
                    addNegEvent('<div class="neg-bubble-wrap buyer-wrap"><div class="neg-bubble-label">Buyer Agent &rarr; '+escHtml(merchant)+'</div><div class="neg-bubble buyer">'+escHtml(terms)+'</div></div>');
                }else if(tc.name==='finalize_deal_and_request_approval'){
                    addNegEvent('<div class="neg-event tool-call">Deal Finalised &mdash; Awaiting approval</div>');
                }else{
                    addNegEvent('<div class="neg-event tool-call">'+escHtml(tc.name)+'</div>');
                }
            });
        }
        if(action==='negotiation_response'&&payload.message){
            const si=payload.status==='accepted'?'Accepted':payload.status==='rejected'?'Rejected':'Counter';
            const tl=payload.final_terms?'\n\nTerms: '+payload.final_terms:'';
            addNegEvent('<div class="neg-bubble-wrap merchant-wrap"><div class="neg-bubble-label">Merchant ['+si+']</div><div class="neg-bubble merchant">'+escHtml(payload.message+tl)+'</div></div>');
        }
    }

    async function fetchOrders(){
        try{
            const res=await fetch('/api/orders/vishal_123');
            const data=await res.json();
            const tbody=document.getElementById('order-table-body');tbody.innerHTML='';
            if(!data.orders||data.orders.length===0){
                tbody.innerHTML='<tr><td colspan="5" class="empty-state">No orders yet</td></tr>';return;
            }
            data.orders.forEach(order=>{
                const status=(order.status||'Pending').toLowerCase();
                const bc=status==='paid'?'paid':status==='failed'?'failed':'pending';
                const amount=order.amount_paise?(order.amount_paise/100).toFixed(2):'-';
                const receipt=order.receipt||order.razorpay_receipt||'-';
                const tr=document.createElement('tr');
                tr.innerHTML='<td>'+escHtml(order.item_description||'-')+'</td>'+
                    '<td>'+escHtml(merchantName(order.merchant_id))+'</td>'+
                    '<td>&#8377;'+amount+'</td>'+
                    '<td><span class="receipt-code">'+escHtml(receipt)+'</span></td>'+
                    '<td><span class="status-badge '+bc+'">'+escHtml(order.status||'Pending')+'</span></td>';
                tbody.appendChild(tr);
            });
        }catch(e){
            document.getElementById('order-table-body').innerHTML='<tr><td colspan="5" class="empty-state">Failed to load orders.</td></tr>';
        }
    }

    document.addEventListener('DOMContentLoaded',()=>{fetchOrders();});
</script>
</body>
</html>"""

with open('static/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Done")

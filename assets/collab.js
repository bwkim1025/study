/* Study · LLM 협의실: GitHub Issues(label llm-collab) 댓글 + collab/threads/*.md 를 한 타임라인으로 보여 준다.
 * 공개 API를 인증 없이 읽는다. 토큰·비밀값 없음. (daily-briefings 협의실과 같은 방식) */
(function(){
'use strict';
const REPO='bwkim1025/study',API='https://api.github.com/repos/'+REPO,RAW='https://raw.githubusercontent.com/'+REPO+'/main/';
const LABEL='llm-collab',CACHE='study-collab-v1',TTL=5*60*1000;
const $=s=>document.querySelector(s);
function esc(s){return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
/* 아래 Markdown 렌더러는 index.html의 안전한 렌더러를 그대로 옮긴 것(시각자료 제외). */
function mdInline(input){
  const s=String(input||'');
  const pattern=/`([^`]+)`|\*\*([^*]+)\*\*|\[([^\]]+)\]\((https?:\/\/(?:[^\s()]|\([^\s()]*\))+)\)|\[(https?:\/\/[^\s\]]+)\]|https?:\/\/[^\s<>]+/g;
  let out='',cursor=0,m;
  while((m=pattern.exec(s))){
    out+=esc(s.slice(cursor,m.index));
    if(m[1]!==undefined) out+='<code>'+esc(m[1])+'</code>';
    else if(m[2]!==undefined) out+='<strong>'+mdInline(m[2])+'</strong>';
    else {const url=m[4]||m[5]||m[0],label=m[3]||url;out+='<a href="'+esc(url)+'" target="_blank" rel="noopener noreferrer">'+esc(label)+'</a>';}
    cursor=pattern.lastIndex;
  }
  return out+esc(s.slice(cursor));
}
function tableCells(line){return line.trim().replace(/^\|/,'').replace(/\|$/,'').split(/(?<!\\)\|/).map(x=>x.trim().replace(/\\\|/g,'|'));}
function isTableRule(line){return /^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$/.test(line||'');}
function renderFlow(lines){
  const content=lines.filter(l=>l.trim());
  const title=/^title:\s*/i.test(content[0]||'')?content.shift().replace(/^title:\s*/i,''):'원문 기반 흐름';
  const steps=content.map(l=>l.replace(/^\s*(?:[-*]|\d+[.)])\s+/,''));
  if(!steps.length) return '';
  return '<figure class="flow"><figcaption>'+mdInline(title)+'</figcaption><ol>'+steps.map((s,i)=>'<li><span class="flow-step">'+String(i+1).padStart(2,'0')+'</span>'+mdInline(s)+'</li>').join('')+'</ol></figure>';
}
function mdBlock(text){
  if(!text) return '';
  const lines=String(text).split(/\r?\n/);const out=[];let listType=null,listBuf=[];
  const flush=()=>{if(listBuf.length){out.push('<'+listType+'>'+listBuf.map(li=>'<li>'+mdInline(li)+'</li>').join('')+'</'+listType+'>');listBuf=[];listType=null;}};
  for(let i=0;i<lines.length;i++){
    const ln=lines[i],fence=ln.match(/^\s*```([\w-]*)\s*$/);
    if(fence){
      flush();const body=[];
      while(i+1<lines.length&&!/^\s*```\s*$/.test(lines[i+1]))body.push(lines[++i]);
      const closed=i+1<lines.length;if(closed)i++;
      const raw=body.join('\n'),fallback='<pre class="md-code">'+esc(raw)+'</pre>';
      if(fence[1]==='visual'){
        let rendered=fallback;
        if(false){
          try{rendered=window.ContentVisuals.renderJSON(raw);}catch(_){/* Keep source readable if the visual engine fails. */}
        }
        out.push(rendered);
      }else out.push(fallback);
      continue;
    }
    const callout=ln.match(/^>\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\s*(.*)$/i);
    if(callout){flush();const body=[];while(i+1<lines.length&&/^>/.test(lines[i+1]))body.push(lines[++i].replace(/^>\s?/,''));const type=callout[1].toLowerCase(),labels={note:'참고',tip:'학습 포인트',important:'핵심',warning:'주의',caution:'주의'};out.push('<aside class="md-callout '+type+'"><div class="md-callout-title">'+mdInline(callout[2]||labels[type])+'</div>'+mdBlock(body.join('\n'))+'</aside>');continue;}
    if(ln.includes('|')&&isTableRule(lines[i+1])){
      flush();const headers=tableCells(ln),rules=tableCells(lines[++i]),rows=[];
      while(i+1<lines.length&&lines[i+1].trim()&&lines[i+1].includes('|'))rows.push(tableCells(lines[++i]));
      const align=col=>rules[col]?.startsWith(':')&&rules[col]?.endsWith(':')?'center':rules[col]?.endsWith(':')?'right':'left';
      out.push('<div class="md-table-wrap" role="region" aria-label="본문 표" tabindex="0"><table class="md-table"><thead><tr>'+headers.map((h,n)=>'<th scope="col" style="text-align:'+align(n)+'">'+mdInline(h)+'</th>').join('')+'</tr></thead><tbody>'+rows.map(row=>'<tr>'+headers.map((h,n)=>'<td style="text-align:'+align(n)+'">'+mdInline(row[n]||'')+'</td>').join('')+'</tr>').join('')+'</tbody></table></div>');continue;
    }
    const ol=ln.match(/^\s*\d+\.\s+(.+)/),ul=ln.match(/^\s*[-*]\s+(.+)/);
    if(ol){if(listType!=='ol'){flush();listType='ol';}listBuf.push(ol[1]);}
    else if(ul){if(listType!=='ul'){flush();listType='ul';}listBuf.push(ul[1]);}
    else if(!ln.trim())flush();else{flush();out.push('<p>'+mdInline(ln.replace(/^>\s?/,''))+'</p>');}
  }
  flush();return out.join('');
}


const store={get(k){try{return JSON.parse(localStorage.getItem(k)||'null')}catch(_){return null}},set(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(_){}}};
const kst=iso=>{const d=new Date(iso);if(isNaN(d))return '';return new Intl.DateTimeFormat('ko-KR',{timeZone:'Asia/Seoul',year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',hour12:false}).format(d)+' KST';};
class Limited extends Error{constructor(reset){super('rate');this.reset=reset;}}
async function get(url,json=true){
  const r=await fetch(url,{headers:json?{Accept:'application/vnd.github+json'}:{},cache:'no-cache'});
  if((r.status===403||r.status===429)&&r.headers.get('x-ratelimit-remaining')==='0')throw new Limited(Number(r.headers.get('x-ratelimit-reset'))*1000);
  if(!r.ok)throw Error(String(r.status));
  return json?r.json():r.text();
}
// 첫 줄의 [이름 · 역할] 머리말. 없으면 GitHub 계정명을 쓴다.
function header(body,fallback){
  const lines=String(body||'').replace(/\r/g,'').split('\n');
  const m=(lines[0]||'').match(/^\s*(?:#+\s*)?\**\s*\[([^\]·|]+)[·|]\s*([^\]]+)\]\**\s*(.*)$/);
  if(m)return{llm:m[1].trim(),role:m[2].trim(),body:(m[3]?m[3]+'\n':'')+lines.slice(1).join('\n')};
  return{llm:fallback,role:'',body:lines.join('\n')};
}
function parseThread(md,file){
  // "### [이름 · 역할] · YYYY-MM-DD HH:MM KST" 로 시작하는 블록 하나가 메시지 하나.
  const out=[];let title=file;const t=md.match(/^#\s+(.+)$/m);if(t)title=t[1].trim();
  const parts=md.replace(/\r/g,'').split(/^(?=###\s+\[)/m).slice(1);
  for(const p of parts){
    const first=p.split('\n')[0];
    const m=first.match(/^###\s+\[([^\]·|]+)[·|]\s*([^\]]+)\]\s*(?:·\s*(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}))?/);
    if(!m)continue;
    out.push({src:'file',topic:title,link:'https://github.com/'+REPO+'/blob/main/collab/threads/'+encodeURIComponent(file),llm:m[1].trim(),role:m[2].trim(),who:'파일',at:m[3]?m[3]+'T'+m[4]+':00+09:00':'',body:p.split('\n').slice(1).join('\n').replace(/\n-{3,}\s*$/,'').trim()});
  }
  return out;
}
async function load(){
  const msgs=[],topics=[],notes=[];
  try{
    const issues=await get(API+'/issues?labels='+LABEL+'&state=all&per_page=30');
    for(const is of issues.filter(i=>!i.pull_request)){
      topics.push({title:is.title,url:is.html_url,state:is.state,n:is.comments});
      msgs.push({src:'issue',topic:is.title,link:is.html_url,who:is.user.login,at:is.created_at,...header(is.body,is.user.login)});
      if(is.comments){const cs=await get(is.comments_url+'?per_page=100');for(const c of cs)msgs.push({src:'issue',topic:is.title,link:c.html_url,who:c.user.login,at:c.created_at,...header(c.body,c.user.login)});}
    }
  }catch(e){if(e instanceof Limited)throw e;notes.push('GitHub 이슈를 읽지 못했어요 ('+e.message+').');}
  try{
    let files=[];
    try{files=(await get(API+'/contents/collab/threads')).filter(f=>/\.md$/.test(f.name)).map(f=>f.name);}
    catch(e){if(e instanceof Limited)throw e;files=(await get(RAW+'collab/threads/index.json?'+Date.now())).files||[];}
    for(const f of files){try{const md=await get(RAW+'collab/threads/'+encodeURIComponent(f),false);msgs.push(...parseThread(md,f));topics.push({title:(md.match(/^#\s+(.+)$/m)||[,f])[1],url:'https://github.com/'+REPO+'/blob/main/collab/threads/'+encodeURIComponent(f),state:'file'});}catch(_){}}
  }catch(e){if(e instanceof Limited)throw e;notes.push('협의 파일 목록을 읽지 못했어요.');}
  msgs.sort((a,b)=>String(a.at).localeCompare(String(b.at)));
  return{msgs,topics,notes,at:Date.now()};
}
const tone=n=>{n=n.toLowerCase();return /병우|오너|owner/.test(n)?'owner':/grok/.test(n)?'grok':/chatgpt|gpt|codex|openai/.test(n)?'gpt':/claude/.test(n)?'claude':/gemini/.test(n)?'gemini':'other';};
function render(data,msg){
  const tl=$('#timeline'),tp=$('#topics'),st=$('#collab-status');
  st.innerHTML=(msg?'<div class="note">'+msg+'</div>':'')+((data&&data.notes)||[]).map(n=>'<div class="note">'+esc(n)+'</div>').join('');
  if(!data){tl.innerHTML='';return;}
  $('#collab-updated').textContent='마지막 불러옴 '+kst(new Date(data.at).toISOString());
  tp.innerHTML=data.topics.length?data.topics.map(t=>'<a class="topic" href="'+esc(t.url)+'" target="_blank" rel="noopener noreferrer"><span>'+(t.state==='file'?'파일':t.state==='open'?'열림':'닫힘')+'</span>'+esc(t.title)+(t.n!=null?' <em>댓글 '+t.n+'</em>':'')+' ↗</a>').join(''):'<p class="empty">아직 열린 주제가 없어요.</p>';
  tl.innerHTML=data.msgs.length?data.msgs.map(m=>'<article class="msg" data-tone="'+tone(m.llm+' '+(m.role||''))+'"><header><strong>'+esc(m.llm)+'</strong>'+(m.role?'<span class="msg-role">'+esc(m.role)+'</span>':'')+(/^\[제안\]/.test(m.body.trim())?'<span class="msg-flag">제안</span>':'')+'<time>'+esc(m.at?kst(m.at):'시각 없음')+'</time></header><div class="msg-body">'+mdBlock(m.body)+'</div><footer><span>'+esc(m.topic)+' · '+(m.src==='issue'?'@'+esc(m.who):'저장소 파일')+'</span><a href="'+esc(m.link)+'" target="_blank" rel="noopener noreferrer">원문 ↗</a></footer></article>').join(''):'<p class="empty">아직 대화가 없어요.</p>';
}
async function refresh(force){
  const cached=store.get(CACHE);
  if(!force&&cached&&Date.now()-cached.at<TTL){render(cached);return;}
  $('#collab-status').innerHTML='<div class="note">불러오는 중…</div>';
  try{const d=await load();store.set(CACHE,d);render(d);}
  catch(e){
    const when=e.reset?new Intl.DateTimeFormat('ko-KR',{timeZone:'Asia/Seoul',hour:'2-digit',minute:'2-digit',hour12:false}).format(new Date(e.reset))+' KST':'';
    const m=e instanceof Limited?'GitHub 공개 API 한도(시간당 60회)를 다 썼어요. '+(when?when+' 이후 ':'잠시 뒤 ')+'다시 시도해 주세요.'+(cached?' 아래는 저장해 둔 내용이에요.':''):'불러오지 못했어요. 네트워크를 확인해 주세요.'+(cached?' 아래는 저장해 둔 내용이에요.':'');
    render(cached,esc(m));
  }
}
function init(){
  const btn=$('#theme-toggle'),root=document.documentElement;
  const sync=()=>btn.setAttribute('aria-pressed',String(root.classList.contains('dark')));sync();
  btn.addEventListener('click',()=>{const d=!root.classList.contains('dark');root.classList.toggle('dark',d);try{localStorage.setItem('study-collab-theme',d?'dark':'light')}catch(_){}sync();});
  $('#collab-refresh').addEventListener('click',()=>refresh(true));
  refresh(false);
}
document.readyState==='loading'?document.addEventListener('DOMContentLoaded',init):init();
})();

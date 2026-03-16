'use client'

import React, { useState, useMemo, useRef, useEffect, useCallback } from 'react'
import { supabase } from '../../lib/supabase'
import type { Feature, FeatureInput } from '../../lib/supabase'

/* ═══════════════════════════════════════════════════════════════
   CONFIG
═══════════════════════════════════════════════════════════════ */
const CAT: Record<string, { color:string; dim:string; border:string; icon:string }> = {
  'Core Gameplay':    { color:'#8b5cf6', dim:'rgba(139,92,246,0.13)',  border:'rgba(139,92,246,0.35)', icon:'⚔️' },
  'Monetization':     { color:'#f59e0b', dim:'rgba(245,158,11,0.13)',  border:'rgba(245,158,11,0.35)', icon:'💎' },
  'LiveOps Event':    { color:'#f43f5e', dim:'rgba(244,63,94,0.13)',   border:'rgba(244,63,94,0.35)',  icon:'🎯' },
  'Meta Progression': { color:'#22d3ee', dim:'rgba(34,211,238,0.12)',  border:'rgba(34,211,238,0.35)', icon:'📈' },
  'Infrastructure':   { color:'#10b981', dim:'rgba(16,185,129,0.12)',  border:'rgba(16,185,129,0.35)', icon:'⚙️' },
}
const STATUS_CFG: Record<string, { color:string; progress:number }> = {
  'Planned':         { color:'#6b7280', progress:5   },
  'In Development':  { color:'#3b82f6', progress:40  },
  'QA':              { color:'#f59e0b', progress:75  },
  'Ready to Launch': { color:'#10b981', progress:95  },
  'Released':        { color:'#8b5cf6', progress:100 },
}
const IMPACT_CFG: Record<string, { color:string; badge:string }> = {
  'Low':    { color:'#6b7280', badge:'L' },
  'Medium': { color:'#f59e0b', badge:'M' },
  'High':   { color:'#f43f5e', badge:'H' },
}
const FILTERS = [
  { key:'Core Gameplay',    label:'Gameplay',    icon:'⚔️' },
  { key:'Monetization',     label:'Revenue',     icon:'💎' },
  { key:'LiveOps Event',    label:'LiveOps',     icon:'🎯' },
  { key:'Meta Progression', label:'Progression', icon:'📈' },
  { key:'Infrastructure',   label:'Infra',       icon:'⚙️' },
]
const MONTHS_LIST = [
  { year:2026, month:2, name:'March 2026' },
  { year:2026, month:3, name:'April 2026' },
  { year:2026, month:4, name:'May 2026'   },
]
const TODAY       = new Date(2026, 2, 16)
const TL_START    = new Date(2026, 2, 15)
const TL_END      = new Date(2026, 4, 10)

/* ═══════════════════════════════════════════════════════════════
   HELPERS
═══════════════════════════════════════════════════════════════ */
const parseDate    = (s: string) => { const [y,m,d]=s.split('-').map(Number); return new Date(y,m-1,d) }
const daysBetween  = (a: Date, b: Date) => Math.round((b.getTime()-a.getTime())/86400000)
const fmtShort     = (d: Date) => d.toLocaleDateString('en-US',{month:'short',day:'numeric'})
const fmtLong      = (s: string) => parseDate(s).toLocaleDateString('en-US',{month:'long',day:'numeric',year:'numeric'})
const daysInMonth  = (y: number, m: number) => new Date(y,m+1,0).getDate()
const firstDayOf   = (y: number, m: number) => new Date(y,m,1).getDay()
const dateToStr    = (d: Date) => `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`

const EMPTY: FeatureInput = {
  name:'', date:'2026-03-18', start_date:'', description:'',
  cat:'Core Gameplay', status:'Planned', impact:'Medium', owner:'Product',
}

/* ═══════════════════════════════════════════════════════════════
   FEATURE FORM
═══════════════════════════════════════════════════════════════ */
function FeatureForm({ form, onChange }: { form: FeatureInput; onChange: (k: keyof FeatureInput, v: string) => void }) {
  const LBL = ({ children }: { children: React.ReactNode }) => (
    <div style={{ fontFamily:'var(--font-dm-mono,DM Mono,monospace)', fontSize:9, color:'rgba(255,255,255,0.38)', marginBottom:5, letterSpacing:'0.1em', textTransform:'uppercase' }}>{children}</div>
  )
  return (
    <div style={{ display:'flex', flexDirection:'column', gap:11 }}>
      <div>
        <LBL>Feature Name *</LBL>
        <input className="rm-input" value={form.name} onChange={e=>onChange('name',e.target.value)} placeholder="e.g. Battle Pass Season 5" autoFocus />
      </div>
      <div>
        <LBL>Description</LBL>
        <textarea className="rm-input" value={form.description} onChange={e=>onChange('description',e.target.value)} placeholder="One sentence describing this feature…" />
      </div>
      <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr 1fr', gap:10 }}>
        <div>
          <LBL>Start Date</LBL>
          <input type="date" className="rm-input" value={form.start_date} onChange={e=>onChange('start_date',e.target.value)} />
        </div>
        <div>
          <LBL>Launch Date *</LBL>
          <input type="date" className="rm-input" value={form.date} onChange={e=>onChange('date',e.target.value)} />
        </div>
        <div>
          <LBL>Owner</LBL>
          <select className="rm-input" value={form.owner} onChange={e=>onChange('owner',e.target.value)}>
            {['Product','Engineering','Design'].map(o=><option key={o}>{o}</option>)}
          </select>
        </div>
      </div>
      <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr 1fr', gap:10 }}>
        <div>
          <LBL>Category</LBL>
          <select className="rm-input" value={form.cat} onChange={e=>onChange('cat',e.target.value)}>
            {Object.keys(CAT).map(c=><option key={c}>{c}</option>)}
          </select>
        </div>
        <div>
          <LBL>Status</LBL>
          <select className="rm-input" value={form.status} onChange={e=>onChange('status',e.target.value)}>
            {Object.keys(STATUS_CFG).map(s=><option key={s}>{s}</option>)}
          </select>
        </div>
        <div>
          <LBL>Impact</LBL>
          <select className="rm-input" value={form.impact} onChange={e=>onChange('impact',e.target.value)}>
            {['Low','Medium','High'].map(i=><option key={i}>{i}</option>)}
          </select>
        </div>
      </div>
    </div>
  )
}

/* ═══════════════════════════════════════════════════════════════
   FEATURE MODAL
═══════════════════════════════════════════════════════════════ */
interface ModalProps {
  feature:  Feature | FeatureInput
  isNew:    boolean
  saving:   boolean
  saveErr?: string | null
  onClose:  () => void
  onSave:   (f: Feature | FeatureInput) => void
  onDelete: (id: number) => void
}
function FeatureModal({ feature, isNew, saving, saveErr, onClose, onSave, onDelete }: ModalProps) {
  const [editing, setEditing] = useState(!!isNew)
  const [form, setForm]       = useState<Feature | FeatureInput>({ ...feature })

  const c  = CAT[form.cat]    ?? CAT['Core Gameplay']
  const st = STATUS_CFG[form.status] ?? STATUS_CFG['Planned']
  const canSave = (form.name ?? '').trim() !== '' && (form.date ?? '') !== ''

  useEffect(() => {
    const fn = (e: KeyboardEvent) => e.key==='Escape' && onClose()
    window.addEventListener('keydown', fn)
    return () => window.removeEventListener('keydown', fn)
  }, [onClose])

  const ch = (k: keyof FeatureInput, v: string) => setForm(p => ({...p, [k]: v}))

  return (
    <div className="rm-fade-in" onClick={onClose} style={{ position:'fixed', inset:0, zIndex:300, background:'rgba(0,0,0,0.75)', backdropFilter:'blur(10px)', display:'flex', alignItems:'center', justifyContent:'center', padding:20 }}>
      <div className="rm-fade-up" onClick={e=>e.stopPropagation()} style={{ background:'#0d1020', border:`1px solid ${c.border}`, borderRadius:16, padding:24, width:'100%', maxWidth:500, maxHeight:'90vh', overflow:'auto', boxShadow:`0 0 70px ${c.color}18` }}>

        {/* Header */}
        <div style={{ display:'flex', gap:12, alignItems:'center', marginBottom:18 }}>
          <div style={{ width:44, height:44, borderRadius:12, background:c.dim, border:`2px solid ${c.color}50`, display:'flex', alignItems:'center', justifyContent:'center', fontSize:20, flexShrink:0 }}>{c.icon}</div>
          <div style={{ flex:1, minWidth:0 }}>
            {editing
              ? <input className="rm-input" style={{ fontSize:15, fontWeight:800, padding:'4px 8px' }} value={form.name} onChange={e=>ch('name',e.target.value)} placeholder="Feature name…" autoFocus />
              : <div style={{ fontFamily:'var(--font-syne,Syne,sans-serif)', fontWeight:800, fontSize:16, lineHeight:1.2 }}>{form.name}</div>
            }
            <div style={{ fontFamily:'var(--font-dm-mono,DM Mono,monospace)', fontSize:10, color:c.color, marginTop:3 }}>{form.cat}</div>
          </div>
          <div style={{ display:'flex', gap:6, flexShrink:0 }}>
            {!isNew && !editing && (
              <button className="rm-btn" onClick={()=>setEditing(true)} style={{ padding:'5px 13px', borderRadius:8, border:'1px solid rgba(255,255,255,0.12)', background:'rgba(255,255,255,0.06)', color:'rgba(255,255,255,0.8)', fontSize:11, fontWeight:700 }}>✏ Edit</button>
            )}
            {editing && !isNew && (
              <button className="rm-btn" onClick={()=>{ setForm({...feature}); setEditing(false) }} style={{ padding:'5px 10px', borderRadius:8, border:'1px solid rgba(255,255,255,0.1)', background:'transparent', color:'rgba(255,255,255,0.4)', fontSize:11 }}>Cancel</button>
            )}
            <button className="rm-btn" onClick={onClose} style={{ padding:'5px 10px', borderRadius:8, border:'1px solid rgba(255,255,255,0.1)', background:'rgba(255,255,255,0.05)', color:'rgba(255,255,255,0.5)', fontSize:14 }}>✕</button>
          </div>
        </div>

        {/* Body */}
        {editing ? (
          <FeatureForm form={form} onChange={ch} />
        ) : (
          <>
            {form.description && <p style={{ fontSize:13, color:'rgba(255,255,255,0.62)', lineHeight:1.65, marginBottom:16 }}>{form.description}</p>}
            <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:8, marginBottom:14 }}>
              {[
                { l: form.start_date ? 'Date Range' : 'Launch Date',
                  v: form.start_date ? `${fmtShort(parseDate(form.start_date))} → ${fmtShort(parseDate(form.date))}` : fmtLong(form.date),
                  i:'📅' },
                { l:'Owner',       v:form.owner,         i:'👤' },
                { l:'Category',    v:form.cat,           i:c.icon },
                { l:'Impact',      v:form.impact,        i:form.impact==='High'?'🔥':form.impact==='Medium'?'⚡':'—' },
              ].map(item=>(
                <div key={item.l} style={{ padding:'9px 11px', borderRadius:9, background:'rgba(255,255,255,0.04)', border:'1px solid rgba(255,255,255,0.07)' }}>
                  <div style={{ fontFamily:'var(--font-dm-mono,DM Mono,monospace)', fontSize:9, color:'rgba(255,255,255,0.3)', marginBottom:4, letterSpacing:'0.06em' }}>{item.l}</div>
                  <div style={{ fontSize:12, fontWeight:600 }}>{item.i} {item.v}</div>
                </div>
              ))}
            </div>
            <div style={{ padding:'12px 14px', borderRadius:10, background:'rgba(255,255,255,0.04)', border:'1px solid rgba(255,255,255,0.07)' }}>
              <div style={{ display:'flex', justifyContent:'space-between', marginBottom:8 }}>
                <span style={{ fontFamily:'var(--font-dm-mono,DM Mono,monospace)', fontSize:10, color:'rgba(255,255,255,0.35)' }}>Status</span>
                <span style={{ fontFamily:'var(--font-dm-mono,DM Mono,monospace)', fontSize:10, color:st.color }}>{form.status}</span>
              </div>
              <div style={{ height:6, background:'rgba(255,255,255,0.07)', borderRadius:3 }}>
                <div className="rm-prog" style={{ height:'100%', width:`${st.progress}%`, background:`linear-gradient(90deg,${st.color}70,${st.color})`, borderRadius:3, boxShadow:`0 0 8px ${st.color}55` }} />
              </div>
              <div style={{ display:'flex', justifyContent:'space-between', marginTop:7 }}>
                {Object.entries(STATUS_CFG).map(([s,cfg])=>(
                  <span key={s} style={{ fontFamily:'var(--font-dm-mono,DM Mono,monospace)', fontSize:8.5, color:form.status===s?cfg.color:'rgba(255,255,255,0.18)', fontWeight:form.status===s?700:400 }}>{s.split(' ')[0]}</span>
                ))}
              </div>
            </div>
          </>
        )}

        {/* Footer */}
        {saveErr && (
          <div style={{ margin:'12px 0 0', padding:'8px 12px', borderRadius:8, background:'rgba(244,63,94,0.1)', border:'1px solid rgba(244,63,94,0.3)', fontFamily:'var(--font-dm-mono,DM Mono,monospace)', fontSize:10, color:'#f43f5e' }}>
            ⚠ {saveErr}
          </div>
        )}
        <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginTop:18 }}>
          <div>
            {!isNew && 'id' in feature && (
              <button className="rm-btn" onClick={()=>onDelete((feature as Feature).id)} style={{ padding:'7px 14px', borderRadius:8, border:'1px solid rgba(244,63,94,0.3)', background:'rgba(244,63,94,0.08)', color:'rgba(244,63,94,0.75)', fontSize:11, fontWeight:600 }}>🗑 Delete</button>
            )}
          </div>
          {editing && (
            <button className="rm-btn" onClick={()=>onSave(form)} disabled={!canSave || saving} style={{ padding:'8px 22px', borderRadius:8, border:'none', background:canSave&&!saving?'linear-gradient(135deg,#8b5cf6,#6d28d9)':'rgba(255,255,255,0.08)', color:canSave&&!saving?'#fff':'rgba(255,255,255,0.3)', fontSize:12, fontWeight:700 }}>
              {saving ? 'Saving…' : isNew ? '+ Add Feature' : '✓ Save Changes'}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

/* ═══════════════════════════════════════════════════════════════
   FEATURE CARD
═══════════════════════════════════════════════════════════════ */
interface CardProps {
  feature:     Feature
  onEdit:      (f: Feature) => void
  onDragStart?: (id: number) => void
  onDragEnd?:  () => void
  isDragging?: boolean
  compact?:    boolean
}
function FeatureCard({ feature, onEdit, onDragStart, onDragEnd, isDragging=false, compact=false }: CardProps) {
  const c  = CAT[feature.cat]    ?? CAT['Core Gameplay']
  const st = STATUS_CFG[feature.status] ?? STATUS_CFG['Planned']
  const im = IMPACT_CFG[feature.impact] ?? IMPACT_CFG['Medium']
  return (
    <div
      className={`rm-card${isDragging?' dragging':''}`}
      draggable
      onDragStart={e=>{ e.dataTransfer.effectAllowed='move'; onDragStart?.(feature.id) }}
      onDragEnd={()=>onDragEnd?.()}
      onClick={()=>{ if(!isDragging) onEdit(feature) }}
      style={{ background:'#101323', borderRadius:9, border:`1px solid ${c.border}`, borderLeft:`3px solid ${c.color}`, padding:compact?'7px 9px':'10px 12px', position:'relative', overflow:'hidden', userSelect:'none' }}
    >
      <div style={{ position:'absolute', top:0, right:0, bottom:0, width:'38%', background:`linear-gradient(to left,${c.dim},transparent)`, pointerEvents:'none' }} />
      <div style={{ display:'flex', gap:6, alignItems:'flex-start', position:'relative' }}>
        <span style={{ fontSize:compact?12:14, flexShrink:0, marginTop:1 }}>{c.icon}</span>
        <div style={{ flex:1, minWidth:0 }}>
          <div style={{ fontSize:compact?10.5:12, fontWeight:700, lineHeight:1.3, marginBottom:compact?0:4, whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis' }}>{feature.name}</div>
          {!compact && <div style={{ fontSize:10.5, color:'rgba(255,255,255,0.46)', lineHeight:1.5 }}>{feature.description}</div>}
        </div>
        <span style={{ fontFamily:'var(--font-dm-mono,DM Mono,monospace)', fontSize:9, fontWeight:600, padding:'2px 5px', borderRadius:4, background:`${im.color}20`, color:im.color, flexShrink:0 }}>{im.badge}</span>
      </div>
      {!compact && (
        <div style={{ display:'flex', alignItems:'center', gap:7, marginTop:9, position:'relative' }}>
          <span style={{ fontFamily:'var(--font-dm-mono,DM Mono,monospace)', fontSize:9.5, color:c.color, whiteSpace:'nowrap' }}>
            {feature.start_date ? `${fmtShort(parseDate(feature.start_date))} → ${fmtShort(parseDate(feature.date))}` : fmtShort(parseDate(feature.date))}
          </span>
          <div style={{ flex:1, height:2, background:'rgba(255,255,255,0.07)', borderRadius:1 }}>
            <div className="rm-prog" style={{ height:'100%', width:`${st.progress}%`, background:st.color, borderRadius:1 }} />
          </div>
          <span style={{ fontFamily:'var(--font-dm-mono,DM Mono,monospace)', fontSize:9, color:st.color, whiteSpace:'nowrap' }}>{feature.status}</span>
          <span style={{ fontFamily:'var(--font-dm-mono,DM Mono,monospace)', fontSize:9, color:'rgba(255,255,255,0.28)', padding:'2px 5px', borderRadius:4, background:'rgba(255,255,255,0.05)' }}>{feature.owner}</span>
        </div>
      )}
    </div>
  )
}

/* ═══════════════════════════════════════════════════════════════
   SIDEBAR
═══════════════════════════════════════════════════════════════ */
function Sidebar({ features }: { features: Feature[] }) {
  const high      = features.filter(f=>f.impact==='High')
  const catCounts = Object.keys(CAT).map(k=>({ key:k, count:features.filter(f=>f.cat===k).length, ...CAT[k] }))
  const mono      = 'var(--font-dm-mono,DM Mono,monospace)'
  const syne      = 'var(--font-syne,Syne,sans-serif)'
  return (
    <div style={{ width:256, minWidth:256, background:'#090b16', borderRight:'1px solid rgba(255,255,255,0.07)', display:'flex', flexDirection:'column', overflow:'hidden' }}>
      <div style={{ padding:'18px 18px 14px', borderBottom:'1px solid rgba(255,255,255,0.07)' }}>
        <div style={{ display:'flex', alignItems:'center', gap:10, marginBottom:6 }}>
          <div style={{ width:34, height:34, borderRadius:9, background:'linear-gradient(135deg,#f43f5e,#8b5cf6)', display:'flex', alignItems:'center', justifyContent:'center', fontSize:17, flexShrink:0 }}>💥</div>
          <div>
            <div style={{ fontFamily:syne, fontWeight:800, fontSize:15, letterSpacing:'-0.4px' }}>BOINKERS</div>
            <div style={{ fontFamily:mono, fontSize:9, color:'rgba(255,255,255,0.3)', letterSpacing:'0.12em', marginTop:1 }}>PRODUCT ROADMAP</div>
          </div>
        </div>
        <div style={{ fontFamily:mono, fontSize:10, color:'rgba(255,255,255,0.28)', marginTop:6 }}>Mar – May 2026 · {features.length} features</div>
      </div>
      <div className="rm-sidebar-body" style={{ padding:'14px 16px', display:'flex', flexDirection:'column', gap:18 }}>
        <SbSection label="Strategic Goals">
          {[['🔄','Improve Retention','D1/D7/D30'],['💰','Increase Monetization','ARPU'],['🎮','New Gameplay Depth','Session Length']].map(([i,t,k])=>(
            <div key={t} style={{ display:'flex', gap:8, alignItems:'center', padding:'7px 9px', borderRadius:8, background:'rgba(255,255,255,0.03)', border:'1px solid rgba(255,255,255,0.05)', marginBottom:5 }}>
              <span style={{ fontSize:13 }}>{i}</span>
              <div><div style={{ fontSize:11, fontWeight:700 }}>{t}</div><div style={{ fontFamily:mono, fontSize:9, color:'rgba(255,255,255,0.3)', marginTop:2 }}>{k}</div></div>
            </div>
          ))}
        </SbSection>
        <SbSection label="KPIs Impacted">
          <div style={{ display:'flex', gap:5 }}>
            {[['Retention','#22d3ee'],['ARPU','#f59e0b'],['Engagement','#8b5cf6']].map(([l,c])=>(
              <div key={l} style={{ flex:1, padding:'7px 4px', borderRadius:8, textAlign:'center', background:`${c}14`, border:`1px solid ${c}38` }}>
                <div style={{ fontFamily:mono, fontSize:9, color:c, fontWeight:500 }}>{l}</div>
              </div>
            ))}
          </div>
        </SbSection>
        <SbSection label="By Category">
          {catCounts.filter(c=>c.count>0).map(c=>(
            <div key={c.key} style={{ display:'flex', alignItems:'center', gap:7, marginBottom:7 }}>
              <span style={{ fontSize:11 }}>{c.icon}</span>
              <div style={{ flex:1 }}>
                <div style={{ display:'flex', justifyContent:'space-between', marginBottom:3 }}>
                  <span style={{ fontSize:10.5, color:'rgba(255,255,255,0.58)', fontWeight:600 }}>{c.key.split(' ')[0]}</span>
                  <span style={{ fontFamily:mono, fontSize:10, color:c.color }}>{c.count}</span>
                </div>
                <div style={{ height:2, background:'rgba(255,255,255,0.06)', borderRadius:1 }}>
                  <div style={{ height:'100%', width:`${(c.count/Math.max(features.length,1))*100}%`, background:c.color, borderRadius:1, transition:'width 0.7s ease' }} />
                </div>
              </div>
            </div>
          ))}
        </SbSection>
        <SbSection label="Big Bets 🎰">
          {high.map(f=>{ const c=CAT[f.cat]??CAT['Core Gameplay']; return (
            <div key={f.id} style={{ padding:'7px 9px', borderRadius:8, marginBottom:5, background:c.dim, borderLeft:`3px solid ${c.color}` }}>
              <div style={{ fontSize:11, fontWeight:700, lineHeight:1.3, marginBottom:2 }}>{f.name}</div>
              <div style={{ fontFamily:mono, fontSize:9, color:'rgba(255,255,255,0.35)' }}>{fmtShort(parseDate(f.date))} · {f.cat}</div>
            </div>
          ) })}
        </SbSection>
      </div>
    </div>
  )
}
function SbSection({ label, children }: { label:string; children:React.ReactNode }) {
  return (
    <section>
      <div style={{ fontFamily:'var(--font-dm-mono,DM Mono,monospace)', fontSize:9, letterSpacing:'0.12em', color:'rgba(255,255,255,0.28)', textTransform:'uppercase', fontWeight:500, marginBottom:9, paddingBottom:5, borderBottom:'1px solid rgba(255,255,255,0.05)' }}>{label}</div>
      {children}
    </section>
  )
}

/* ═══════════════════════════════════════════════════════════════
   HEADER
═══════════════════════════════════════════════════════════════ */
interface HeaderProps {
  view: string; setView: (v:string)=>void
  filters: string[]; setFilters: (f:string[])=>void
  count: number; saving: boolean
  onAdd: ()=>void
}
function Header({ view, setView, filters, setFilters, count, saving, onAdd }: HeaderProps) {
  const toggle = (k:string) => setFilters(filters.includes(k) ? filters.filter(x=>x!==k) : [...filters,k])
  return (
    <div style={{ padding:'10px 18px', borderBottom:'1px solid rgba(255,255,255,0.07)', background:'rgba(9,11,22,0.92)', backdropFilter:'blur(12px)', display:'flex', alignItems:'center', gap:10, flexWrap:'wrap', position:'sticky', top:0, zIndex:20 }}>
      <div style={{ display:'flex', gap:2, padding:3, background:'rgba(255,255,255,0.05)', borderRadius:10, border:'1px solid rgba(255,255,255,0.07)' }}>
        {[{k:'timeline',l:'Timeline',i:'⟶'},{k:'month',l:'Month',i:'▦'},{k:'list',l:'List',i:'≡'}].map(v=>(
          <button key={v.k} className="rm-btn" onClick={()=>setView(v.k)} style={{ padding:'5px 13px', borderRadius:7, fontSize:11.5, fontWeight:700, background:view===v.k?'rgba(255,255,255,0.1)':'transparent', color:view===v.k?'#fff':'rgba(255,255,255,0.38)', transition:'all 0.15s' }}>
            <span style={{ marginRight:5 }}>{v.i}</span>{v.l}
          </button>
        ))}
      </div>
      <div style={{ flex:1 }} />
      <div style={{ display:'flex', gap:5, alignItems:'center', flexWrap:'wrap' }}>
        <span style={{ fontFamily:'var(--font-dm-mono,DM Mono,monospace)', fontSize:9.5, color:'rgba(255,255,255,0.22)', letterSpacing:'0.08em' }}>FILTER</span>
        {FILTERS.map(opt=>{ const c=CAT[opt.key]; const active=filters.includes(opt.key); return (
          <button key={opt.key} className="rm-btn" onClick={()=>toggle(opt.key)} style={{ padding:'4px 10px', borderRadius:20, fontSize:10.5, fontWeight:700, border:`1px solid ${active?c.color:'rgba(255,255,255,0.1)'}`, background:active?c.dim:'transparent', color:active?c.color:'rgba(255,255,255,0.38)', transition:'all 0.14s', display:'flex', alignItems:'center', gap:4 }}>
            {opt.icon} {opt.label}
          </button>
        ) })}
        {filters.length>0 && <button className="rm-btn" onClick={()=>setFilters([])} style={{ padding:'4px 8px', borderRadius:20, fontSize:10, fontFamily:'var(--font-dm-mono,DM Mono,monospace)', border:'1px solid rgba(255,255,255,0.1)', background:'transparent', color:'rgba(255,255,255,0.3)' }}>✕</button>}
      </div>
      <span style={{ fontFamily:'var(--font-dm-mono,DM Mono,monospace)', fontSize:10, color:'rgba(255,255,255,0.25)' }}>{count} launches</span>
      {saving && <span style={{ fontFamily:'var(--font-dm-mono,DM Mono,monospace)', fontSize:10, color:'#8b5cf6' }}>Saving…</span>}
      <button className="rm-btn" onClick={onAdd} style={{ padding:'6px 14px', borderRadius:9, border:'none', background:'linear-gradient(135deg,#8b5cf6,#6d28d9)', color:'#fff', fontSize:12, fontWeight:700, display:'flex', alignItems:'center', gap:6, boxShadow:'0 0 16px rgba(139,92,246,0.35)' }}>
        + Add Feature
      </button>
    </div>
  )
}

/* ═══════════════════════════════════════════════════════════════
   TIMELINE VIEW
═══════════════════════════════════════════════════════════════ */
function TimelineView({ features, onEdit, onUpdateDates }: { features:Feature[]; onEdit:(f:Feature)=>void; onUpdateDates:(id:number,date:string,startDate?:string)=>void }) {
  const [dragId,      setDragId]      = useState<number|null>(null)
  const [dragOverDay, setDragOverDay] = useState<number|null>(null)
  const scrollRef = useRef<HTMLDivElement>(null)

  const DAY_W = 46, ROW_H = 64, HDR_H = 62
  const TOTAL = daysBetween(TL_START, TL_END) + 1
  const TOD_X = daysBetween(TL_START, TODAY)

  useEffect(() => { if (scrollRef.current) scrollRef.current.scrollLeft = Math.max(0, TOD_X*DAY_W-180) }, [])

  const months = useMemo(() => {
    const segs: {label:string;s:number;e:number;days:number}[] = []
    let cur = new Date(TL_START.getFullYear(), TL_START.getMonth(), 1)
    while (cur <= TL_END) {
      const mEnd = new Date(cur.getFullYear(), cur.getMonth()+1, 0)
      const s = Math.max(0, daysBetween(TL_START, cur))
      const e = Math.min(TOTAL-1, daysBetween(TL_START, mEnd))
      if (s <= TOTAL-1) segs.push({ label:cur.toLocaleString('en-US',{month:'long',year:'numeric'}), s, e, days:e-s+1 })
      cur = new Date(cur.getFullYear(), cur.getMonth()+1, 1)
    }
    return segs
  }, [TOTAL])

  const { featureRows, numRows } = useMemo(() => {
    const sorted = [...features].sort((a,b)=>{
      const aS = a.start_date ? parseDate(a.start_date) : parseDate(a.date)
      const bS = b.start_date ? parseDate(b.start_date) : parseDate(b.date)
      return aS.getTime()-bS.getTime()
    })
    const tails: number[] = [], fRows: Record<number,number> = {}
    sorted.forEach(f => {
      const startX = daysBetween(TL_START, f.start_date ? parseDate(f.start_date) : parseDate(f.date))
      const endX   = daysBetween(TL_START, parseDate(f.date))
      let r = tails.findIndex(t => startX >= t + 3)
      if (r===-1) { r=tails.length; tails.push(endX) } else tails[r]=endX
      fRows[f.id] = r
    })
    return { featureRows:fRows, numRows:Math.max(tails.length,1) }
  }, [features])

  const days = useMemo(() => Array.from({length:TOTAL},(_,i)=>{
    const d = new Date(TL_START.getFullYear(), TL_START.getMonth(), TL_START.getDate()+i)
    return { i, d, isToday:i===TOD_X, isWeekend:d.getDay()===0||d.getDay()===6 }
  }), [TOTAL, TOD_X])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    if (!scrollRef.current) return
    const rect = scrollRef.current.getBoundingClientRect()
    const x = e.clientX - rect.left + scrollRef.current.scrollLeft
    setDragOverDay(Math.max(0, Math.min(Math.floor(x/DAY_W), TOTAL-1)))
  }, [TOTAL, DAY_W])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    if (dragId!==null && dragOverDay!==null) {
      const feat = features.find(f=>f.id===dragId)
      const nd = new Date(TL_START.getFullYear(), TL_START.getMonth(), TL_START.getDate()+dragOverDay)
      if (feat?.start_date) {
        const delta = dragOverDay - daysBetween(TL_START, parseDate(feat.date))
        const oldS  = parseDate(feat.start_date)
        const newS  = new Date(oldS.getTime() + delta*86400000)
        onUpdateDates(dragId, dateToStr(nd), dateToStr(newS))
      } else {
        onUpdateDates(dragId, dateToStr(nd))
      }
    }
    setDragId(null); setDragOverDay(null)
  }, [dragId, dragOverDay, features, onUpdateDates])

  const totalH = HDR_H + numRows*ROW_H + 32
  const mono = 'var(--font-dm-mono,DM Mono,monospace)'
  const syne = 'var(--font-syne,Syne,sans-serif)'

  return (
    <div style={{ flex:1, overflow:'hidden', display:'flex', flexDirection:'column' }}>
      {dragId!==null && (
        <div style={{ padding:'6px 18px', background:'rgba(139,92,246,0.1)', borderBottom:'1px solid rgba(139,92,246,0.2)', display:'flex', alignItems:'center', gap:8 }}>
          <span style={{ fontSize:12 }}>📅</span>
          <span style={{ fontFamily:mono, fontSize:10, color:'rgba(139,92,246,0.9)' }}>
            {dragOverDay!==null ? `Drop to move launch to ${fmtShort(new Date(TL_START.getFullYear(), TL_START.getMonth(), TL_START.getDate()+dragOverDay))}` : 'Drag over the timeline to pick a new date'}
          </span>
        </div>
      )}
      <div ref={scrollRef} className="rm-tl-scroll" onDragOver={dragId!==null?handleDragOver:undefined} onDrop={dragId!==null?handleDrop:undefined} onDragEnd={()=>{setDragId(null);setDragOverDay(null)}} style={{ flex:1 }}>
        <div style={{ width:TOTAL*DAY_W, minHeight:totalH, position:'relative' }}>

          {/* Sticky header */}
          <div style={{ position:'sticky', top:0, zIndex:10, height:HDR_H, background:'#07080f', borderBottom:'1px solid rgba(255,255,255,0.07)' }}>
            {months.map((m,i)=>(
              <div key={i} style={{ position:'absolute', left:m.s*DAY_W, top:0, width:m.days*DAY_W, height:HDR_H, borderRight:'1px solid rgba(255,255,255,0.07)', paddingLeft:10, paddingTop:9 }}>
                <div style={{ fontFamily:syne, fontWeight:700, fontSize:11.5, color:'rgba(255,255,255,0.68)' }}>{m.label}</div>
              </div>
            ))}
            <div style={{ position:'absolute', bottom:0, left:0, display:'flex' }}>
              {days.map(({i,d,isToday,isWeekend})=>(
                <div key={i} style={{ width:DAY_W, textAlign:'center', fontFamily:mono, fontSize:9.5, paddingBottom:6, color:isToday?'#fff':isWeekend?'rgba(255,255,255,0.17)':'rgba(255,255,255,0.3)' }}>
                  {isToday ? <span style={{ display:'inline-flex', alignItems:'center', justifyContent:'center', width:22, height:22, background:'#f43f5e', borderRadius:'50%', fontSize:9, fontWeight:700, lineHeight:1 }}>{d.getDate()}</span> : d.getDate()}
                </div>
              ))}
            </div>
          </div>

          {/* Grid */}
          {days.map(({i,isWeekend})=>(
            <div key={i} style={{ position:'absolute', left:i*DAY_W, top:HDR_H, width:DAY_W, bottom:0, background:isWeekend?'rgba(255,255,255,0.008)':'transparent', borderRight:'1px solid rgba(255,255,255,0.025)', pointerEvents:'none' }} />
          ))}

          {/* Drop highlight */}
          {dragId!==null && dragOverDay!==null && (
            <div style={{ position:'absolute', left:dragOverDay*DAY_W, top:HDR_H, width:DAY_W, bottom:0, background:'rgba(139,92,246,0.2)', border:'1px solid rgba(139,92,246,0.5)', pointerEvents:'none', zIndex:8 }}>
              <div style={{ position:'sticky', top:HDR_H+8, display:'flex', justifyContent:'center' }}>
                <span style={{ fontFamily:mono, fontSize:9, color:'#8b5cf6', background:'rgba(0,0,0,0.7)', padding:'2px 6px', borderRadius:4, whiteSpace:'nowrap' }}>
                  {fmtShort(new Date(TL_START.getFullYear(), TL_START.getMonth(), TL_START.getDate()+dragOverDay))}
                </span>
              </div>
            </div>
          )}

          {/* Today line */}
          {TOD_X>=0 && TOD_X<TOTAL && (
            <div className="rm-today-ln" style={{ position:'absolute', left:TOD_X*DAY_W+DAY_W/2-0.5, top:HDR_H, bottom:0, width:1, background:'linear-gradient(to bottom,#f43f5e,rgba(244,63,94,0.06))', zIndex:5, pointerEvents:'none' }}>
              <div style={{ position:'absolute', top:6, left:'50%', transform:'translateX(-50%)', fontFamily:mono, fontSize:7.5, color:'#f43f5e', letterSpacing:'0.1em', whiteSpace:'nowrap' }}>TODAY</div>
            </div>
          )}

          {/* Features */}
          {features.map(f=>{
            const c        = CAT[f.cat]    ?? CAT['Core Gameplay']
            const st       = STATUS_CFG[f.status] ?? STATUS_CFG['Planned']
            const dx       = daysBetween(TL_START, parseDate(f.date))
            const row      = featureRows[f.id] ?? 0
            const cy       = HDR_H + row*ROW_H
            const isDragging = dragId===f.id
            const hasRange = !!f.start_date

            if (hasRange) {
              // Bar rendering: spans from start_date to date
              const sx       = daysBetween(TL_START, parseDate(f.start_date))
              const barLeft  = sx * DAY_W + 2
              const barWidth = Math.max(DAY_W - 4, (dx - sx + 1) * DAY_W - 4)
              return (
                <React.Fragment key={f.id}>
                  <div
                    draggable
                    onDragStart={e=>{e.dataTransfer.effectAllowed='move';setDragId(f.id)}}
                    onDragEnd={()=>{setDragId(null);setDragOverDay(null)}}
                    onClick={()=>{ if(!isDragging) onEdit(f) }}
                    title={`${f.name}\n${fmtShort(parseDate(f.start_date))} → ${fmtShort(parseDate(f.date))}`}
                    style={{ position:'absolute', left:barLeft, top:cy+12, width:barWidth, height:34, borderRadius:7, background:isDragging?'rgba(139,92,246,0.2)':c.dim, border:`1px solid ${isDragging?'rgba(139,92,246,0.5)':c.color}40`, borderLeft:`3px solid ${c.color}`, display:'flex', alignItems:'center', paddingLeft:8, cursor:'grab', zIndex:6, opacity:isDragging?0.35:1, overflow:'hidden', userSelect:'none' }}
                  >
                    <span style={{ fontSize:11, marginRight:5, flexShrink:0 }}>{c.icon}</span>
                    <span style={{ fontFamily:mono, fontSize:10, fontWeight:700, color:'rgba(255,255,255,0.88)', whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis', flex:1 }}>{f.name}</span>
                    <span style={{ fontFamily:mono, fontSize:8, color:c.color, padding:'1px 5px', borderRadius:3, background:`${c.color}18`, flexShrink:0, marginRight:6 }}>{f.status.split(' ')[0]}</span>
                    {/* Progress fill */}
                    <div style={{ position:'absolute', bottom:0, left:0, width:`${st.progress}%`, height:2, background:c.color, borderRadius:'0 0 7px 0', opacity:0.6 }} />
                    {/* End cap — launch dot */}
                    <div style={{ position:'absolute', right:-1, top:'50%', transform:'translateY(-50%)', width:8, height:8, borderRadius:'50%', background:c.color, border:'2px solid #07080f', boxShadow:`0 0 6px ${c.color}` }} />
                  </div>
                </React.Fragment>
              )
            } else {
              // Dot + compact card (point-in-time features)
              const cx   = dx*DAY_W + DAY_W/2
              const cardW = 200
              const left  = Math.max(2, Math.min(cx-cardW/2, TOTAL*DAY_W-cardW-2))
              return (
                <React.Fragment key={f.id}>
                  <div style={{ position:'absolute', left:cx-0.5, top:HDR_H, height:row*ROW_H+22, width:1, background:`linear-gradient(to bottom,transparent,${c.color}30)`, pointerEvents:'none', zIndex:2 }} />
                  <div draggable onDragStart={e=>{e.dataTransfer.effectAllowed='move';setDragId(f.id)}} onDragEnd={()=>{setDragId(null);setDragOverDay(null)}} style={{ position:'absolute', left:cx-6, top:cy+14, width:13, height:13, borderRadius:'50%', background:isDragging?'rgba(139,92,246,0.5)':c.color, border:'2px solid #07080f', boxShadow:`0 0 10px ${c.color}90`, zIndex:7, cursor:'grab' }} />
                  <div style={{ position:'absolute', left, top:cy+30, width:cardW, zIndex:6, opacity:isDragging?0.3:1 }}>
                    <FeatureCard feature={f} onEdit={onEdit} onDragStart={()=>setDragId(f.id)} onDragEnd={()=>{setDragId(null);setDragOverDay(null)}} isDragging={isDragging} compact />
                  </div>
                </React.Fragment>
              )
            }
          })}
        </div>
      </div>
    </div>
  )
}

/* ═══════════════════════════════════════════════════════════════
   MONTH VIEW
═══════════════════════════════════════════════════════════════ */
function MonthView({ features, onEdit, onUpdateDates }: { features:Feature[]; onEdit:(f:Feature)=>void; onUpdateDates:(id:number,date:string,startDate?:string)=>void }) {
  const [idx,          setIdx]          = useState(0)
  const [dragId,       setDragId]       = useState<number|null>(null)
  const [dragOverCell, setDragOverCell] = useState<number|null>(null)
  const { year, month, name } = MONTHS_LIST[idx]
  const mono = 'var(--font-dm-mono,DM Mono,monospace)'

  type CalEntry = { f: Feature; isStart: boolean }
  const featuresByDay = useMemo(() => {
    const map: Record<number, CalEntry[]> = {}
    features.forEach(f => {
      const d = parseDate(f.date)
      if (d.getFullYear()===year && d.getMonth()===month) {
        if (!map[d.getDate()]) map[d.getDate()]=[]
        map[d.getDate()].push({ f, isStart: false })
      }
      if (f.start_date) {
        const sd = parseDate(f.start_date)
        if (sd.getFullYear()===year && sd.getMonth()===month && sd.toDateString()!==d.toDateString()) {
          if (!map[sd.getDate()]) map[sd.getDate()]=[]
          map[sd.getDate()].push({ f, isStart: true })
        }
      }
    })
    return map
  }, [features,year,month])

  const weeks = useMemo(() => {
    const total=daysInMonth(year,month), first=firstDayOf(year,month)
    const cells=[...Array(first).fill(null)] as (number|null)[]
    for(let d=1;d<=total;d++) cells.push(d)
    while(cells.length%7!==0) cells.push(null)
    const w=[]; for(let i=0;i<cells.length;i+=7) w.push(cells.slice(i,i+7)); return w
  }, [year,month])

  const isToday = (d:number) => year===TODAY.getFullYear()&&month===TODAY.getMonth()&&d===TODAY.getDate()
  const monthFeatures = features.filter(f=>{const d=parseDate(f.date);return d.getFullYear()===year&&d.getMonth()===month})

  return (
    <div style={{ flex:1, overflow:'auto', padding:'18px 22px' }}>
      <div style={{ display:'flex', alignItems:'center', gap:14, marginBottom:18 }}>
        <button className="rm-btn" onClick={()=>setIdx(Math.max(0,idx-1))} disabled={idx===0} style={{ width:32, height:32, borderRadius:8, border:'1px solid rgba(255,255,255,0.1)', background:'transparent', color:idx===0?'rgba(255,255,255,0.18)':'rgba(255,255,255,0.7)', fontSize:18 }}>‹</button>
        <div style={{ fontFamily:'var(--font-syne,Syne,sans-serif)', fontWeight:800, fontSize:22, letterSpacing:'-0.5px' }}>{name}</div>
        <button className="rm-btn" onClick={()=>setIdx(Math.min(MONTHS_LIST.length-1,idx+1))} disabled={idx===MONTHS_LIST.length-1} style={{ width:32, height:32, borderRadius:8, border:'1px solid rgba(255,255,255,0.1)', background:'transparent', color:idx===MONTHS_LIST.length-1?'rgba(255,255,255,0.18)':'rgba(255,255,255,0.7)', fontSize:18 }}>›</button>
        <div style={{ marginLeft:'auto', fontFamily:mono, fontSize:10, color:'rgba(255,255,255,0.28)' }}>
          {Object.keys(featuresByDay).length} launch days · {monthFeatures.length} features
        </div>
      </div>
      {dragId!==null && <div style={{ marginBottom:10, padding:'6px 14px', background:'rgba(139,92,246,0.1)', border:'1px solid rgba(139,92,246,0.2)', borderRadius:8, fontFamily:mono, fontSize:10, color:'rgba(139,92,246,0.9)' }}>📅 Drop onto a date to reschedule</div>}
      <div style={{ background:'#0a0c16', borderRadius:14, border:'1px solid rgba(255,255,255,0.07)', overflow:'hidden' }}>
        <div style={{ display:'grid', gridTemplateColumns:'repeat(7,1fr)', borderBottom:'1px solid rgba(255,255,255,0.07)' }}>
          {['Sun','Mon','Tue','Wed','Thu','Fri','Sat'].map(d=>(
            <div key={d} style={{ padding:'10px 0', textAlign:'center', fontFamily:mono, fontSize:10, color:'rgba(255,255,255,0.28)', letterSpacing:'0.06em' }}>{d}</div>
          ))}
        </div>
        {weeks.map((week,wi)=>(
          <div key={wi} style={{ display:'grid', gridTemplateColumns:'repeat(7,1fr)', borderBottom:wi<weeks.length-1?'1px solid rgba(255,255,255,0.05)':'none' }}>
            {week.map((day,di)=>{
              const dayFeatures = day ? featuresByDay[day]||[] : []
              const today = !!day && isToday(day)
              const isDropTarget = dragId!==null && dragOverCell===day && day!==null
              return (
                <div key={di} className={`rm-cal-day${isDropTarget?' drop-target':''}`}
                  onDragOver={day?e=>{e.preventDefault();setDragOverCell(day)}:undefined}
                  onDragLeave={()=>setDragOverCell(null)}
                  onDrop={()=>{ if(dragId!==null&&day!==null){
                    const feat=features.find(f=>f.id===dragId)
                    const newDate=dateToStr(new Date(year,month,day))
                    if(feat?.start_date){
                      const delta=Math.round((new Date(year,month,day).getTime()-parseDate(feat.date).getTime())/86400000)
                      const newS=new Date(parseDate(feat.start_date).getTime()+delta*86400000)
                      onUpdateDates(dragId,newDate,dateToStr(newS))
                    } else { onUpdateDates(dragId,newDate) }
                    setDragId(null);setDragOverCell(null)
                  } }}
                  style={{ minHeight:90, padding:'8px 6px', borderRight:di<6?'1px solid rgba(255,255,255,0.05)':'none', background:!day?'rgba(0,0,0,0.18)':today?'rgba(244,63,94,0.07)':'transparent' }}
                >
                  {day && (
                    <>
                      {today ? <span style={{ display:'inline-flex', alignItems:'center', justifyContent:'center', width:24, height:24, background:'#f43f5e', borderRadius:'50%', fontFamily:mono, fontSize:11, fontWeight:700, marginBottom:5 }}>{day}</span>
                        : <div style={{ fontFamily:mono, fontSize:11, color:dayFeatures.length>0?'rgba(255,255,255,0.65)':'rgba(255,255,255,0.28)', marginBottom:5, fontWeight:dayFeatures.length>0?600:400 }}>{day}</div>}
                      <div style={{ display:'flex', flexDirection:'column', gap:3 }}>
                        {dayFeatures.slice(0,3).map(({f,isStart})=>{ const c=CAT[f.cat]??CAT['Core Gameplay']; return (
                          <div key={`${f.id}-${isStart?'s':'e'}`} className="rm-pill-drag" draggable={!isStart}
                            onDragStart={isStart?undefined:e=>{e.dataTransfer.effectAllowed='move';setDragId(f.id)}}
                            onDragEnd={()=>{setDragId(null);setDragOverCell(null)}}
                            onClick={()=>{ if(!dragId) onEdit(f) }}
                            style={{ padding:'2px 6px', borderRadius:4, background:dragId===f.id?'rgba(139,92,246,0.15)':c.dim, border:`1px solid ${dragId===f.id?'rgba(139,92,246,0.5)':c.border}`, borderStyle:isStart?'dashed':'solid', fontSize:9, fontWeight:700, color:dragId===f.id?'#8b5cf6':c.color, whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis', opacity:isStart?0.45:dragId===f.id?0.5:1 }}
                          >{isStart?'▶ ':''}{c.icon} {f.name}</div>
                        ) })}
                        {dayFeatures.length>3 && <div style={{ fontSize:9, fontFamily:mono, color:'rgba(255,255,255,0.28)', paddingLeft:3 }}>+{dayFeatures.length-3}</div>}
                      </div>
                    </>
                  )}
                </div>
              )
            })}
          </div>
        ))}
      </div>
      <div style={{ display:'flex', gap:12, marginTop:14, flexWrap:'wrap' }}>
        {Object.entries(CAT).map(([k,v])=>(
          <div key={k} style={{ display:'flex', alignItems:'center', gap:5 }}>
            <div style={{ width:9, height:9, borderRadius:2, background:v.color }} />
            <span style={{ fontFamily:mono, fontSize:9.5, color:'rgba(255,255,255,0.35)' }}>{k}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

/* ═══════════════════════════════════════════════════════════════
   LIST VIEW
═══════════════════════════════════════════════════════════════ */
function ListView({ features, onEdit, onUpdateDates }: { features:Feature[]; onEdit:(f:Feature)=>void; onUpdateDates:(id:number,date:string,startDate?:string)=>void }) {
  const [dragId,       setDragId]       = useState<number|null>(null)
  const [dragOverDate, setDragOverDate] = useState<string|null>(null)
  const mono = 'var(--font-dm-mono,DM Mono,monospace)'
  const syne = 'var(--font-syne,Syne,sans-serif)'

  const byWeek = useMemo(() => {
    const sorted = [...features].sort((a,b)=>parseDate(a.date).getTime()-parseDate(b.date).getTime())
    const dayMap: Record<string,Feature[]> = {}
    sorted.forEach(f=>{ if(!dayMap[f.date])dayMap[f.date]=[]; dayMap[f.date].push(f) })
    const weekMap: Record<string,{mon:Date;days:{date:string;feats:Feature[]}[]}> = {}
    Object.entries(dayMap).forEach(([date,feats])=>{
      const d=parseDate(date), dow=d.getDay()===0?7:d.getDay()
      const mon=new Date(d.getFullYear(),d.getMonth(),d.getDate()-(dow-1))
      const wk=dateToStr(mon)
      if(!weekMap[wk]) weekMap[wk]={mon,days:[]}
      weekMap[wk].days.push({date,feats})
    })
    return Object.entries(weekMap).sort(([a],[b])=>new Date(a).getTime()-new Date(b).getTime()).map(([k,v])=>({key:k,mon:v.mon,days:v.days.sort((a,b)=>new Date(a.date).getTime()-new Date(b.date).getTime())}))
  }, [features])

  return (
    <div style={{ flex:1, overflow:'auto', padding:'18px 22px' }}>
      {dragId!==null && <div style={{ maxWidth:680, margin:'0 auto 14px', padding:'6px 14px', background:'rgba(139,92,246,0.1)', border:'1px solid rgba(139,92,246,0.2)', borderRadius:8, fontFamily:mono, fontSize:10, color:'rgba(139,92,246,0.9)' }}>📅 Drop onto a date to reschedule</div>}
      <div style={{ maxWidth:680, margin:'0 auto', display:'flex', flexDirection:'column', gap:26 }}>
        {byWeek.map(week=>{
          const sunDate=new Date(week.mon); sunDate.setDate(sunDate.getDate()+6)
          const total=week.days.reduce((s,d)=>s+d.feats.length,0)
          return (
            <div key={week.key}>
              <div style={{ display:'flex', alignItems:'center', gap:10, marginBottom:14 }}>
                <div style={{ fontFamily:syne, fontWeight:800, fontSize:12, color:'rgba(255,255,255,0.82)' }}>{fmtShort(week.mon)} – {fmtShort(sunDate)}</div>
                <div style={{ flex:1, height:1, background:'rgba(255,255,255,0.07)' }} />
                <div style={{ fontFamily:mono, fontSize:9.5, color:'rgba(255,255,255,0.3)', padding:'2px 9px', borderRadius:20, background:'rgba(255,255,255,0.04)', border:'1px solid rgba(255,255,255,0.07)' }}>{total} {total===1?'launch':'launches'}</div>
              </div>
              <div style={{ display:'flex', flexDirection:'column', gap:10 }}>
                {week.days.map(({date,feats})=>{
                  const d=parseDate(date), today=d.toDateString()===TODAY.toDateString()
                  const isDropTarget = dragId!==null && dragOverDate===date
                  return (
                    <div key={date} style={{ display:'flex', gap:14, alignItems:'flex-start' }}>
                      <div onDragOver={e=>{e.preventDefault();setDragOverDate(date)}} onDragLeave={()=>setDragOverDate(null)} onDrop={()=>{ if(dragId!==null){
                        const feat=features.find(f=>f.id===dragId)
                        if(feat?.start_date){
                          const delta=Math.round((parseDate(date).getTime()-parseDate(feat.date).getTime())/86400000)
                          const newS=new Date(parseDate(feat.start_date).getTime()+delta*86400000)
                          onUpdateDates(dragId,date,dateToStr(newS))
                        } else { onUpdateDates(dragId,date) }
                        setDragId(null);setDragOverDate(null)
                      } }}
                        style={{ width:46, flexShrink:0, textAlign:'right', paddingTop:3, borderRadius:6, padding:'3px 5px 3px 0', background:isDropTarget?'rgba(139,92,246,0.15)':'transparent', outline:isDropTarget?'1px dashed rgba(139,92,246,0.5)':'none', cursor:dragId!==null?'copy':'default', transition:'background 0.12s' }}>
                        <div style={{ fontFamily:mono, fontSize:9, color:today?'#f43f5e':'rgba(255,255,255,0.35)' }}>{d.toLocaleString('en-US',{month:'short'})}</div>
                        <div style={{ fontFamily:syne, fontWeight:800, fontSize:20, letterSpacing:'-0.5px', color:today?'#f43f5e':isDropTarget?'#8b5cf6':'rgba(255,255,255,0.65)', lineHeight:1 }}>{d.getDate()}</div>
                        {today && <div style={{ fontFamily:mono, fontSize:7.5, color:'#f43f5e', letterSpacing:'0.1em', marginTop:2 }}>TODAY</div>}
                      </div>
                      <div style={{ width:1, alignSelf:'stretch', background:'rgba(255,255,255,0.08)', flexShrink:0, position:'relative' }}>
                        <div style={{ position:'absolute', top:10, left:'50%', transform:'translateX(-50%)', width:9, height:9, borderRadius:'50%', background:today?'#f43f5e':'rgba(255,255,255,0.14)', border:today?'2px solid rgba(244,63,94,0.3)':'2px solid rgba(255,255,255,0.06)' }} />
                      </div>
                      <div style={{ flex:1, display:'flex', flexDirection:'column', gap:7, paddingBottom:4 }}>
                        {feats.map(f=><FeatureCard key={f.id} feature={f} onEdit={onEdit} onDragStart={()=>setDragId(f.id)} onDragEnd={()=>{setDragId(null);setDragOverDate(null)}} isDragging={dragId===f.id} />)}
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          )
        })}
        {features.length===0 && <div style={{ textAlign:'center', padding:'48px 0', color:'rgba(255,255,255,0.25)', fontFamily:'var(--font-dm-mono,DM Mono,monospace)', fontSize:12 }}>No features match the current filters.</div>}
      </div>
    </div>
  )
}

/* ═══════════════════════════════════════════════════════════════
   MAIN APP
═══════════════════════════════════════════════════════════════ */
export default function RoadmapApp() {
  const [features, setFeatures] = useState<Feature[]>([])
  const [loading,  setLoading]  = useState(true)
  const [saving,   setSaving]   = useState(false)
  const [error,    setError]    = useState<string|null>(null)
  const [view,     setView]     = useState('timeline')
  const [filters,  setFilters]  = useState<string[]>([])
  const [modal,    setModal]    = useState<{feature: Feature|FeatureInput; isNew:boolean}|null>(null)
  const [saveErr,  setSaveErr]  = useState<string|null>(null)

  // Load features + real-time subscription
  useEffect(() => {
    loadFeatures()
    const channel = supabase
      .channel('roadmap-features')
      .on('postgres_changes', { event:'*', schema:'public', table:'features' }, () => loadFeatures())
      .subscribe()
    return () => { supabase.removeChannel(channel) }
  }, [])

  async function loadFeatures() {
    const { data, error } = await supabase.from('features').select('*').order('date')
    if (error) setError(error.message)
    else setFeatures((data ?? []).map(f => ({ ...f, start_date: f.start_date ?? '' })))
    setLoading(false)
  }

  const visible = useMemo(() =>
    filters.length===0 ? features : features.filter(f=>filters.includes(f.cat)),
    [features, filters]
  )

  async function handleSave(f: Feature|FeatureInput) {
    setSaving(true)
    setSaveErr(null)
    const normalized = { ...f, start_date: (f as Feature).start_date ?? '' }
    if (modal?.isNew) {
      const { error } = await supabase.from('features').insert(normalized as FeatureInput)
      if (error) { setSaving(false); setSaveErr(error.message); return }
    } else {
      const { id, ...updates } = normalized as Feature
      const { error } = await supabase.from('features').update(updates).eq('id', id)
      if (error) { setSaving(false); setSaveErr(error.message); return }
    }
    setSaving(false)
    setSaveErr(null)
    setModal(null)
  }

  async function handleDelete(id: number) {
    if (!window.confirm('Delete this feature?')) return
    setSaving(true)
    const { error } = await supabase.from('features').delete().eq('id', id)
    if (error) setError(error.message)
    setSaving(false)
    setModal(null)
  }

  async function updateDates(id: number, date: string, startDate?: string) {
    setFeatures(p => p.map(f => f.id===id ? {...f, date, ...(startDate!==undefined ? {start_date:startDate} : {})} : f))
    const payload: Record<string,string> = { date }
    if (startDate !== undefined) payload.start_date = startDate
    const { error } = await supabase.from('features').update(payload).eq('id', id)
    if (error) { setError(error.message); loadFeatures() }
  }

  if (loading) return (
    <div className="rm-root" style={{ alignItems:'center', justifyContent:'center' }}>
      <div style={{ fontFamily:'var(--font-dm-mono,DM Mono,monospace)', fontSize:12, color:'rgba(255,255,255,0.35)' }}>Loading roadmap…</div>
    </div>
  )

  if (error) return (
    <div className="rm-root" style={{ alignItems:'center', justifyContent:'center', flexDirection:'column', gap:12 }}>
      <div style={{ fontFamily:'var(--font-dm-mono,DM Mono,monospace)', fontSize:12, color:'#f43f5e' }}>Error: {error}</div>
      <button className="rm-btn" onClick={()=>{setError(null);loadFeatures()}} style={{ padding:'6px 14px', borderRadius:8, border:'1px solid rgba(255,255,255,0.1)', background:'transparent', color:'rgba(255,255,255,0.6)', fontSize:12 }}>Retry</button>
    </div>
  )

  return (
    <div className="rm-root">
      <Sidebar features={features} />
      <div style={{ flex:1, display:'flex', flexDirection:'column', overflow:'hidden' }}>
        <Header view={view} setView={setView} filters={filters} setFilters={setFilters} count={visible.length} saving={saving} onAdd={()=>setModal({feature:{...EMPTY},isNew:true})} />
        <div style={{ flex:1, overflow:'hidden', display:'flex', flexDirection:'column' }}>
          {view==='timeline' && <TimelineView key="tl" features={visible} onEdit={f=>setModal({feature:f,isNew:false})} onUpdateDates={updateDates} />}
          {view==='month'    && <MonthView    key="mo" features={visible} onEdit={f=>setModal({feature:f,isNew:false})} onUpdateDates={updateDates} />}
          {view==='list'     && <ListView     key="li" features={visible} onEdit={f=>setModal({feature:f,isNew:false})} onUpdateDates={updateDates} />}
        </div>
      </div>
      {modal && <FeatureModal feature={modal.feature} isNew={modal.isNew} saving={saving} saveErr={saveErr} onClose={()=>{setModal(null);setSaveErr(null)}} onSave={handleSave} onDelete={handleDelete} />}
    </div>
  )
}

import type { Metadata } from 'next'
import { Syne, DM_Mono } from 'next/font/google'
import './roadmap.css'

const syne   = Syne  ({ subsets:['latin'], variable:'--font-syne',  weight:['400','600','700','800'] })
const dmMono = DM_Mono({ subsets:['latin'], variable:'--font-dm-mono', weight:['300','400','500'] })

export const metadata: Metadata = {
  title:       'Boinkers — Product Roadmap',
  description: 'Internal product roadmap for Boinkers mobile game',
}

export default function RoadmapLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className={`${syne.variable} ${dmMono.variable}`} style={{ height:'100vh', overflow:'hidden' }}>
      {children}
    </div>
  )
}

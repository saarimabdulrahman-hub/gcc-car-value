import React from 'react';
import { Search, Bell, Moon, ChevronDown, Zap, Filter, MapPin } from 'lucide-react';

export default function BrowsePage() {
  return (
    <div className="min-h-screen bg-[var(--bg-primary)] text-[var(--text-primary)] font-sans">
      {/* Header - Aligned to Design System */}
      <header className="header">
        <div className="header-brand">
          <div className="logo-icon">CV</div>
          <div className="header-titles">
            <h1>CAR VALUATOR</h1>
            <div className="header-subtitle">GCC MARKET INTELLIGENCE</div>
          </div>
        </div>
        <div className="header-actions">
          <button className="header-btn"><Search size={18} /></button>
          <button className="header-btn"><Bell size={18} /></button>
          <button className="header-btn"><Moon size={18} /></button>
          <button className="lang-btn">
            <span className="lang-option active">EN</span>
            <span className="lang-divider">/</span>
            <span className="lang-option">AR</span>
          </button>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="p-[var(--space-5)]">
        {/* Hero Section */}
        <section className="relative rounded-[var(--radius-xl)] overflow-hidden mb-[var(--space-5)] bg-[#11131C] min-h-[400px]">
          {/* Background Map Overlay */}
          <div className="absolute inset-0 bg-[url('/img/map-overlay.png')] bg-cover bg-right-top opacity-30 pointer-events-none" />

          {/* Content */}
          <div className="relative p-[var(--space-6)] flex flex-col h-full">
            <div className="text-[var(--text-caption)] font-medium text-[var(--text-secondary)] mb-2">
              Home {'>'} Browse Models
            </div>
            <h1 className="text-[var(--text-display)] font-extrabold mb-2">Browse Models</h1>
            <p className="text-[var(--text-lead)] text-[var(--text-secondary)] max-w-xl">
              Explore every make and model across 12 manufacturers in 6 GCC countries.
            </p>
          </div>

          {/* Cars Overlay (Positioned below/around KPI cards) */}
          <div className="absolute bottom-0 left-0 right-0 h-[250px] bg-[url('/img/hero-cars.png')] bg-bottom bg-no-repeat" />
        </section>

        {/* KPI Cards */}
        <section className="grid grid-cols-5 gap-[var(--space-2)] mb-[var(--space-5)]">
          {[
            { label: 'MANUFACTURERS', value: '12', sub: 'Active brands' },
            { label: 'TOTAL MODELS', value: '57', sub: 'Across all brands' },
            { label: 'ACTIVE LISTINGS', value: '0.0M+', sub: 'Live in market' },
            { label: 'COUNTRIES', value: '6', sub: 'GCC countries' },
            { label: 'DATA FRESHNESS', value: '2 min ago', sub: 'Real-time updates' },
          ].map((kpi, i) => (
            <div key={i} className="bg-[var(--bg-card)] p-[var(--space-3)] rounded-[var(--radius-lg)] border border-[var(--border-default)]">
              <div className="text-[var(--text-xs)] text-[var(--text-secondary)] font-bold mb-1">{kpi.label}</div>
              <div className="text-[var(--text-stat)] font-bold">{kpi.value}</div>
              <div className="text-[var(--text-sm)] text-[var(--text-muted)]">{kpi.sub}</div>
            </div>
          ))}
        </section>

        {/* Search & Filters */}
        <section className="flex gap-[var(--space-2)] mb-[var(--space-5)]">
          <div className="flex-1 relative">
            <input
              type="text"
              placeholder="Search manufacturers, models, or keyword..."
              className="w-full bg-[var(--bg-input)] border border-[var(--border-default)] p-[var(--space-2)] rounded-[var(--radius-md)] text-[var(--text-input)] pl-[var(--space-5)]"
            />
            <Search className="absolute left-[var(--space-2)] top-1/2 -translate-y-1/2 text-[var(--text-muted)]" size={16} />
          </div>
          <button className="flex items-center gap-2 px-[var(--space-3)] border border-[var(--gold)]/30 rounded-[var(--radius-md)] text-[var(--gold)] hover:bg-[var(--gold)]/10">
            <Filter size={16} /> Advanced Filters
          </button>
        </section>
      </main>
    </div>
  );
}

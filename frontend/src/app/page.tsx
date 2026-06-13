"use client";

import React, { useState } from "react";
import { 
  Wand2, 
  Cpu, 
  Layers, 
  FileText, 
  Video, 
  Code, 
  CheckCircle2, 
  Sparkles, 
  Play, 
  Activity 
} from "lucide-react";

export default function Home() {
  const [prompt, setPrompt] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);

  const handleGenerate = (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;
    setIsGenerating(true);
    setTimeout(() => {
      setIsGenerating(false);
      alert("Prototype request queued! Backend will pick up the job and generate assets shortly.");
    }, 1500);
  };

  return (
    <div className="flex flex-col min-h-screen bg-slate-950 text-slate-100 selection:bg-blue-600 selection:text-white overflow-x-hidden">
      {/* Header */}
      <header className="sticky top-0 z-50 backdrop-blur-md bg-slate-950/80 border-b border-slate-800">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="h-9 w-9 bg-gradient-to-tr from-blue-600 to-indigo-500 rounded-lg flex items-center justify-center shadow-lg shadow-blue-500/20">
              <Wand2 className="h-5 w-5 text-white" />
            </div>
            <span className="font-bold text-xl tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-300 bg-clip-text text-transparent">
              ProtoForge <span className="text-blue-500">AI</span>
            </span>
          </div>
          <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-400">
            <a href="#features" className="hover:text-white transition-colors">Features</a>
            <a href="#demo" className="hover:text-white transition-colors">Interactive Demo</a>
            <a href="#pricing" className="hover:text-white transition-colors">Pricing</a>
          </nav>
          <div className="flex items-center gap-4">
            <button className="text-sm font-medium text-slate-300 hover:text-white transition-colors">
              Sign In
            </button>
            <button className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-sm font-medium rounded-lg text-white shadow-lg shadow-blue-600/20 hover:shadow-blue-600/30 transition-all">
              Get Started Free
            </button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative pt-20 pb-24 md:pt-32 md:pb-36 bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 overflow-hidden">
        {/* Glow Effects */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-blue-600/10 rounded-full blur-[120px] pointer-events-none"></div>
        <div className="absolute top-1/3 left-1/3 w-[300px] h-[300px] bg-indigo-500/10 rounded-full blur-[100px] pointer-events-none"></div>

        <div className="container mx-auto px-4 max-w-6xl relative z-10 text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-blue-500/30 bg-blue-500/5 text-xs text-blue-400 mb-6 animate-pulse">
            <Sparkles className="h-3.5 w-3.5" />
            <span>Next-Gen Generative 3D CAD is Live</span>
          </div>

          <h1 className="text-4xl md:text-6xl lg:text-7xl font-extrabold tracking-tight mb-6 bg-gradient-to-b from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
            Turn Any Idea Into a Complete <br className="hidden md:inline" />
            <span className="bg-gradient-to-r from-blue-500 via-indigo-400 to-cyan-400 bg-clip-text text-transparent">3D Prototype</span> in Minutes
          </h1>

          <p className="text-lg md:text-xl text-slate-400 max-w-3xl mx-auto mb-10 leading-relaxed">
            From a single text prompt, sketch, or drawing, get production-ready ISO CAD models (STEP/STL/GLTF), photorealistic 4K renders, FEA stress simulations, animations, and an instantly shareable WebXR viewer.
          </p>

          {/* Quick Sandbox Generator */}
          <div className="max-w-2xl mx-auto mb-16 p-2 rounded-xl bg-slate-900/90 border border-slate-800 shadow-2xl focus-within:border-blue-500/50 focus-within:ring-2 focus-within:ring-blue-500/10 transition-all">
            <form onSubmit={handleGenerate} className="flex flex-col sm:flex-row gap-2">
              <input
                type="text"
                placeholder="Describe what you want to prototype (e.g. 'Ergonomic gaming mouse with honeycomb design and USB-C port')..."
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                className="flex-1 bg-transparent border-0 px-4 py-3 text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-0 text-sm"
              />
              <button
                type="submit"
                disabled={isGenerating}
                className="px-6 py-3 bg-blue-600 hover:bg-blue-500 disabled:bg-blue-800 text-sm font-semibold rounded-lg text-white flex items-center justify-center gap-2 transition-colors shrink-0"
              >
                {isGenerating ? (
                  <>
                    <div className="h-4 w-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                    Generating...
                  </>
                ) : (
                  <>
                    <Wand2 className="h-4 w-4" />
                    Forge Prototype
                  </>
                )}
              </button>
            </form>
          </div>

          {/* Pipeline Deliverables Strip */}
          <div className="grid grid-cols-2 md:grid-cols-6 gap-4 max-w-5xl mx-auto border-t border-slate-900 pt-12 text-slate-400">
            <div className="flex flex-col items-center p-3 rounded-lg hover:bg-slate-900/50 transition-all border border-transparent hover:border-slate-800">
              <Code className="h-6 w-6 text-blue-500 mb-2" />
              <span className="font-semibold text-white text-sm">3D CAD Files</span>
              <span className="text-xs text-slate-500 mt-1">STEP / STL / OBJ</span>
            </div>
            <div className="flex flex-col items-center p-3 rounded-lg hover:bg-slate-900/50 transition-all border border-transparent hover:border-slate-800">
              <Layers className="h-6 w-6 text-indigo-500 mb-2" />
              <span className="font-semibold text-white text-sm">ISO Drawings</span>
              <span className="text-xs text-slate-500 mt-1">Ready for CNC/Mfg</span>
            </div>
            <div className="flex flex-col items-center p-3 rounded-lg hover:bg-slate-900/50 transition-all border border-transparent hover:border-slate-800">
              <Sparkles className="h-6 w-6 text-cyan-500 mb-2" />
              <span className="font-semibold text-white text-sm">4K Renders</span>
              <span className="text-xs text-slate-500 mt-1">Photorealistic</span>
            </div>
            <div className="flex flex-col items-center p-3 rounded-lg hover:bg-slate-900/50 transition-all border border-transparent hover:border-slate-800">
              <Video className="h-6 w-6 text-purple-500 mb-2" />
              <span className="font-semibold text-white text-sm">Animations</span>
              <span className="text-xs text-slate-500 mt-1">360° Exploded Views</span>
            </div>
            <div className="flex flex-col items-center p-3 rounded-lg hover:bg-slate-900/50 transition-all border border-transparent hover:border-slate-800">
              <Activity className="h-6 w-6 text-emerald-500 mb-2" />
              <span className="font-semibold text-white text-sm">FEA Simulation</span>
              <span className="text-xs text-slate-500 mt-1">Stress & Thermal</span>
            </div>
            <div className="flex flex-col items-center p-3 rounded-lg hover:bg-slate-900/50 transition-all border border-transparent hover:border-slate-800">
              <FileText className="h-6 w-6 text-amber-500 mb-2" />
              <span className="font-semibold text-white text-sm">Instant BOM</span>
              <span className="text-xs text-slate-500 mt-1">Cost & Parts Est.</span>
            </div>
          </div>
        </div>
      </section>

      {/* Live Interactive Demo Preview Area */}
      <section id="demo" className="py-20 bg-slate-900 border-y border-slate-850 relative">
        <div className="container mx-auto px-4 max-w-6xl">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Interactive 3D Viewer Playground</h2>
            <p className="text-slate-400 max-w-2xl mx-auto">
              Rotate, zoom, and explode actual generated models. Toggle between texture, wireframe, and engineering drawing modes instantly.
            </p>
          </div>

          <div className="aspect-video w-full rounded-2xl bg-slate-950 border border-slate-800 shadow-inner flex flex-col items-center justify-center relative overflow-hidden group">
            {/* Grid background representing 3D CAD canvas */}
            <div className="absolute inset-0 bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:24px_24px] opacity-40"></div>
            
            <div className="z-10 text-center p-6">
              <div className="mx-auto w-16 h-16 rounded-full bg-blue-500/10 border border-blue-500/30 flex items-center justify-center mb-4 group-hover:scale-105 transition-transform duration-300">
                <Play className="h-6 w-6 text-blue-500 fill-blue-500" />
              </div>
              <h3 className="font-bold text-lg mb-2">Interactive 3D WebGL Canvas</h3>
              <p className="text-sm text-slate-500 max-w-md mx-auto mb-6">
                Ready for BabylonJS or Three.js loading of actual STEP/GLTF models. This core system exposes complete interaction with real mechanical constraints.
              </p>
              <div className="inline-flex gap-3">
                <button className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-xs font-semibold text-white shadow-md transition-colors">
                  Load Sample Model
                </button>
                <button className="px-4 py-2 rounded-lg bg-slate-850 hover:bg-slate-800 text-xs font-semibold text-slate-300 border border-slate-750 transition-colors">
                  View Source Schema
                </button>
              </div>
            </div>

            {/* Bottom Floating controls overlay */}
            <div className="absolute bottom-4 left-4 right-4 flex items-center justify-between p-3 rounded-lg bg-slate-900/90 border border-slate-800 backdrop-blur-md text-xs text-slate-400 z-10">
              <div className="flex gap-4">
                <span>Model: <strong>drone_housing_v3.gltf</strong></span>
                <span>Vertices: <strong>42,810</strong></span>
              </div>
              <div className="flex gap-2">
                <span className="px-2 py-0.5 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded">Ready</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Breakdown */}
      <section id="features" className="py-24 bg-slate-950">
        <div className="container mx-auto px-4 max-w-6xl">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold mb-4">Enterprise-Grade Generation Pipeline</h2>
            <p className="text-slate-400 max-w-2xl mx-auto">
              Our backend self-improves nightly by learning from engineers' direct corrections. Every model goes through an automated verification suite to guarantee ISO compliance.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="p-6 rounded-xl bg-slate-900/50 border border-slate-850 hover:border-blue-500/30 transition-all group">
              <div className="h-10 w-10 rounded-lg bg-blue-600/10 flex items-center justify-center text-blue-500 mb-6 group-hover:bg-blue-600 group-hover:text-white transition-colors duration-300">
                <Cpu className="h-5 w-5" />
              </div>
              <h3 className="text-xl font-bold mb-3 text-white">Parametric Engineering Engine</h3>
              <p className="text-slate-400 text-sm leading-relaxed">
                Generates fully parametric CAD models, preserving logical hierarchies, hole positions, and joint constraints. Export in industry-standard formats including STEP, STL, and OBJ.
              </p>
            </div>

            <div className="p-6 rounded-xl bg-slate-900/50 border border-slate-850 hover:border-indigo-500/30 transition-all group">
              <div className="h-10 w-10 rounded-lg bg-indigo-600/10 flex items-center justify-center text-indigo-500 mb-6 group-hover:bg-indigo-600 group-hover:text-white transition-colors duration-300">
                <Activity className="h-5 w-5" />
              </div>
              <h3 className="text-xl font-bold mb-3 text-white">Auto-Run FEA Simulations</h3>
              <p className="text-slate-400 text-sm leading-relaxed">
                Our pipeline meshes models and executes structural finite element analysis under standard load cases. Identify weaknesses and fatigue limits automatically before printing.
              </p>
            </div>

            <div className="p-6 rounded-xl bg-slate-900/50 border border-slate-850 hover:border-cyan-500/30 transition-all group">
              <div className="h-10 w-10 rounded-lg bg-cyan-600/10 flex items-center justify-center text-cyan-500 mb-6 group-hover:bg-cyan-600 group-hover:text-white transition-colors duration-300">
                <Layers className="h-5 w-5" />
              </div>
              <h3 className="text-xl font-bold mb-3 text-white">ISO Engineering Drawings</h3>
              <p className="text-slate-400 text-sm leading-relaxed">
                Generates complete 2D projection blueprints in full compliance with ISO 128 standards, including dimensioning, tolerance callouts, sectional views, and detailed annotations.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Tiers (Aligned with Business Plan) */}
      <section id="pricing" className="py-24 bg-slate-900 border-t border-slate-850">
        <div className="container mx-auto px-4 max-w-6xl">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold mb-4">Transparent, Scale-Ready Pricing</h2>
            <p className="text-slate-400 max-w-2xl mx-auto">
              Get started for free or unlock high-performance FEA simulation, photorealistic 4K renders, and enterprise-grade SLA.
            </p>
          </div>

          <div className="grid md:grid-cols-4 gap-6">
            {/* Free Tier */}
            <div className="p-6 rounded-xl bg-slate-950 border border-slate-800 flex flex-col justify-between">
              <div>
                <h3 className="font-bold text-lg text-slate-300">Free</h3>
                <div className="mt-4 mb-6">
                  <span className="text-3xl font-extrabold text-white">$0</span>
                </div>
                <p className="text-xs text-slate-500 mb-6">Perfect for testing the engine or students learning product design.</p>
                <ul className="space-y-3 text-xs text-slate-400 border-t border-slate-850 pt-6">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-3.5 w-3.5 text-blue-500 shrink-0" />
                    <span>1 project / month</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-3.5 w-3.5 text-blue-500 shrink-0" />
                    <span>Public sharing only</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-3.5 w-3.5 text-blue-500 shrink-0" />
                    <span>480p render limit</span>
                  </li>
                </ul>
              </div>
              <button className="mt-8 w-full py-2 rounded-lg bg-slate-850 hover:bg-slate-800 text-xs font-semibold text-slate-300 transition-colors">
                Choose Free
              </button>
            </div>

            {/* Starter Tier */}
            <div className="p-6 rounded-xl bg-slate-950 border border-slate-850 flex flex-col justify-between relative">
              <div>
                <h3 className="font-bold text-lg text-slate-300">Starter</h3>
                <div className="mt-4 mb-6">
                  <span className="text-3xl font-extrabold text-white">$29</span>
                  <span className="text-xs text-slate-500"> / mo</span>
                </div>
                <p className="text-xs text-slate-500 mb-6">For freelancers and industrial designers iterating fast on consumer products.</p>
                <ul className="space-y-3 text-xs text-slate-400 border-t border-slate-850 pt-6">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-3.5 w-3.5 text-blue-500 shrink-0" />
                    <span>10 projects / month</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-3.5 w-3.5 text-blue-500 shrink-0" />
                    <span>Full export suite</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-3.5 w-3.5 text-blue-500 shrink-0" />
                    <span>4K renders</span>
                  </li>
                </ul>
              </div>
              <button className="mt-8 w-full py-2 rounded-lg bg-slate-850 hover:bg-slate-800 text-xs font-semibold text-slate-300 transition-colors">
                Choose Starter
              </button>
            </div>

            {/* Pro Tier */}
            <div className="p-6 rounded-xl bg-slate-950 border-2 border-blue-500 flex flex-col justify-between relative">
              <div className="absolute top-0 right-6 -translate-y-1/2 px-2.5 py-0.5 rounded-full bg-blue-600 text-[10px] font-bold text-white uppercase tracking-wider shadow-md">
                Popular
              </div>
              <div>
                <h3 className="font-bold text-lg text-white">Professional</h3>
                <div className="mt-4 mb-6">
                  <span className="text-3xl font-extrabold text-white">$99</span>
                  <span className="text-xs text-slate-500"> / mo</span>
                </div>
                <p className="text-xs text-slate-500 mb-6">For design firms and engineering teams needing precise stress validation.</p>
                <ul className="space-y-3 text-xs text-slate-300 border-t border-slate-850 pt-6">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-3.5 w-3.5 text-blue-500 shrink-0" />
                    <span>50 projects / month</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-3.5 w-3.5 text-blue-500 shrink-0" />
                    <span>FEA Stress Simulation</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-3.5 w-3.5 text-blue-500 shrink-0" />
                    <span>Priority Queue</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-3.5 w-3.5 text-blue-500 shrink-0" />
                    <span>Team Sharing & Collab</span>
                  </li>
                </ul>
              </div>
              <button className="mt-8 w-full py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-xs font-semibold text-white shadow-lg shadow-blue-600/15 transition-colors">
                Choose Professional
              </button>
            </div>

            {/* Enterprise Tier */}
            <div className="p-6 rounded-xl bg-slate-950 border border-slate-800 flex flex-col justify-between">
              <div>
                <h3 className="font-bold text-lg text-slate-300">Enterprise</h3>
                <div className="mt-4 mb-6">
                  <span className="text-3xl font-extrabold text-white">$299</span>
                  <span className="text-xs text-slate-500"> / mo</span>
                </div>
                <p className="text-xs text-slate-500 mb-6">For global manufacturing and R&D divisions requiring absolute scale.</p>
                <ul className="space-y-3 text-xs text-slate-400 border-t border-slate-850 pt-6">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-3.5 w-3.5 text-blue-500 shrink-0" />
                    <span>Unlimited projects</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-3.5 w-3.5 text-blue-500 shrink-0" />
                    <span>Private cloud deployment</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-3.5 w-3.5 text-blue-500 shrink-0" />
                    <span>SSO & custom security</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-3.5 w-3.5 text-blue-500 shrink-0" />
                    <span>Custom engine training</span>
                  </li>
                </ul>
              </div>
              <button className="mt-8 w-full py-2 rounded-lg bg-slate-850 hover:bg-slate-800 text-xs font-semibold text-slate-300 transition-colors">
                Contact Sales
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-850 bg-slate-950 py-12 text-sm text-slate-500">
        <div className="container mx-auto px-4 max-w-6xl flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-2">
            <div className="h-6 w-6 bg-blue-600 rounded flex items-center justify-center text-white font-bold text-xs">PF</div>
            <span className="font-bold text-slate-300">ProtoForge AI, Inc.</span>
          </div>
          <div className="flex gap-8 text-xs">
            <a href="#" className="hover:text-slate-300 transition-colors">Privacy Policy</a>
            <a href="#" className="hover:text-slate-300 transition-colors">Terms of Service</a>
            <a href="#" className="hover:text-slate-300 transition-colors">ISO 9001 compliance</a>
          </div>
          <div className="text-xs text-slate-600">
            &copy; {new Date().getFullYear()} ProtoForge AI. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
}

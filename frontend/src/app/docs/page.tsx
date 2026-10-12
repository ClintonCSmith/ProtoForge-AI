'use client'

import React from 'react'
import { 
  Book, 
  Code, 
  Terminal, 
  Cpu, 
  Globe, 
  Search,
  Copy,
  ExternalLink,
  ChevronRight,
  Hash
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

const SECTIONS = [
  { id: 'start', title: 'Getting Started', items: ['Introduction', 'Core Concepts', 'Authentication'] },
  { id: 'api', title: 'API Reference', items: ['Generate Prototype', 'Job Status', 'Asset Downloads'] },
  { id: 'webhooks', title: 'Webhooks', items: ['Webhook Basics', 'Event Types', 'Security'] },
  { id: 'sdks', title: 'SDK Examples', items: ['JavaScript / Node.js', 'Python', 'cURL'] },
]

const CODE_EXAMPLES = {
  curl: `curl -X POST https://api.protoforge.ai/v1/generate \\
  -H "Authorization: Bearer protoforge_sk_••••" \\
  -H "Content-Type: application/json" \\
  -d '{
    "name": "Bicycle Bracket",
    "input": { "text": "Ergonomic aero handlebar bracket" },
    "settings": { "quality": "Production" }
  }'`,
  python: `import protoforge

client = protoforge.Client(api_key="your_key")
job = client.projects.generate(
    name="Bicycle Bracket",
    text_input="Ergonomic aero handlebar bracket",
    quality="production"
)

print(f"Forging job started: {job.id}")`,
  js: `const { ProtoForge } = require('@protoforge/sdk');

const forge = new ProtoForge('your_key');
const project = await forge.generate({
  name: 'Bicycle Bracket',
  input: { text: 'Ergonomic aero handlebar bracket' },
  standard: 'ISO'
});`
}

export default function DocsPage() {
  return (
    <div className="flex min-h-[calc(100vh-64px)] bg-white dark:bg-slate-950">
      {/* Documentation Sidebar */}
      <aside className="w-72 border-r border-slate-200 dark:border-slate-800 flex flex-col h-full sticky top-16 hidden lg:flex">
        <div className="p-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3 w-3 text-slate-400" />
            <Input 
              placeholder="Search docs..." 
              className="pl-8 h-9 text-xs bg-slate-50 dark:bg-slate-900 border-none rounded-lg"
            />
          </div>
        </div>
        <ScrollArea className="flex-1 px-4 pb-8">
          <div className="space-y-8">
            {SECTIONS.map((section) => (
              <div key={section.id} className="space-y-3">
                <h4 className="text-[10px] font-bold uppercase tracking-widest text-slate-400 px-2">{section.title}</h4>
                <div className="space-y-1">
                  {section.items.map((item) => (
                    <button
                      key={item}
                      className="w-full text-left px-2 py-1.5 rounded-lg text-sm font-medium hover:bg-slate-100 dark:hover:bg-slate-900 text-slate-600 dark:text-slate-400 transition-colors"
                    >
                      {item}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>
      </aside>

      {/* Documentation Content */}
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto p-12 space-y-16 animate-in fade-in slide-in-from-bottom-4 duration-700">
          
          {/* Header */}
          <section className="space-y-4">
            <Badge variant="outline" className="text-blue-600 bg-blue-50 border-blue-100 font-bold px-3">DEVELOPER HUB</Badge>
            <h1 className="text-4xl font-bold tracking-tight">API Reference</h1>
            <p className="text-xl text-muted-foreground leading-relaxed">
              Automate your hardware design workflow. ProtoForge AI provides a RESTful API to programmatically generate 3D models, simulations, and manufacturing documentation.
            </p>
          </section>

          {/* Authentication Section */}
          <section className="space-y-6 pt-8 border-t">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-xl bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center text-blue-600">
                <Hash className="h-5 w-5" />
              </div>
              <h2 className="text-2xl font-bold">Authentication</h2>
            </div>
            <p className="text-slate-600 dark:text-slate-400">
              The ProtoForge API uses Bearer authentication with an API Key. You can manage your keys in the <Link href="/settings" className="text-blue-600 hover:underline">Settings</Link> page.
            </p>
            <div className="bg-slate-950 rounded-xl p-4 border border-slate-800">
              <code className="text-sm text-slate-300">Authorization: Bearer YOUR_API_KEY</code>
            </div>
          </section>

          {/* Core Endpoint Section */}
          <section className="space-y-8 pt-8 border-t">
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Badge className="bg-green-600 text-white font-mono uppercase">POST</Badge>
                <code className="text-lg font-bold">/v1/generate</code>
              </div>
              <p className="text-slate-600 dark:text-slate-400">
                Starts the AI forging pipeline to create a new prototype. This is an asynchronous operation.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="space-y-4">
                <h4 className="text-xs font-bold uppercase tracking-widest text-slate-500">Payload Parameters</h4>
                <div className="space-y-4">
                  <div className="border-l-2 border-slate-100 pl-4 py-1">
                    <p className="text-sm font-bold font-mono">name <span className="text-red-500 text-[10px]">required</span></p>
                    <p className="text-xs text-muted-foreground">The project name.</p>
                  </div>
                  <div className="border-l-2 border-slate-100 pl-4 py-1">
                    <p className="text-sm font-bold font-mono">input.text <span className="text-slate-400 text-[10px] font-normal italic">string</span></p>
                    <p className="text-xs text-muted-foreground">Natural language description of the object.</p>
                  </div>
                  <div className="border-l-2 border-slate-100 pl-4 py-1">
                    <p className="text-sm font-bold font-mono">settings.quality <span className="text-slate-400 text-[10px] font-normal italic">string</span></p>
                    <p className="text-xs text-muted-foreground">Either "Preview" or "Production".</p>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <Tabs defaultValue="curl" className="w-full">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="text-xs font-bold uppercase tracking-widest text-slate-500">Request Body</h4>
                    <TabsList className="h-7 bg-slate-100 dark:bg-slate-900 border-none p-1">
                      <TabsTrigger value="curl" className="text-[10px] px-2 h-5">cURL</TabsTrigger>
                      <TabsTrigger value="python" className="text-[10px] px-2 h-5">Python</TabsTrigger>
                      <TabsTrigger value="js" className="text-[10px] px-2 h-5">Node.js</TabsTrigger>
                    </TabsList>
                  </div>
                  <TabsContent value="curl" className="mt-0">
                    <pre className="p-4 bg-slate-950 text-slate-300 rounded-xl text-[11px] font-mono leading-relaxed overflow-x-auto relative group">
                      {CODE_EXAMPLES.curl}
                      <Button size="icon" variant="ghost" className="absolute top-2 right-2 h-8 w-8 text-slate-500 opacity-0 group-hover:opacity-100 transition-opacity">
                        <Copy className="h-4 w-4" />
                      </Button>
                    </pre>
                  </TabsContent>
                  <TabsContent value="python" className="mt-0">
                    <pre className="p-4 bg-slate-950 text-slate-300 rounded-xl text-[11px] font-mono leading-relaxed overflow-x-auto">
                      {CODE_EXAMPLES.python}
                    </pre>
                  </TabsContent>
                  <TabsContent value="js" className="mt-0">
                    <pre className="p-4 bg-slate-950 text-slate-300 rounded-xl text-[11px] font-mono leading-relaxed overflow-x-auto">
                      {CODE_EXAMPLES.js}
                    </pre>
                  </TabsContent>
                </Tabs>
              </div>
            </div>
          </section>

          {/* Success Widget */}
          <div className="bg-slate-50 dark:bg-slate-900 border-2 border-slate-200 dark:border-slate-800 rounded-2xl p-8 flex flex-col md:flex-row items-center gap-8 justify-between">
            <div className="space-y-2">
              <h3 className="text-xl font-bold">API Access included</h3>
              <p className="text-sm text-slate-600 dark:text-slate-400">
                All ProtoForge AI plans include API access with varying rate limits.
              </p>
            </div>
            <Button className="bg-blue-600 hover:bg-blue-500 rounded-xl gap-2 h-12 font-bold px-8">
              Explore Full Reference
              <ExternalLink className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </main>
    </div>
  )
}

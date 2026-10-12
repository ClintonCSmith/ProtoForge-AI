import { InputWizard } from '@/components/input-wizard'
import { ChevronLeft } from 'lucide-react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'

export default function NewProjectPage() {
  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 pb-20">
      {/* Header */}
      <header className="bg-white dark:bg-slate-950 border-b border-slate-200 dark:border-slate-800 h-16 mb-12">
        <div className="max-w-7xl mx-auto px-6 h-full flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/dashboard">
              <Button variant="ghost" size="icon" className="h-8 w-8">
                <ChevronLeft className="h-4 w-4" />
              </Button>
            </Link>
            <h1 className="text-sm font-bold uppercase tracking-widest text-slate-500">New Prototype</h1>
          </div>
          <div className="flex items-center gap-4 text-xs font-medium text-slate-400">
            <span>Step 1 of 2</span>
          </div>
        </div>
      </header>

      <main className="px-6">
        <InputWizard />
      </main>
    </div>
  )
}

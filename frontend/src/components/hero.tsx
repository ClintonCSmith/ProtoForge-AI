'use client'

import { motion } from 'framer-motion'
import { Button } from '@/components/ui/button'
import Link from 'next/link'
import { ArrowRight, Sparkles } from 'lucide-react'

export default function Hero() {
  return (
    <section className="relative flex min-h-[calc(100vh-4rem)] items-center justify-center overflow-hidden py-20">
      {/* Background decoration */}
      <div className="absolute inset-0 -z-10 bg-[radial-gradient(45%_45%_at_50%_50%,rgba(59,130,246,0.1)_0%,rgba(255,255,255,0)_100%)]" />
      
      <div className="container px-4 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="mb-6 inline-flex items-center rounded-full border bg-muted/50 px-3 py-1 text-sm font-medium">
            <Sparkles className="mr-2 h-4 w-4 text-primary" />
            <span>Introducing ProtoForge AI Beta</span>
          </div>
          
          <h1 className="mb-6 text-4xl font-extrabold tracking-tight sm:text-6xl lg:text-7xl">
            From Idea to <span className="text-primary">3D Prototype</span> <br className="hidden sm:block" />
            in Minutes
          </h1>
          
          <p className="mx-auto mb-10 max-w-2xl text-lg text-muted-foreground sm:text-xl">
            Turn any input — text, voice, sketch, or drawing — into complete, manufacturing-ready 3D prototypes. ISO-compliant drawings, FEA simulations, and BOMs included.
          </p>
          
          <div className="flex flex-col items-center justify-center space-y-4 sm:flex-row sm:space-x-4 sm:space-y-0">
            <Link href="/login">
              <Button size="lg" className="h-12 px-8 text-base">
                Start Building Now
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
            <Link href="#features">
              <Button size="lg" variant="outline" className="h-12 px-8 text-base">
                View Sample Projects
              </Button>
            </Link>
          </div>
        </motion.div>
        
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.2 }}
          className="mt-16 overflow-hidden rounded-xl border bg-card shadow-2xl"
        >
          {/* Placeholder for a 3D viewer or demo video */}
          <div className="aspect-video w-full bg-muted flex items-center justify-center">
            <div className="text-muted-foreground">Interactive 3D Demo Placeholder</div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}

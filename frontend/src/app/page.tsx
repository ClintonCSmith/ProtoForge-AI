import Hero from '@/components/hero'
import { CheckCircle2, Cpu, FileText, Layers, MousePointer2, Zap } from 'lucide-react'

const features = [
  {
    name: 'Multi-modal Input',
    description: 'Describe your idea with text, voice commands, or hand-drawn sketches.',
    icon: MousePointer2,
  },
  {
    name: 'Parametric 3D Models',
    description: 'Get high-quality STEP, STL, OBJ, and GLTF files ready for CAD and 3D printing.',
    icon: Layers,
  },
  {
    name: 'Engineering Drawings',
    description: 'ISO-compliant technical drawings generated automatically for manufacturing.',
    icon: FileText,
  },
  {
    name: 'Stress Simulations',
    description: 'Integrated FEA stress analysis to verify the structural integrity of your designs.',
    icon: Cpu,
  },
  {
    name: 'Instant Renders',
    description: 'Photorealistic 4K renders and MP4 animations for presentations and marketing.',
    icon: Zap,
  },
  {
    name: 'Manufacturing BOM',
    description: 'Complete bill of materials with real-time cost estimates from global suppliers.',
    icon: CheckCircle2,
  },
]

export default function Home() {
  return (
    <>
      <Hero />
      
      {/* Features Section */}
      <section id="features" className="bg-muted/30 py-24">
        <div className="container px-4">
          <div className="mb-16 text-center">
            <h2 className="mb-4 text-3xl font-bold tracking-tight sm:text-4xl">Everything you need to go from concept to product</h2>
            <p className="mx-auto max-w-2xl text-muted-foreground">
              ProtoForge AI combines cutting-edge generative AI with industrial-grade engineering tools.
            </p>
          </div>
          
          <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
            {features.map((feature) => (
              <div key={feature.name} className="relative rounded-2xl border bg-card p-8 transition-shadow hover:shadow-md">
                <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10 text-primary">
                  <feature.icon className="h-6 w-6" />
                </div>
                <h3 className="mb-2 font-semibold">{feature.name}</h3>
                <p className="text-sm text-muted-foreground">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-24">
        <div className="container px-4">
          <div className="mb-16 text-center">
            <h2 className="mb-4 text-3xl font-bold tracking-tight sm:text-4xl">Simple, transparent pricing</h2>
            <p className="mx-auto max-w-2xl text-muted-foreground">
              Choose the plan that fits your prototyping needs.
            </p>
          </div>
          
          <div className="grid gap-8 md:grid-cols-3">
            {[
              { name: 'Starter', price: '$29', description: 'Perfect for freelancers and students', projects: '10 projects/mo' },
              { name: 'Professional', price: '$99', description: 'For professional design firms', projects: '50 projects/mo', popular: true },
              { name: 'Enterprise', price: '$299', description: 'For large manufacturing teams', projects: 'Unlimited projects' },
            ].map((plan) => (
              <div key={plan.name} className={`relative flex flex-col rounded-2xl border p-8 ${plan.popular ? 'border-primary ring-1 ring-primary' : ''}`}>
                {plan.popular && (
                  <span className="absolute -top-4 left-1/2 -translate-x-1/2 rounded-full bg-primary px-3 py-1 text-xs font-semibold text-primary-foreground">
                    Most Popular
                  </span>
                )}
                <h3 className="text-lg font-semibold">{plan.name}</h3>
                <div className="mt-4 flex items-baseline">
                  <span className="text-4xl font-bold">{plan.price}</span>
                  <span className="ml-1 text-muted-foreground">/mo</span>
                </div>
                <p className="mt-2 text-sm text-muted-foreground">{plan.description}</p>
                <ul className="mt-8 flex-1 space-y-4 text-sm">
                  <li className="flex items-center">
                    <CheckCircle2 className="mr-2 h-4 w-4 text-primary" />
                    {plan.projects}
                  </li>
                  <li className="flex items-center">
                    <CheckCircle2 className="mr-2 h-4 w-4 text-primary" />
                    Full export suite (STEP, STL, OBJ)
                  </li>
                  <li className="flex items-center">
                    <CheckCircle2 className="mr-2 h-4 w-4 text-primary" />
                    4K Renders & MP4 Animations
                  </li>
                </ul>
                <button className={`mt-8 w-full rounded-lg px-4 py-2 text-sm font-semibold transition-colors ${plan.popular ? 'bg-primary text-primary-foreground hover:bg-primary/90' : 'bg-muted hover:bg-muted/80'}`}>
                  Get Started
                </button>
              </div>
            ))}
          </div>
        </div>
      </section>
    </>
  )
}

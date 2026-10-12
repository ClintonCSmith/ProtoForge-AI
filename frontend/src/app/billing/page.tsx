'use client'

import React from 'react'
import { 
  CreditCard, 
  Check, 
  Zap, 
  Star, 
  Crown, 
  ExternalLink, 
  Download,
  AlertCircle
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Progress } from '@/components/ui/progress'

const PLANS = [
  { 
    name: 'Free', 
    price: '$0', 
    features: ['1 project/month', 'Public sharing', '480p renders'],
    icon: Zap,
    color: 'slate'
  },
  { 
    name: 'Starter', 
    price: '$29', 
    features: ['10 projects/month', 'Full export suite', '4K renders'],
    current: true,
    icon: Star,
    color: 'blue'
  },
  { 
    name: 'Professional', 
    price: '$99', 
    features: ['50 projects/month', 'FEA Simulation', 'Priority queue'],
    icon: Crown,
    color: 'purple'
  },
  { 
    name: 'Enterprise', 
    price: 'Custom', 
    features: ['Unlimited projects', 'SSO & SLA', 'Custom training'],
    icon: CreditCard,
    color: 'amber'
  },
]

const INVOICES = [
  { id: 'INV-001', date: '2026-06-01', amount: '$29.00', status: 'Paid' },
  { id: 'INV-002', date: '2026-05-01', amount: '$29.00', status: 'Paid' },
]

export default function BillingPage() {
  return (
    <div className="p-8 max-w-6xl mx-auto space-y-10 animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Subscription & Billing</h1>
          <p className="text-muted-foreground mt-1">Manage your plan, payment methods, and invoice history.</p>
        </div>
        <Button className="bg-blue-600 hover:bg-blue-500 rounded-xl gap-2 h-12 font-bold">
          Manage in Stripe
          <ExternalLink className="h-4 w-4" />
        </Button>
      </div>

      {/* Current Plan Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <Card className="lg:col-span-2 border-2 shadow-sm rounded-3xl overflow-hidden">
          <CardHeader className="bg-slate-50 dark:bg-slate-900/50 border-b pb-8">
            <div className="flex justify-between items-start">
              <div>
                <Badge className="bg-blue-600/10 text-blue-600 border-none uppercase font-bold text-[10px] mb-2">Active Plan</Badge>
                <CardTitle className="text-2xl font-bold">Starter Plan</CardTitle>
                <CardDescription>Billed monthly. Next billing date: July 1, 2026.</CardDescription>
              </div>
              <div className="text-right">
                <p className="text-3xl font-bold">$29.00</p>
                <p className="text-xs text-muted-foreground">per month</p>
              </div>
            </div>
          </CardHeader>
          <CardContent className="p-8 space-y-8">
            <div className="space-y-4">
              <div className="flex justify-between items-center text-sm">
                <span className="font-bold flex items-center gap-2">
                  Project Usage
                  <span className="text-xs font-normal text-muted-foreground">3 / 10 used</span>
                </span>
                <span className="text-blue-600 font-bold">30%</span>
              </div>
              <Progress value={30} className="h-3 bg-slate-100 dark:bg-slate-800" />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="flex items-center gap-3 p-4 rounded-2xl border bg-slate-50 dark:bg-slate-900/50">
                <div className="h-10 w-10 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center text-blue-600">
                  <Star className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-xs font-bold uppercase tracking-widest text-slate-500">Plan Tier</p>
                  <p className="font-bold">Starter Individual</p>
                </div>
              </div>
              <div className="flex items-center gap-3 p-4 rounded-2xl border bg-slate-50 dark:bg-slate-900/50">
                <div className="h-10 w-10 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center text-green-600">
                  <CreditCard className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-xs font-bold uppercase tracking-widest text-slate-500">Payment Method</p>
                  <p className="font-bold">Visa •••• 4242</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-2 shadow-sm rounded-3xl bg-blue-600 text-white flex flex-col justify-between">
          <CardHeader>
            <div className="h-12 w-12 rounded-2xl bg-white/10 flex items-center justify-center mb-4">
              <Zap className="h-6 w-6 text-white" />
            </div>
            <CardTitle className="text-xl font-bold">Need more power?</CardTitle>
            <CardDescription className="text-blue-100">Upgrade to Professional to unlock FEA stress simulations and priority forging.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {['FEA Stress Simulation', 'BOM Cost Optimization', 'Priority Cloud Queue', 'Team Collaboration'].map(f => (
                <div key={f} className="flex items-center gap-2 text-xs font-medium">
                  <Check className="h-3 w-3 text-blue-300" />
                  {f}
                </div>
              ))}
            </div>
          </CardContent>
          <CardFooter className="pb-8">
            <Button variant="secondary" className="w-full bg-white text-blue-600 hover:bg-blue-50 font-bold h-12 rounded-xl">
              Upgrade to Pro
            </Button>
          </CardFooter>
        </Card>
      </div>

      {/* Plan Comparison Table */}
      <div className="space-y-6">
        <h2 className="text-xl font-bold">Available Plans</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
          {PLANS.map((plan) => (
            <Card key={plan.name} className={`relative border-2 rounded-3xl overflow-hidden transition-all ${plan.current ? 'border-blue-500 shadow-lg' : 'hover:border-slate-300'}`}>
              {plan.current && (
                <div className="absolute top-0 right-0 p-2">
                  <Badge className="bg-blue-500 text-white border-none uppercase text-[8px]">Active</Badge>
                </div>
              )}
              <CardHeader>
                <div className={`h-10 w-10 rounded-xl mb-4 flex items-center justify-center ${
                  plan.color === 'blue' ? 'bg-blue-100 text-blue-600' :
                  plan.color === 'purple' ? 'bg-purple-100 text-purple-600' :
                  plan.color === 'amber' ? 'bg-amber-100 text-amber-600' :
                  'bg-slate-100 text-slate-600'
                }`}>
                  <plan.icon className="h-5 w-5" />
                </div>
                <CardTitle className="text-lg">{plan.name}</CardTitle>
                <div className="flex items-baseline gap-1 mt-2">
                  <span className="text-2xl font-bold">{plan.price}</span>
                  {plan.price !== 'Custom' && <span className="text-xs text-muted-foreground">/mo</span>}
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                {plan.features.map(f => (
                  <div key={f} className="flex items-center gap-2 text-xs">
                    <Check className="h-3 w-3 text-green-500" />
                    {f}
                  </div>
                ))}
              </CardContent>
              <CardFooter className="pt-4">
                <Button 
                  variant={plan.current ? "secondary" : "outline"} 
                  className="w-full rounded-xl font-bold"
                  disabled={plan.current}
                >
                  {plan.current ? 'Current Plan' : plan.name === 'Enterprise' ? 'Contact Sales' : 'Switch Plan'}
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>
      </div>

      {/* Invoice History */}
      <div className="space-y-6">
        <h2 className="text-xl font-bold">Billing History</h2>
        <Card className="border-2 shadow-sm rounded-3xl overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow className="bg-slate-50 dark:bg-slate-900/50">
                <TableHead className="font-bold">Invoice ID</TableHead>
                <TableHead className="font-bold">Date</TableHead>
                <TableHead className="font-bold">Amount</TableHead>
                <TableHead className="font-bold">Status</TableHead>
                <TableHead className="font-bold text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {INVOICES.map((inv) => (
                <TableRow key={inv.id}>
                  <TableCell className="font-mono text-xs">{inv.id}</TableCell>
                  <TableCell className="text-sm">{inv.date}</TableCell>
                  <TableCell className="text-sm font-bold">{inv.amount}</TableCell>
                  <TableCell>
                    <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200 text-[10px] font-bold">
                      {inv.status}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right">
                    <Button variant="ghost" size="sm" className="gap-2">
                      <Download className="h-3 w-3" />
                      PDF
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Card>
      </div>
    </div>
  )
}

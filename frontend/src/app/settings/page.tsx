'use client'

import React, { useState } from 'react'
import { 
  User, 
  Key, 
  Bell, 
  Shield, 
  Save, 
  Copy, 
  RotateCcw, 
  Mail, 
  Building,
  CheckCircle2
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Switch } from '@/components/ui/switch'
import { Separator } from '@/components/ui/separator'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"

export default function SettingsPage() {
  const [apiKey, setApiKey] = useState('protoforge_sk_8f3d2a1b9c7e4a5d6e7f8g9h0i')
  const [isRotating, setIsRotating] = useState(false)
  const [copied, setCopied] = useState(false)

  const handleRotateKey = () => {
    setIsRotating(true)
    setTimeout(() => {
      setApiKey('protoforge_sk_' + Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15))
      setIsRotating(false)
    }, 1500)
  }

  const copyKey = () => {
    navigator.clipboard.writeText(apiKey)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-8 animate-in fade-in duration-500">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground mt-1">Manage your account, security, and integration preferences.</p>
      </div>

      <Tabs defaultValue="profile" className="w-full">
        <TabsList className="bg-slate-100 dark:bg-slate-900 h-11 p-1 rounded-xl">
          <TabsTrigger value="profile" className="rounded-lg gap-2 font-bold px-6">
            <User className="h-4 w-4" />
            Profile
          </TabsTrigger>
          <TabsTrigger value="api" className="rounded-lg gap-2 font-bold px-6">
            <Key className="h-4 w-4" />
            API Keys
          </TabsTrigger>
          <TabsTrigger value="notifications" className="rounded-lg gap-2 font-bold px-6">
            <Bell className="h-4 w-4" />
            Notifications
          </TabsTrigger>
        </TabsList>

        {/* Profile Tab */}
        <TabsContent value="profile" className="mt-8">
          <Card className="border-2 shadow-sm rounded-2xl overflow-hidden">
            <CardHeader className="bg-slate-50 dark:bg-slate-900/50 border-b">
              <CardTitle className="text-lg">Personal Information</CardTitle>
              <CardDescription>Update your personal details and company information.</CardDescription>
            </CardHeader>
            <CardContent className="p-6 space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="name">Full Name</Label>
                  <Input id="name" defaultValue="John Designer" className="rounded-lg h-10" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="email">Email Address</Label>
                  <Input id="email" type="email" defaultValue="john@protoforge.ai" className="rounded-lg h-10" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="company">Company</Label>
                  <div className="relative">
                    <Building className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                    <Input id="company" defaultValue="DesignForge Studios" className="pl-10 rounded-lg h-10" />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="role">Role</Label>
                  <Input id="role" defaultValue="Industrial Designer" className="rounded-lg h-10" />
                </div>
              </div>
              <Separator />
              <div className="flex justify-end">
                <Button className="bg-blue-600 hover:bg-blue-500 rounded-xl gap-2 px-8 font-bold">
                  <Save className="h-4 w-4" />
                  Save Changes
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* API Keys Tab */}
        <TabsContent value="api" className="mt-8">
          <Card className="border-2 shadow-sm rounded-2xl">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Key className="h-5 w-5 text-blue-500" />
                Secret API Keys
              </CardTitle>
              <CardDescription>
                Use these keys to authenticate your requests to the ProtoForge AI API. Keep them secure.
              </CardDescription>
            </CardHeader>
            <CardContent className="p-6 space-y-6">
              <div className="space-y-4">
                <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 flex items-center justify-between group">
                  <div className="font-mono text-sm text-slate-300 truncate pr-4">
                    {apiKey.replace(/(.{15}).+/, '$1••••••••••••••••••••')}
                  </div>
                  <div className="flex items-center gap-2">
                    <Button 
                      size="sm" 
                      variant="secondary" 
                      className="bg-slate-800 hover:bg-slate-700 text-white border-none gap-2"
                      onClick={copyKey}
                    >
                      {copied ? <CheckCircle2 className="h-4 w-4 text-green-500" /> : <Copy className="h-4 w-4" />}
                      {copied ? 'Copied' : 'Copy'}
                    </Button>
                    
                    <Dialog>
                      <DialogTrigger asChild>
                        <Button size="sm" variant="ghost" className="text-slate-500 hover:text-white">
                          <RotateCcw className="h-4 w-4" />
                        </Button>
                      </DialogTrigger>
                      <DialogContent>
                        <DialogHeader>
                          <DialogTitle>Rotate API Key?</DialogTitle>
                          <DialogDescription>
                            This will invalidate your current key immediately. Any services using it will stop working.
                          </DialogDescription>
                        </DialogHeader>
                        <DialogFooter>
                          <Button variant="outline">Cancel</Button>
                          <Button 
                            className="bg-red-600 hover:bg-red-500 text-white" 
                            onClick={handleRotateKey}
                            disabled={isRotating}
                          >
                            {isRotating ? 'Rotating...' : 'Yes, Rotate Key'}
                          </Button>
                        </DialogFooter>
                      </DialogContent>
                    </Dialog>
                  </div>
                </div>
                <p className="text-[10px] text-muted-foreground flex items-center gap-1">
                  <Shield className="h-3 w-3" />
                  Last rotated on June 12, 2026
                </p>
              </div>

              <div className="p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-100 dark:border-blue-900 rounded-xl">
                <p className="text-sm font-bold text-blue-700 dark:text-blue-300">Developers</p>
                <p className="text-xs text-blue-600 dark:text-blue-400 mt-1">
                  View our <Link href="/docs" className="underline font-bold">API Documentation</Link> to learn how to integrate ProtoForge into your custom workflows.
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Notifications Tab */}
        <TabsContent value="notifications" className="mt-8 space-y-6">
          <Card className="border-2 shadow-sm rounded-2xl">
            <CardHeader>
              <CardTitle className="text-lg">Email Notifications</CardTitle>
              <CardDescription>Configure when you want to be contacted via email.</CardDescription>
            </CardHeader>
            <CardContent className="p-6 space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label className="text-sm font-bold">Project Completion</Label>
                    <p className="text-xs text-muted-foreground">Receive an email when your 3D prototype is ready.</p>
                  </div>
                  <Switch defaultChecked />
                </div>
                <Separator />
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label className="text-sm font-bold">Weekly Digest</Label>
                    <p className="text-xs text-muted-foreground">A summary of your projects and usage for the week.</p>
                  </div>
                  <Switch defaultChecked />
                </div>
                <Separator />
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label className="text-sm font-bold">Model Evolution</Label>
                    <p className="text-xs text-muted-foreground">Get notified when our AI engine improves based on your feedback.</p>
                  </div>
                  <Switch />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

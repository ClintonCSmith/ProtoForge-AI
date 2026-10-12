'use client'

import React, { useState, useEffect } from 'react'
import QRCode from 'qrcode'
import { 
  Share2, 
  Lock, 
  Globe, 
  Key, 
  Copy, 
  Check, 
  Twitter, 
  Linkedin, 
  Mail, 
  Calendar as CalendarIcon,
  Code
} from 'lucide-react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter
} from "@/components/ui/dialog"
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

export function ShareModal({ projectId }: { projectId: string }) {
  const [visibility, setVisibility] = useState('private')
  const [copied, setCopied] = useState(false)
  const [qrCode, setQrCode] = useState('')
  const shareUrl = `https://protoforge.ai/share/${projectId}`
  const embedCode = `<iframe src="https://protoforge.ai/embed/${projectId}" width="100%" height="600" frameborder="0"></iframe>`

  useEffect(() => {
    QRCode.toDataURL(shareUrl, { width: 200, margin: 2 }, (err, url) => {
      if (!err) setQrCode(url)
    })
  }, [shareUrl])

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline" className="gap-2">
          <Share2 className="h-4 w-4" />
          Share
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Share Prototype</DialogTitle>
          <DialogDescription>
            Manage visibility and sharing options for this prototype.
          </DialogDescription>
        </DialogHeader>

        <Tabs defaultValue="link" className="w-full mt-4">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="link">Link</TabsTrigger>
            <TabsTrigger value="embed">Embed</TabsTrigger>
            <TabsTrigger value="qr">QR Code</TabsTrigger>
          </TabsList>

          <TabsContent value="link" className="space-y-6 pt-4">
            <div className="space-y-4">
              <Label>Visibility</Label>
              <RadioGroup value={visibility} onValueChange={setVisibility} className="grid grid-cols-1 gap-2">
                <div className="flex items-center space-x-3 space-y-0 rounded-lg border p-3 hover:bg-slate-50 dark:hover:bg-slate-900 transition-colors">
                  <RadioGroupItem value="private" id="private" />
                  <Label htmlFor="private" className="flex flex-1 items-center gap-3 cursor-pointer">
                    <Lock className="h-4 w-4 text-slate-400" />
                    <div>
                      <p className="font-bold">Private</p>
                      <p className="text-[10px] text-muted-foreground">Only you and invited teammates can view.</p>
                    </div>
                  </Label>
                </div>
                <div className="flex items-center space-x-3 space-y-0 rounded-lg border p-3 hover:bg-slate-50 dark:hover:bg-slate-900 transition-colors">
                  <RadioGroupItem value="password" id="password" />
                  <Label htmlFor="password" className="flex flex-1 items-center gap-3 cursor-pointer">
                    <Key className="h-4 w-4 text-amber-500" />
                    <div>
                      <p className="font-bold">Password Protected</p>
                      <p className="text-[10px] text-muted-foreground">Anyone with the link and password can view.</p>
                    </div>
                  </Label>
                </div>
                <div className="flex items-center space-x-3 space-y-0 rounded-lg border p-3 hover:bg-slate-50 dark:hover:bg-slate-900 transition-colors">
                  <RadioGroupItem value="public" id="public" />
                  <Label htmlFor="public" className="flex flex-1 items-center gap-3 cursor-pointer">
                    <Globe className="h-4 w-4 text-blue-500" />
                    <div>
                      <p className="font-bold">Public</p>
                      <p className="text-[10px] text-muted-foreground">Anyone with the link can view.</p>
                    </div>
                  </Label>
                </div>
              </RadioGroup>
            </div>

            {visibility === 'password' && (
              <div className="space-y-2 animate-in fade-in slide-in-from-top-2">
                <Label htmlFor="pass">Set Password</Label>
                <Input id="pass" type="password" placeholder="Enter share password" />
              </div>
            )}

            <div className="space-y-2">
              <Label>Share Link</Label>
              <div className="flex gap-2">
                <Input value={shareUrl} readOnly className="font-mono text-xs bg-slate-50 dark:bg-slate-900" />
                <Button size="icon" onClick={() => copyToClipboard(shareUrl)}>
                  {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                </Button>
              </div>
            </div>

            <div className="flex justify-center gap-4 pt-2">
              <Button size="icon" variant="outline" className="rounded-full hover:text-blue-400">
                <Twitter className="h-4 w-4" />
              </Button>
              <Button size="icon" variant="outline" className="rounded-full hover:text-blue-700">
                <Linkedin className="h-4 w-4" />
              </Button>
              <Button size="icon" variant="outline" className="rounded-full hover:text-slate-600">
                <Mail className="h-4 w-4" />
              </Button>
            </div>
          </TabsContent>

          <TabsContent value="embed" className="space-y-4 pt-4">
            <div className="space-y-2">
              <Label className="flex items-center gap-2">
                <Code className="h-4 w-4" />
                iFrame Embed Code
              </Label>
              <div className="relative">
                <textarea 
                  value={embedCode} 
                  readOnly 
                  className="w-full h-32 p-3 text-[10px] font-mono bg-slate-950 text-slate-300 rounded-lg border border-slate-800 focus:outline-none"
                />
                <Button 
                  size="sm" 
                  className="absolute bottom-3 right-3 gap-2"
                  onClick={() => copyToClipboard(embedCode)}
                >
                  <Copy className="h-3 w-3" />
                  Copy
                </Button>
              </div>
              <p className="text-[10px] text-muted-foreground italic">
                * Prototypes must be set to 'Public' to be visible in embeds.
              </p>
            </div>
          </TabsContent>

          <TabsContent value="qr" className="pt-4 flex flex-col items-center gap-4">
            <div className="p-4 bg-white rounded-xl border-4 border-slate-100 shadow-inner">
              {qrCode ? (
                <img src={qrCode} alt="Share QR Code" className="w-48 h-48" />
              ) : (
                <div className="w-48 h-48 bg-slate-100 animate-pulse rounded-lg" />
              )}
            </div>
            <p className="text-xs text-center text-muted-foreground px-8">
              Scan this code to view the interactive 3D prototype and AR model on your mobile device.
            </p>
            <Button variant="outline" size="sm" onClick={() => copyToClipboard(qrCode)}>
              Download QR Image
            </Button>
          </TabsContent>
        </Tabs>

        <DialogFooter className="mt-6 pt-6 border-t">
          <div className="flex items-center justify-between w-full">
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <CalendarIcon className="h-3 w-3" />
              Expires in 30 days
            </div>
            <Button>Save Settings</Button>
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

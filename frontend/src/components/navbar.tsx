import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { createClient } from '@/lib/supabase/server'
import { Box } from 'lucide-react'

export default async function Navbar() {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()

  return (
    <nav className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        <Link href="/" className="flex items-center space-x-2">
          <Box className="h-6 w-6 text-primary" />
          <span className="text-xl font-bold">ProtoForge AI</span>
        </Link>
        
        <div className="hidden md:flex md:items-center md:space-x-6">
          <Link href="#features" className="text-sm font-medium transition-colors hover:text-primary">
            Features
          </Link>
          <Link href="#pricing" className="text-sm font-medium transition-colors hover:text-primary">
            Pricing
          </Link>
          {user ? (
            <Link href="/dashboard" className="text-sm font-medium transition-colors hover:text-primary">
              Dashboard
            </Link>
          ) : null}
        </div>

        <div className="flex items-center space-x-4">
          {user ? (
            <form action="/auth/signout" method="post">
              <Button variant="ghost" size="sm">
                Sign Out
              </Button>
            </form>
          ) : (
            <>
              <Link href="/login">
                <Button variant="ghost" size="sm">
                  Log in
                </Button>
              </Link>
              <Link href="/login">
                <Button size="sm">Get Started</Button>
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}

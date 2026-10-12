'use client'

import React, { useState } from 'react'
import * as XLSX from 'xlsx'
import { 
  Download, 
  FileSpreadsheet, 
  ChevronDown, 
  ChevronRight, 
  ExternalLink,
  Table as TableIcon,
  Calculator,
  ArrowUpDown
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'

const MOCK_BOM = [
  { id: 'PF-001', desc: 'Main Chassis Plate', material: 'Aluminum 6061-T6', qty: 1, unitCost: 45.50, suppliers: [
    { name: 'Xometry', url: 'https://xometry.com', leadTime: '5 days' },
    { name: 'Protolabs', url: 'https://protolabs.com', leadTime: '3 days' }
  ]},
  { id: 'PF-002', desc: 'Support Column', material: 'Stainless Steel 304', qty: 4, unitCost: 12.75, suppliers: [
    { name: 'McMaster-Carr', url: 'https://mcmaster.com', leadTime: '1 day' }
  ]},
  { id: 'PF-003', desc: 'Custom Gear Housing', material: 'ABS Plastic (3D Printed)', qty: 2, unitCost: 8.20, suppliers: [
    { name: 'Shapeways', url: 'https://shapeways.com', leadTime: '7 days' }
  ]},
  { id: 'PF-004', desc: 'M5 x 20mm Socket Head Bolt', material: 'Steel (Zinc Plated)', qty: 16, unitCost: 0.12, suppliers: [
    { name: 'McMaster-Carr', url: 'https://mcmaster.com', leadTime: '1 day' }
  ]},
  { id: 'PF-005', desc: 'Elastomer Gasket', material: 'Nitrile Rubber', qty: 1, unitCost: 4.30, suppliers: [
    { name: 'Apple Rubber', url: 'https://applerubber.com', leadTime: '10 days' }
  ]},
]

const CURRENCIES: Record<string, { symbol: string, rate: number }> = {
  USD: { symbol: '$', rate: 1.0 },
  EUR: { symbol: '€', rate: 0.92 },
  GBP: { symbol: '£', rate: 0.79 },
  ZAR: { symbol: 'R', rate: 18.50 },
}

export function BOMTable({ projectId, bomUrl }: { projectId: string, bomUrl?: string }) {
  const [currency, setCurrency] = useState('USD')
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set())

  const toggleRow = (id: string) => {
    const next = new Set(expandedRows)
    if (next.has(id)) next.delete(id)
    else next.add(id)
    setExpandedRows(next)
  }

  const formatPrice = (val: number) => {
    const cur = CURRENCIES[currency]
    return `${cur.symbol}${(val * cur.rate).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
  }

  const totalMaterialCost = MOCK_BOM.reduce((sum, item) => sum + (item.unitCost * item.qty), 0)
  const estManufacturingCost = totalMaterialCost * 0.4 // Mock multiplier
  const totalCost = totalMaterialCost + estManufacturingCost

  const exportToExcel = () => {
    const data = MOCK_BOM.map(item => ({
      'Part #': item.id,
      'Description': item.desc,
      'Material': item.material,
      'Qty': item.qty,
      'Unit Cost': item.unitCost,
      'Total Cost': item.unitCost * item.qty
    }))
    const ws = XLSX.utils.json_to_sheet(data)
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, "BOM")
    XLSX.writeFile(wb, `ProtoForge_BOM_${projectId.slice(0,8)}.xlsx`)
  }

  const exportToCSV = () => {
    const headers = ['Part #', 'Description', 'Material', 'Qty', 'Unit Cost', 'Total Cost']
    const rows = MOCK_BOM.map(item => [
      item.id, item.desc, item.material, item.qty, item.unitCost, item.unitCost * item.qty
    ])
    const csvContent = "data:text/csv;charset=utf-8," + [headers, ...rows].map(e => e.join(",")).join("\n")
    const encodedUri = encodeURI(csvContent)
    const link = document.createElement("a")
    link.setAttribute("href", encodedUri)
    link.setAttribute("download", `ProtoForge_BOM_${projectId.slice(0,8)}.csv`)
    document.body.appendChild(link)
    link.click()
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <h3 className="text-xl font-bold flex items-center gap-2">
          <TableIcon className="h-5 w-5 text-blue-500" />
          Manufacturing BOM
        </h3>
        <div className="flex items-center gap-2 w-full sm:w-auto">
          <Select value={currency} onValueChange={setCurrency}>
            <SelectTrigger className="w-24 h-9 bg-slate-50 dark:bg-slate-900 border-slate-200 dark:border-slate-800">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {Object.keys(CURRENCIES).map(c => (
                <SelectItem key={c} value={c}>{c}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <div className="h-8 w-[1px] bg-slate-200 dark:bg-slate-800 mx-1" />
          <Button variant="outline" size="sm" className="h-9 gap-2" onClick={exportToCSV}>
            CSV
          </Button>
          <Button variant="outline" size="sm" className="h-9 gap-2 border-green-200 text-green-700 bg-green-50 hover:bg-green-100" onClick={exportToExcel}>
            <FileSpreadsheet className="h-4 w-4" />
            Excel
          </Button>
        </div>
      </div>

      <div className="border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden shadow-sm bg-white dark:bg-slate-950">
        <Table>
          <TableHeader>
            <TableRow className="bg-slate-50 dark:bg-slate-900/50">
              <TableHead className="w-[50px]"></TableHead>
              <TableHead className="font-bold">Part # <ArrowUpDown className="h-3 w-3 inline ml-1 cursor-pointer opacity-50" /></TableHead>
              <TableHead className="font-bold">Description</TableHead>
              <TableHead className="font-bold">Material</TableHead>
              <TableHead className="font-bold text-center">Qty</TableHead>
              <TableHead className="font-bold text-right">Unit Cost</TableHead>
              <TableHead className="font-bold text-right">Total</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {MOCK_BOM.map((item) => (
              <React.Fragment key={item.id}>
                <TableRow className="cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-900/50" onClick={() => toggleRow(item.id)}>
                  <TableCell>
                    {expandedRows.has(item.id) ? <ChevronDown className="h-4 w-4 text-slate-400" /> : <ChevronRight className="h-4 w-4 text-slate-400" />}
                  </TableCell>
                  <TableCell className="font-mono text-xs">{item.id}</TableCell>
                  <TableCell className="font-medium">{item.desc}</TableCell>
                  <TableCell><Badge variant="secondary" className="font-normal text-[10px]">{item.material}</Badge></TableCell>
                  <TableCell className="text-center">{item.qty}</TableCell>
                  <TableCell className="text-right font-mono">{formatPrice(item.unitCost)}</TableCell>
                  <TableCell className="text-right font-bold font-mono">{formatPrice(item.unitCost * item.qty)}</TableCell>
                </TableRow>
                {expandedRows.has(item.id) && (
                  <TableRow className="bg-slate-50/50 dark:bg-slate-900/20">
                    <TableCell colSpan={7} className="p-4">
                      <div className="pl-10 space-y-3">
                        <p className="text-[10px] font-bold uppercase text-slate-500 tracking-wider">Suggested Suppliers</p>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                          {item.suppliers.map((s, i) => (
                            <div key={i} className="flex items-center justify-between p-2 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950">
                              <div className="flex items-center gap-3">
                                <div className="h-8 w-8 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center font-bold text-xs">
                                  {s.name[0]}
                                </div>
                                <div>
                                  <p className="text-xs font-bold">{s.name}</p>
                                  <p className="text-[10px] text-muted-foreground">Lead time: {s.leadTime}</p>
                                </div>
                              </div>
                              <Button size="icon" variant="ghost" asChild>
                                <a href={s.url} target="_blank" rel="noopener noreferrer">
                                  <ExternalLink className="h-3 w-3" />
                                </a>
                              </Button>
                            </div>
                          ))}
                        </div>
                      </div>
                    </TableCell>
                  </TableRow>
                )}
              </React.Fragment>
            ))}
          </TableBody>
        </Table>
      </div>

      {/* Summary Bar */}
      <div className="bg-blue-600 rounded-xl p-6 text-white shadow-lg overflow-hidden relative">
        <div className="absolute top-0 right-0 p-8 opacity-10 pointer-events-none">
          <Calculator className="w-24 h-24" />
        </div>
        <div className="relative grid grid-cols-1 md:grid-cols-3 gap-6 divide-y md:divide-y-0 md:divide-x divide-blue-500/50">
          <div>
            <p className="text-blue-100 text-xs font-bold uppercase tracking-widest mb-1">Material Subtotal</p>
            <p className="text-3xl font-bold font-mono">{formatPrice(totalMaterialCost)}</p>
          </div>
          <div className="md:pl-6 pt-4 md:pt-0">
            <p className="text-blue-100 text-xs font-bold uppercase tracking-widest mb-1">Est. Manufacturing</p>
            <p className="text-3xl font-bold font-mono">{formatPrice(estManufacturingCost)}</p>
          </div>
          <div className="md:pl-6 pt-4 md:pt-0">
            <p className="text-blue-100 text-xs font-bold uppercase tracking-widest mb-1">Estimated Unit Cost</p>
            <p className="text-3xl font-bold font-mono">{formatPrice(totalCost)}</p>
          </div>
        </div>
      </div>
    </div>
  )
}

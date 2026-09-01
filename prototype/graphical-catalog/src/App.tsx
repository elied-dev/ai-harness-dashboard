import { useMemo, useState } from "react"
import {
  Copy,
  ExternalLink,
  FolderOpen,
  RefreshCw,
  Search,
  ShieldCheck,
} from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

type Family = "Skill" | "Agent" | "Rule" | "Prompt"

type Asset = {
  id: string
  name: string
  family: Family
  description: string
  path: string
  updated: string
  placements: Array<{
    harness: string
    scope: string
    state: "active" | "merged" | "shadowed" | "unknown"
  }>
}

const assets: Asset[] = [
  {
    id: "agents-md",
    name: "AGENTS.md",
    family: "Rule",
    description: "Shared repository guidance for coding agents.",
    path: "~/projects/ai-harness-dashboard/AGENTS.md",
    updated: "2 min ago",
    placements: [
      { harness: "Pi CLI", scope: "project", state: "active" },
      { harness: "Codex CLI", scope: "project", state: "merged" },
      { harness: "Cursor", scope: "project", state: "active" },
      { harness: "Copilot CLI", scope: "project", state: "unknown" },
    ],
  },
  {
    id: "research",
    name: "research",
    family: "Skill",
    description: "Researches a question using primary sources.",
    path: "~/.agents/skills/research/SKILL.md",
    updated: "18 min ago",
    placements: [
      { harness: "Pi CLI", scope: "user", state: "active" },
      { harness: "Codex CLI", scope: "user", state: "active" },
      { harness: "Gemini CLI", scope: "user", state: "active" },
    ],
  },
  {
    id: "security-reviewer",
    name: "security-reviewer",
    family: "Agent",
    description: "Reviews trust boundaries and unsafe defaults.",
    path: "~/.claude/agents/security-reviewer.md",
    updated: "Yesterday",
    placements: [{ harness: "Claude Code", scope: "user", state: "active" }],
  },
  {
    id: "review-changes",
    name: "review-changes",
    family: "Prompt",
    description: "Reviews the working tree for actionable findings.",
    path: "~/.pi/agent/prompts/review-changes.md",
    updated: "3 days ago",
    placements: [{ harness: "Pi CLI", scope: "user", state: "active" }],
  },
  {
    id: "frontend-accessibility",
    name: "frontend-accessibility",
    family: "Rule",
    description: "Applies accessibility guidance to frontend files.",
    path: "~/work/acme/.cursor/rules/frontend-accessibility.mdc",
    updated: "5 days ago",
    placements: [{ harness: "Cursor", scope: "project", state: "active" }],
  },
]

const families = ["All", "Skill", "Agent", "Rule", "Prompt"] as const

function App() {
  const [query, setQuery] = useState("")
  const [family, setFamily] = useState<(typeof families)[number]>("All")
  const [selectedId, setSelectedId] = useState(assets[0].id)
  const [status, setStatus] = useState("5 assets from 3 source roots")

  const filtered = useMemo(() => {
    const needle = query.trim().toLowerCase()
    return assets.filter(
      (asset) =>
        (family === "All" || asset.family === family) &&
        (!needle ||
          [
            asset.name,
            asset.description,
            asset.path,
            ...asset.placements.map((placement) => placement.harness),
          ]
            .join(" ")
            .toLowerCase()
            .includes(needle))
    )
  }, [family, query])

  const selected =
    filtered.find((asset) => asset.id === selectedId) ?? filtered[0]

  function copyPath() {
    if (!selected) return
    void navigator.clipboard.writeText(selected.path)
    setStatus("Path copied")
  }

  return (
    <div className="min-h-svh bg-background text-foreground">
      <header className="flex h-14 items-center justify-between border-b px-4">
        <div className="flex items-center gap-3">
          <div className="flex size-7 items-center justify-center rounded-md bg-primary text-xs font-semibold text-primary-foreground">
            AI
          </div>
          <span className="font-medium">AI Harness Dashboard</span>
          <Badge variant="outline" className="hidden gap-1 sm:flex">
            <ShieldCheck data-icon="inline-start" /> Local only
          </Badge>
        </div>
        <Button
          variant="outline"
          onClick={() => setStatus("Scan complete · no changes")}
        >
          <RefreshCw data-icon="inline-start" /> Rescan
        </Button>
      </header>

      <div className="grid min-h-[calc(100svh-3.5rem)] lg:grid-cols-[200px_minmax(0,1fr)_360px]">
        <aside className="border-b p-4 lg:border-r lg:border-b-0">
          <p className="mb-3 text-xs font-medium text-muted-foreground">
            Asset family
          </p>
          <nav
            className="flex flex-wrap gap-1 lg:flex-col"
            aria-label="Asset family"
          >
            {families.map((item) => (
              <Button
                key={item}
                variant={family === item ? "secondary" : "ghost"}
                className="justify-between"
                onClick={() => setFamily(item)}
              >
                {item}
                <span className="text-xs text-muted-foreground">
                  {item === "All"
                    ? assets.length
                    : assets.filter((asset) => asset.family === item).length}
                </span>
              </Button>
            ))}
          </nav>
          <Separator className="my-4" />
          <div className="text-xs text-muted-foreground">
            <p>{status}</p>
            <p className="mt-2">1 discovery problem</p>
          </div>
        </aside>

        <main className="min-w-0 border-b lg:border-r lg:border-b-0">
          <div className="flex flex-col gap-3 border-b p-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h1 className="font-medium">Assets</h1>
              <p className="text-sm text-muted-foreground">
                {filtered.length} results
              </p>
            </div>
            <div className="relative w-full sm:w-72">
              <Search className="absolute top-1/2 left-2.5 size-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Search assets"
                aria-label="Search assets"
                className="pl-8"
              />
            </div>
          </div>

          <ScrollArea className="h-[520px] lg:h-[calc(100svh-8.5rem)]">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Asset</TableHead>
                  <TableHead>Family</TableHead>
                  <TableHead className="text-right">Placements</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filtered.map((asset) => (
                  <TableRow
                    key={asset.id}
                    data-state={
                      selected?.id === asset.id ? "selected" : undefined
                    }
                    className="cursor-pointer"
                    tabIndex={0}
                    onClick={() => setSelectedId(asset.id)}
                    onKeyDown={(event) => {
                      if (event.key === "Enter" || event.key === " ") {
                        event.preventDefault()
                        setSelectedId(asset.id)
                      }
                    }}
                  >
                    <TableCell>
                      <div className="font-medium">{asset.name}</div>
                      <div className="max-w-80 truncate text-xs text-muted-foreground">
                        {asset.description}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">{asset.family}</Badge>
                    </TableCell>
                    <TableCell className="text-right text-muted-foreground">
                      {asset.placements.length}
                    </TableCell>
                  </TableRow>
                ))}
                {filtered.length === 0 && (
                  <TableRow>
                    <TableCell
                      colSpan={3}
                      className="h-24 text-center text-muted-foreground"
                    >
                      No matching assets.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </ScrollArea>
        </main>

        <aside className="p-4">
          {selected ? (
            <Card size="sm">
              <CardHeader>
                <CardTitle>{selected.name}</CardTitle>
                <CardDescription>{selected.description}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <code className="block rounded-md bg-muted p-2 text-xs break-all">
                  {selected.path}
                </code>

                <div className="flex flex-wrap gap-2">
                  <Button
                    size="sm"
                    onClick={() => setStatus("Open in editor · prototype")}
                  >
                    <ExternalLink data-icon="inline-start" /> Open
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => setStatus("Reveal · prototype")}
                  >
                    <FolderOpen data-icon="inline-start" /> Reveal
                  </Button>
                  <Button
                    size="icon-sm"
                    variant="outline"
                    aria-label="Copy path"
                    onClick={copyPath}
                  >
                    <Copy />
                  </Button>
                </div>

                <Separator />

                <div>
                  <h2 className="mb-2 text-sm font-medium">Placements</h2>
                  <div className="space-y-2">
                    {selected.placements.map((placement) => (
                      <div
                        key={`${placement.harness}-${placement.scope}`}
                        className="flex items-center justify-between rounded-md border p-2 text-sm"
                      >
                        <div>
                          <p>{placement.harness}</p>
                          <p className="text-xs text-muted-foreground">
                            {placement.scope} scope
                          </p>
                        </div>
                        <Badge variant="secondary">{placement.state}</Badge>
                      </div>
                    ))}
                  </div>
                </div>

                <Separator />

                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  <span>Updated</span>
                  <span>{selected.updated}</span>
                </div>
              </CardContent>
            </Card>
          ) : (
            <p className="text-sm text-muted-foreground">Select an asset.</p>
          )}
        </aside>
      </div>
    </div>
  )
}

export default App

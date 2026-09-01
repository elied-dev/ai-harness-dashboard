# AI Asset Catalog

The catalog describes file-backed AI assets as they exist across local coding harnesses. Its language separates physical identity, discovered placement, and evidenced compatibility so the UI never invents portability or precedence.

## Assets

**AI Asset**:
One logical catalog item backed by an entry document and, optionally, bundled resources. Its identity follows the underlying filesystem object rather than its declared name or content hash.
_Avoid_: Plugin, integration

**Asset Family**:
The normalized kind of an AI Asset: Skill, Agent, Rule, or Prompt. Native labels remain available; Instruction is a Rule subtype and Command is a Prompt subtype.
_Avoid_: Asset type

**Resource**:
A file bundled beneath an AI Asset, such as a skill script or reference. A Resource is not an independent Asset merely because it is searchable or referenced.
_Avoid_: Child asset

**Catalog Snapshot**:
The complete current result of a successful scan. It contains no history: an Asset that disappears from the filesystem disappears from the next Snapshot.
_Avoid_: Inventory history

## Discovery

**Source Root**:
A user-approved directory boundary for discovery, classified as a known harness location or a custom location and carrying its native and normalized scope.
_Avoid_: Scan path

**Placement**:
One Adapter observation of an AI Asset within a Source Root for a Harness Surface. It preserves the discovered and canonical paths, applicability, native scope, metadata interpretation, and precedence evidence.
_Avoid_: Copy, installation

**Discovery Problem**:
A scan result for an entry that cannot safely become an AI Asset, such as an unreadable or broken entry. It belongs to a Source Root and path, not to a partial Asset.
_Avoid_: Broken asset

## Harnesses

**Harness**:
A coding-assistant product family, independent of the environments in which it runs.
_Avoid_: Platform, provider

**Harness Surface**:
A specific runtime of a Harness, such as its CLI, IDE integration, or cloud agent. Compatibility and precedence claims apply to a Surface rather than vaguely to the whole Harness.
_Avoid_: Harness mode

**Adapter**:
The catalog component that discovers and interprets native facts for one or more related Harness Surfaces. It can report documented precedence but cannot invent a universal winner.
_Avoid_: Plugin, connector

**Compatibility Claim**:
An evidence-backed relationship between an AI Asset and a Harness Surface, with a status of native, portable, extended, unsupported, or unknown. It retains its evidence source and applicable version when known.
_Avoid_: Compatible flag

**Resolution State**:
An Adapter-provided statement that a Placement is active, shadowed, merged, or unknown under a Harness Surface's documented precedence rules.
_Avoid_: Enabled, winner

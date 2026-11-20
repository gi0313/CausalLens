# CausalLens Agent and MCP Architecture

## Purpose

CausalLens will use specialized software agents to coordinate data processing,
semantic interpretation, causal analysis, and human-readable explanations.
Every result should remain traceable to its data, assumptions, and sources.

An agent is a software component with a defined responsibility. Not every agent
must use a large language model.

## Orchestrator Agent

### Responsibility

The Orchestrator Agent receives a user request, checks required inputs, invokes
the appropriate specialist agents, and returns a combined result.

### Inputs

- Selected dataset and split
- Selected engine
- Requested analysis
- User-interface request

### Outputs

- Workflow status
- Combined diagnostic result
- Missing-input or error messages
- Provenance references

### Restrictions

- Must not modify raw data
- Must not invent missing results
- Must preserve limitations from specialist agents
- Must not describe prototype assumptions as validated facts

## Preprocessing Agent

### Responsibility

The Preprocessing Agent loads and validates FD001 data and prepares an engine
trajectory for later components.

### Inputs

- Dataset file
- Dataset split
- Engine identifier

### Outputs

- Validated engine records
- Named sensor fields
- Validation results
- Dataset metadata

### Existing implementation

The initial implementation reuses functions from `src/fd001_loader.py`.

### Restrictions

- Must reject malformed data
- Must report missing and duplicate records
- Must not silently fabricate values

## Semantic Agent

### Responsibility

The Semantic Agent maps engine records and diagnostic results to ontology
concepts.

### Inputs

- Validated engine records
- Causal results
- Ontology
- RDF mapping rules

### Outputs

- RDF triples
- Semantic identifiers
- SPARQL results
- Human-readable labels

### Existing implementation

The project currently includes:

- `ontology/CausalLens.ttl`
- `src/semantic_mapper.py`
- `src/sparql_test.py`

### Restrictions

- Must not create unsupported ontology relationships
- Must preserve mapping provenance

## Causal Analysis Agent

### Responsibility

The Causal Analysis Agent evaluates documented graph paths and produces
prototype diagnostic results.

### Inputs

- Validated engine data
- Edge register
- Selected measurements
- Analysis configuration

### Outputs

- Diagnostic indicator
- Elevated-condition records
- Candidate explanation paths
- Limitations
- Provenance

### Initial implementation

- `src/causal_graph.py`
- `src/diagnostic_query.py`
- `src/causal_provenance.py`
- `docs/causal_edge_register.csv`

### Restrictions

- Must distinguish hypotheses from calculation dependencies
- Must not claim that a graph path proves physical causation
- Must reject unsupported query targets
- Must expose thresholds and assumptions

## Explanation Agent

### Responsibility

The Explanation Agent converts structured results into language appropriate
for a non-expert user.

### Inputs

- Diagnostic summary
- Semantic labels
- Graph paths
- Provenance
- Limitations

### Outputs

- Human-readable trajectory
- Supporting measurements
- Assumptions
- Limitations
- Source references

### Restrictions

- Must remain consistent with the structured results
- Must not invent causes
- Must not invent maintenance recommendations
- Must explain uncertainty

## MCP Position

Model Context Protocol, or MCP, provides controlled access between agents and
project resources or tools. MCP is an integration boundary rather than the
analysis itself.

Potential MCP resources include:

- FD001 dataset metadata
- Ontology concepts
- Causal-edge register
- Provenance records
- Project documentation

Potential MCP tools include:

- Load and validate an engine run
- Query ontology concepts
- Execute a supported diagnostic query
- Retrieve provenance
- Export an explanation

## MCP Boundaries

Each tool should define:

- Required inputs
- Allowed values
- Structured outputs
- Error responses
- Read and write permissions
- Provenance requirements

Raw data should be read-only during analysis. Results should be written to
separate export locations. Unsupported requests should produce a clear error
instead of a fabricated response.

## Proposed Workflow

1. The user selects an FD001 engine.
2. The Orchestrator Agent validates the request.
3. The Preprocessing Agent loads and validates the records.
4. The Semantic Agent maps records to ontology concepts.
5. The Causal Analysis Agent runs a supported diagnostic query.
6. The Explanation Agent creates a readable explanation.
7. The interface displays the result, evidence, and limitations.
8. Provenance connects the result to its data, code, and assumptions.

## Current Prototype Boundary

The current prototype implements data loading, a small documented graph,
diagnostic calculation, explanation paths, provenance, and testing. Full
autonomous agent execution and a production MCP server remain future work.
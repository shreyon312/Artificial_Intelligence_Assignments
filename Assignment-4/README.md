Shreyon Roy
sr5655
Artificial Intelligence CS-GY 6613
Spring 2026
Assignment 4

1. Deep document understanding vs naive chunking (10 pts)
RAGFlow emphasizes layout-aware document parsing (tables, structure, metadata) through its DeepDoc engine and configurable PDF parsers.
Why does deep document understanding outperform fixed-size chunking in enterprise RAG? Discuss implications for: 
Retrieval fidelity, Index design, Preprocessing cost
Answer: Deep document understanding outperforms fixed size chunking because enterprise documents are not usually linear text streams. PDFs, reports, slides, etc. have a more complex format like section headers, captions, tables, or page structures which RAGFlow’s Deepdoc is able to handle because it models it. It has a PDF parser which extracts and outputs text chunks with page coordinates and tables based on natural sentences. It does a good job of keeping the page architecture rather than flattening it. 
There are implications for Retrieval fidelity. Fixed size chunking breaks semantic units at wrong boundaries. Headers can get separated from table rows and captions can get separated from figures. Deep document understanding improves retrieval fidelity because the indexed unit matches the author’s intended meaning. It will contain the right interpretation and correct tokens. 
There are implications for Index design. When parsing is aware of the layout, the index should not be a single text field. All of the raw text and structure including title, table, captions, body, and equations must be preserved. RAGFlow has more positive-aware chunks and table artifacts. So it is better at parsing changes that the retriever is allowed to score. It uses content similarity and structure aware priors. 
There are also implications for Preprocessing cost. Parsing is slower and more resource-intensive. RAGFlow takes longer than simpler frameworks because of layout analysis, table structure recognition, OCR, and built-in parsing models. So the trade-off is front-loaded cost versus downstream accuracy. In high value enterprise scenarios, deep parsing is cheaper than any mistakes with retrieval. 
2. Chunking strategy: template vs semantic (10 pts)
RAGFlow supports configurable chunking strategies rather than a single method.
Compare:
Template-based chunking
Embedding-driven semantic segmentation
Which one fails under:
Highly structured documents (e.g., financial reports)
Loosely structured corpora (e.g., chat logs)
Answer: Template-based chunking uses known structure like section headings, document type templates, XML/HTML tags, report line items, page regions, or schema-driven delimiters. Embedding-driven semantic segmentation uses similarity shifts in embedding space to infer topic boundaries.
For highly structured documents, embedding-driven semantic segmentation fails and template-based chunking is usually better. These documents have meaning through stable structural cues like balance-sheet sections, note numbers, and line-item headers. Semantic segmentation fails in this situation because embedding similarity does not always respect tabular or hierarchical semantics. Two adjacent paragraphs may be semantically similar but belong to different categories. Additionally, a table row may be semantically sparse but structurally essential.
For loosely structured corpora, template-based chunking usually fails and embedding-driven semantic segmentation is generally better. Template-based chunking fails because there is no reliable external structure. A fixed schema ignores topic turns, speaker shifts, and latent subproblems. Semantic segmentation can detect transitions even when both occur in one thread.
3. Hybrid retrieval architecture (10 pts)
RAGFlow combines lexical (BM25), vector similarity, and re-ranking.
Formally analyze why hybrid retrieval improves recall and precision. Provide concrete failure cases for:
Lexical-only
Vector-only
Hybrid (edge case)
Answer: Hybrid retrieval improves quality because sparse and dense retrievers have different error distributions. Sparse retrieval is strong on exact lexical constraints. Dense retrieval is strong on semantic paraphrase and synonymy. Fusion reduces the chance that one retriever’s blind spot eliminates the relevant document. Recall improves because the union of sparse and dense candidates covers more relevant documents than either alone. Precision improves once reranking or calibrated fusion is applied, because candidates retrieved for different reasons can be rescored using a stronger relevance model.
Lexical-only failure can occur in the following scenario. There can be a query “policy for parental leave during adoption.” There can be a relevant passage that says “family expansion benefits for adoptive caregivers.” BM25 may miss it because the vocabulary does not overlap enough. Vector-only failure can occur in the following scenario. There can be a query “error code ORA-00942 in payroll batch.” Dense retrieval may surface semantically related database troubleshooting passages but miss the exact code string, version number, or SKU-like identifier. Hybrid failure edge cases can occur like the following. An example query is “jaguar battery issue.” Sparse retrieval returns car-manual chunks because of “battery” and dense retrieval returns animal-biology text because of “jaguar.” Fusion may rank both above the correct EV-service bulletin if query intent is not resolved. 



4. Multi-stage retrieval pipeline (10 pts)
RAGFlow decomposes retrieval into candidate generation, re-ranking, and query refinement.
Why is a multi-stage pipeline superior to a single-pass ANN search? Discuss:
Recall vs latency trade-off
Cascading error propagation


Answer: A multi-stage retrieval pipeline is better than single-pass ANN search because retrieval in production is not one decision. It is a sequence of increasingly expensive approximations. 
Single-pass ANN is optimized for speed but not final relevance. It is useful for first-stage candidate generation because approximate nearest neighbor search is cheap relative to cross-encoders or graph traversal. But ANN alone tends to optimize local embedding similarity, which is not always the same as task relevance.
There is a downside which is cascading error. If stage 1 fails to include the relevant item, stage 2 cannot recover it. So multi-stage systems shift the design burden onto candidate-generation recall. A second cascading error comes from query refinement. If the system rewrites the query incorrectly, later stages become sharper but wrong.

5. Indexing strategy and storage backends (10 pts)
RAGFlow builds retrieval-optimized indexes rather than relying on generic storage, with support for switching between doc engines including Elasticsearch and Infinity.
Define design criteria for selecting a backend:
Elasticsearch-like hybrid store
Vector-native DB
Graph-augmented store
What workloads favor each?
Answer: Elasticsearch-like hybrid store is selected for strong lexical retrieval, filtering and aggregations, phrase search, mature operational tooling, and enterprise logging and observability. So it is best for enterprise document search and filter-heavy retrieval.
Vector-native DB is selected for high-throughput semantic KNN, low-latency embedding retrieval, large-scale ANN performance, and simpler retrieval workloads with limited lexical needs. This fits recommendation-style retrieval and semantic FAQ lookup where exact identifiers do not matter that much. 
Graph-augmented store is selected for explicit entity/relation traversal, multi-hop retrieval, provenance over relationships, and reasoning over typed edges. So it is best for explicit relational reasoning. 


6. Query understanding and reformulation (10 pts)
RAGFlow incorporates query rewriting and semantic gap handling in its pipeline via its multi-turn optimization feature.
Why is query transformation (e.g., expansion, decomposition) critical in RAG? Compare:
Static query to retrieval
Iterative query refinement (agent-driven)
Answer: Query transformation is critical because user queries are usually bad retrieval objects. They are vague and ambiguous, or phrased in vocabulary that does not match the indexed corpus. RAGFlow exposes mechanisms such as cross-language retrieval and multi-turn optimization, which shows that it is too weak for production RAG.
Static query to retrieval is the simplest path. It is low-latency and easier to debug. It works best when the corpus and user query share vocabulary and when the question is atomic. It fails when there is synonym mismatch, missing disambiguation, or multi-part questions that require decomposition. Iterative query refinement is better when the query is ambiguous, compositional, multilingual, or relational. The retriever can expand acronyms, decompose subquestions, add missing constraints, or search follow-up entity names discovered in initial results. It has two main risks which are drift (the rewritten query becomes more fluent but less faithful to user intent) and latency amplification (each refinement loop adds retrieval and model cost).


7. Knowledge representation layer (10 pts)
RAGFlow can construct embeddings, metadata layers, and knowledge graphs.
Compare three representations:
Dense vector space
Relational schema
Knowledge graph
How does each affect:
Compositional reasoning
Retrieval explainability
Answer: Dense vector space represents each chunk as an embedding in continuous space. It has strong semantic recall and is robust to paraphrase. But it has poor explicit compositional reasoning and is hard to explain why a passage matched. Dense vectors affect compositional reasoning very weakly. Its effect on retrieval explainability is also very low.
Relational schema represents facts as typed tables like entities, timestamps, attributes, document metadata, access controls, and structured business records. It has excellent precision under explicit constraints and strong explainability. But it has weak semantic generalization and limited handling of fuzzy language. Relational schema is ideal for metadata and operational memory, but not sufficient for free-text knowledge by itself. For compositional reasoning, relational schema is strong for formal joins and for retrieval explainability, its effect is high and clear.
Knowledge graph represents entities and relationships explicitly. Supports multi-hop and compositional reasoning and better provenance of relation chains. But its extraction quality is brittle and graph construction is expensive. For compositional reasoning, the knowledge graph is strongest for relation-centric multi-hop reasoning. For retrieval explainability, its effect is medium. They offer the best explainability for complex queries. 


8. Data ingestion pipeline architecture (10 pts)
RAGFlow provides an ingestion pipeline that converts heterogeneous data into indexed knowledge.
Design a robust ingestion system. Address:
Schema normalization across sources
Incremental indexing
Consistency vs throughput trade-offs
Answer: For schema normalization across sources:
Heterogeneous data must be mapped to a Unified Document Schema to ensure the retrieval engine can query them uniformly. The extraction layer must use specialized parsers to pull raw content. The global schema will make sure every ingested object is mapped to a standard record where the content is a raw text chunk, the metadata is standardized fields like source_url, created_at, author, and document_type, and entities are extracted with Named Entity Recognition to populate Knowledge Graphs. In order to normalize, an Adapter Pattern can be used. There can be specific Adapters for each source that output the same JSON schema. This allows you to add new data sources without changing the core indexing logic. 
For incremental indexing:
We can use content hashing which will create a cryptographic hash of each document’s raw content. If the hash has not changed, skip processing for that file. Then, Change Data Capture is used for relational sources, listening to database logs to trigger indexing only on INSERT, UPDATE, or DELETE events.
If a file is no longer present during a crawl, its corresponding vectors and metadata must be removed from the index to prevent hallucinated retrievals from non-existent documents.
For consistency vs throughput trade-offs:
For the throughput use large batch sizes and asynchronous indexing. This gives high efficiency. Processing 10,000 documents at once allows for better GPU utilization during embedding generation. This might cause indexing lag. A user uploads a file but cannot query it for several minutes.
For consistency, use synchronous indexing and immediate "Refresh" calls on the vector database. It will give immediate availability. As soon as the upload finishes, the RAG system can answer questions about it. One downside of this is a massive performance hit. Frequent index refreshes destroy search throughput and increase compute costs significantly.



9. Memory design in RAG systems (10 pts)
RAGFlow introduces memory components for long-running interactions, with evolving support across v0.23 and v0.24.
Compare memory architectures:
Vector memory (semantic recall)
Structured memory (SQL/graph)
Episodic logs (temporal traces)
Answer: 
Vector memory stores past interactions or facts as embeddings for semantic recall. It is good for flexible semantic matching and easy to append-only design. However, it has weak temporal ordering, poor determinism, and it is hard to enforce schemas or constraints. 
Structured memory stores durable user facts, plans, entities, tools, and state in SQL or graph form. It is the best profile facts, task states, preferences, workflow checkpoints. Some of its strengths include precision, constraints, auditability, and better update semantics. But, it is less flexible for fuzzy recall and requires schema and governance
Episodic logs store timestamped traces of interactions, tool calls, and observations. They are good at temporal reasoning and replay/debugging. It preserves chronology and is good for observability and agent accountability. However, it is also a bit noisy, there is a large context volume, and is a weak abstraction by itself.
For the best architecture, one should use vector memory for associative recall, structured memory for durable facts/state, and episodic logs for temporal traceability.



10. End-to-end system decomposition (10 pts)
RAGFlow spans ingestion, indexing, retrieval, reasoning, and serving (see system architecture).
Design a microservices architecture for RAGFlow. Specify:
Stateless vs stateful services
Scaling strategy per component
Failure isolation boundaries
Answer: 
The Mermaid diagram code is:
flowchart LR
   A[Source Connectors] --> B[Ingestion Orchestrator]
   B --> C[Parser Service]
   C --> D[Chunking & Enrichment]
   D --> E[Embedding Service]
   D --> F[Metadata Extractor]
   D --> G[Graph Builder]
   E --> H[Index Writer]
   F --> H
   G --> H
   H --> I[Hybrid Retrieval API]
   I --> J[Reranker Service]
   J --> K[Agent/Reasoning Service]
   K --> L[Serving API]


   M[(Object Store)] --> C
   N[(Metadata DB)] --> B
   O[(Search/Vector Store)] --> I
   P[(Memory Store)] --> K
   Q[(Trace/Event Log)] --> B
   Q --> K

Stateless vs stateful services:
Stateless services are API gateway, retrieval coordinator, reranker workers, agent orchestration workers, parser workers, and embedding workers. Stateful services are object store for raw documents, metadata DB, search/vector index, graph store, memory store, queue/event bus, and cache/session store.
Scaling strategy per component:
Parsing service would scale by job queue and worker pool. GPU-backed workers for OCR/VLM/layout-heavy parsing. Embedding service would scale separately from parsing because the compute pattern differs. Batch aggressively for throughput. Index writer would scale for write bursts, but protect the backend with backpressure. Retrieval API would scale for QPS and tail-latency control. Reranker service would scale elastically because it is expensive and directly impacts latency. Agent service would scale by conversation concurrency, but isolate tool-execution sandboxes from orchestration logic.
Failure isolation boundaries: 
Ingestion must be isolated from serving. Reranker must be optional. If reranking is unavailable, the system should degrade to hybrid retrieval rather than fail closed. Graph retrieval must be isolated. The memory subsystem must degrade safely. If memory retrieval fails, the agent should continue with short-term context rather than block user requests. Index publication must be atomic.
 Prevent half-built indexes from serving traffic.

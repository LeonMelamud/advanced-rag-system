Okay, here is the High-Level Design (HLD) document translated into English, in Markdown format.

```markdown
# High-Level Design (HLD): Advanced RAG System with File Analysis and AI Chat

**Document ID:** ARAG-FS-HLD-001
**Version:** 1.0
**Date:** May 29, 2025

## Version History:

| Version | Date    | Author             | Details                 |
|---------|---------|--------------------|-------------------------|
| 1.0     | 05/29/25| Chief Systems Architect | Initial Document Creation |

## Abstract:

This document details a comprehensive High-Level Design (HLD) for an innovative Retrieval Augmented Generation (RAG) system. This system is designed to provide advanced capabilities in analyzing diverse files and to serve as an intelligent and versatile AI chat interface. The core of the system lies in its ability to ingest, deeply process, understand semantics and contexts, and finally make relevant information accessible from a wide range of common file formats, including complex PDF documents, CSV spreadsheets, plain text files (TXT), and even audio files containing transcriptions. The system is designed to handle significantly large files up to 100MB while maintaining optimal performance and resource efficiency.

The detailed design thoroughly addresses both the functional requirements defining the system's capabilities and the non-functional requirements critical for ensuring its quality, performance, reliability, and security. Key functional capabilities include: high-quality text and relevant metadata extraction from all supported file formats; advanced chunking processes tailored to content type and characteristics to produce atomic yet sufficiently contextualized information units; generation of high-quality semantic embeddings that faithfully represent the information's meaning and enable efficient comparison and search; ability to retrieve accurate and relevant information from multiple Knowledge Collections simultaneously, considering query context; smart merging mechanisms for retrieval results from different sources and prioritization of the most relevant contexts for the answer; and development of an intuitive chat interface supporting multi-turn and complex conversations, while maintaining conversation context and understanding question sequences, in addition to supporting real-time streaming of answers for an enhanced user experience.

Beyond basic functional capabilities, the detailed design also addresses the Knowledge Collection management system. This includes mechanisms for version control of critical configurations, such as system prompts affecting language model behavior, and mappings of external tools integrated into the system. Version management capability allows tracking changes, reverting to previous configurations if necessary, and maintaining system stability and predictability. Additionally, the design includes seamless integration of external tools and complementary services through a flexible orchestrator component. This component will enable the expansion of system capabilities and the integration of custom functionality according to changing needs.

Fundamentally, this detailed design forms a solid foundation for developing an advanced RAG system that is not only powerful and possesses high analytical capabilities but is also scalable to handle growth in information volume and user numbers, and secure to ensure the integrity and privacy of organizational data. This system will enable users to interact efficiently and intuitively with their organizational knowledge bases, receive accurate and context-based answers to complex questions, thereby improving decision-making processes and overall organizational efficiency. The current document is intended to serve as a detailed and comprehensive roadmap for the various development teams, as well as for technical management, providing a shared knowledge base and guiding the development process. It is based on a structural and content depth similar to the document '2\_HLD 0.6 Intelligence Data Management\_Leon\_YW.docx' <1>, with significant expansion and precise adaptation to the unique and advanced needs of this RAG system.

## Table of Contents:
*(The table of contents will be dynamically generated based on the headings and final structure of the document)*

## 1. General

### 1.1. Introduction

The purpose of this document is to provide a comprehensive High-Level Design (HLD) for an advanced Retrieval Augmented Generation (RAG) system, integrated with file analysis capabilities and an AI chat interface. This system is designed to ingest, process, and understand a wide variety of file types, making their content accessible and queryable through an intelligent chat interface. The need for an "advanced" system stems from the understanding that basic RAG systems, focusing on simple question-answering over documents, do not fully address modern organizational challenges. The requirement for "file analysis" and "AI chat" indicates a need for deeper understanding of ingested content and more sophisticated user interaction, which may include multi-turn conversations, context memory, and the ability to synthesize information from diverse sources.

The scope of this HLD includes functional and non-functional requirements, system architecture (logical and physical), component design, data models, key processes, technology stack recommendations, security considerations, deployment strategies, and operational aspects. The document explicitly addresses handling of files (PDF, CSV, TXT, Audio up to 100MB), text and metadata extraction, chunking, embedding creation, retrieval from multiple knowledge collections, context merging and prioritization, AI chat interface, management of collection configurations (versioning of prompts and tools), and the option for integrating external tools.

The target audience for this document includes technical leads, system architects, senior engineers, and project/product managers involved in the design, development, and deployment of the RAG system.

This HLD will strive for a structural depth and level of detail similar to those presented in the document '2_HLD 0.6 Intelligence Data Management_Leon_YW.docx' <1>, while expanding relevant sections to fit the specific needs of an advanced RAG system.

### 1.2. Glossary, Acronyms, and Linked Documents

A comprehensive list of terms, acronyms, and abbreviations used in this document will be provided below and updated throughout the document's creation. A well-defined glossary is essential for a complex system involving terms from AI/ML and data processing domains, ensuring clarity and shared understanding among all stakeholders, thereby preventing misinterpretations that could lead to design or implementation errors. The system involves concepts from several fields: file processing, natural language processing (NLP), large language models (LLMs), databases, information security, and cloud infrastructure. Each field has its unique terminology (e.g., "embedding," "chunking," "vector store" from RAG; "ACID," "sharding" from databases; "RBAC," "TLS" from information security). Different stakeholders (developers, product managers, QA testers, operations personnel) may have varying levels of familiarity with these terms. Ambiguity in terminology can lead to misunderstandings in requirements, design discussions, and implementation details. For example, "metadata" can have different meanings in the context of a file system, a database record, or an AI model. A clear and centralized glossary, similar to that in document <1>, serves as a single source of truth for definitions, reduces ambiguity, and improves communication efficiency throughout the project lifecycle. This directly impacts the quality and correctness of the final system.

#### Table 1: Glossary and Acronyms

| Term/Acronym         | Definition                                       | Context/Relevance to System                                                              |
|----------------------|--------------------------------------------------|------------------------------------------------------------------------------------------|
| RAG                  | Retrieval Augmented Generation                   | The core architecture of the system.                                                     |
| LLM                  | Large Language Model                             | A central component for generating responses and understanding language.                 |
| NLP                  | Natural Language Processing                      | The AI field dealing with understanding and processing human language.                   |
| API                  | Application Programming Interface                | Interface for communication between software components.                                 |
| CRUD                 | Create, Read, Update, Delete                     | Basic data operations.                                                                   |
| RBAC                 | Role-Based Access Control                        | Mechanism for managing user permissions.                                                 |
| SLA                  | Service Level Agreement                          | Commitment to system performance levels.                                                 |
| KPI                  | Key Performance Indicator                        | Metric for measuring system success.                                                     |
| Vector Database      | Vector Database                                  | Database optimized for storing and retrieving embedding vectors.                         |
| Embedding            | Embedding                                        | Vector representation of text or other data in a multi-dimensional space.                |
| Chunking             | Chunking                                         | Process of dividing long text into smaller segments.                                     |
| MCP                  | Model Context Protocol                           | A possible protocol for integrating external tools.                                      |
| Artifact             | Artifact                                         | Generic term referring to a single data unit ingested into the system (inspired by <1>). |
| Strong Identifier    | Strong Identifier                                | A unique attribute used to group and identify data related to a specific entity (inspired by <1>). |
| ACID                 | Atomicity, Consistency, Isolation, Durability    | Properties ensuring reliability of database transactions (inspired by <1>).              |
| FTS                  | Full-Text Search                                 | Search functionality allowing users to search for specific words or phrases (inspired by <1>). |
| SHA256               | Secure Hash Algorithm 256-bit                    | Cryptographic hash function used to create a checksum.                                   |
| MIME Type            | Multipurpose Internet Mail Extensions Type       | Standard identifier for file types on the internet and in communication.                 |
| OCR                  | Optical Character Recognition                    | Technology for converting images of text into editable text.                             |
| UI                   | User Interface                                   | How the user interacts with the system.                                                  |
| UX                   | User Experience                                  | The overall feel and usability of the system for the user.                               |
| RPO                  | Recovery Point Objective                         | Maximum acceptable data loss after a failure.                                            |
| RTO                  | Recovery Time Objective                          | Maximum time allotted to restore the system after a failure.                             |

**Linked Documents:**
1.  `2_HLD 0.6 Intelligence Data Management_Leon_YW.docx` (Serves as a structural and content example).
2.  *(To be completed later if necessary with API documentation of selected services, relevant standards, etc.)*

## 2. System Overview and Goals

### 2.1. Problem Statement and Business Value

The central problem this system aims to solve is the difficulty organizations face in extracting value from the vast repositories of information they possess, locked within a wide array of file formats such as PDF documents, spreadsheets (CSV), text files, and audio recordings. Extracting, understanding, and making this information accessible for decision-making, knowledge discovery, and user support is a significant challenge. Traditional search methods, often keyword-based, struggle to understand context and provide complex, accurate answers. RAG systems help Large Language Models overcome the limitations of the static data they were trained on, providing them access to current and domain-specific information. <2> The RAG technique optimizes LLM output by consulting a reliable knowledge base, thereby improving the relevance and accuracy of responses. <3>

The business value of this advanced RAG system lies in its ability to transform passive data stores into active, intelligent knowledge assets. The system will enable:
* Providing fast, contextual, and accurate answers to user queries, based on organizational documents.
* Improving knowledge worker productivity by reducing time spent searching for information.
* Enabling the discovery of new insights through the synthesis of information from multiple documents and sources.
* Increasing user engagement through an intelligent and intuitive AI chat interface. The shift is not just from simple search to deep understanding, but from data storage to data leverage, potentially leading to faster decision-making, improved innovation, and better customer service, especially if the chat interface also serves external clients.

### 2.2. System Goals and Objectives

The primary goal is to develop a scalable, secure, and high-performance RAG system that ingests, analyzes, and indexes a variety of file types, and allows users to interact with this knowledge through an advanced AI chat interface.

Specific objectives to achieve this goal include:
* Support ingestion of PDF, CSV, TXT, and audio files up to 100MB in size.
* Implement robust text and metadata extraction for supported file types.
* Utilize efficient chunking and embedding strategies for optimal retrieval.
* Enable the creation and management of multiple "Knowledge Collections."
* Provide mechanisms for version control of collection configurations (system prompts, tool mappings).
* Allow users to select one or more collections for querying.
* Implement intelligent merging and/or re-ranking of context from multiple collections.
* Deliver accurate and contextually relevant responses through an AI chat interface with streaming capabilities.
* Offer traceability of AI responses back to the source segments in documents.
* Meet defined NFR targets for performance, scalability, security, and availability.
* (Optional, depending on interpretation of "advanced") Support integration with external tools via an orchestration component.

> These objectives highlight an inherent tension between flexibility (multiple collections, configurable prompts/tools) and complexity. Supporting multiple file types, large file sizes, and multiple collections introduces complexity in ingestion and retrieval pipelines. Allowing users to select multiple collections for a query requires the system to handle context merging from potentially heterogeneous sources, a non-trivial task. <4> Versioning collection configurations (prompts, tools) adds another management layer but is crucial for reproducibility and iterative improvement. <6> The "traceability" objective is key for building trust and debugging, especially in enterprise environments. The broader implication is that the HLD must not only define these features but also address how their interactions and combined complexity will be managed to ensure a robust and usable system. This points to a need for modular design with well-defined interfaces.

### 2.3. High-Level System Capabilities

The system will provide the following core capabilities:

* **File Ingestion and Analysis:**
    * Upload interface for PDF, CSV, TXT, and audio files (up to 100MB).
    * Automatic detection of file type (MIME type).
    * Checksum generation (e.g., SHA256) and duplicate file detection/handling. <1>
    * Text extraction from all supported file types.
    * Metadata extraction (standard fields like author, title, creation date, and custom/inferred metadata).
    * Transcription of audio files to text.
    * Error handling for corrupted, encrypted (password-protected), or unprocessable files.

* **Knowledge Preparation and Indexing:**
    * Chunking of extracted textual content (configurable strategies: fixed-size, recursive, semantic).
    * Generation of high-quality text embeddings using advanced models (e.g., from the Gemini family).
    * Storage of chunks and embeddings in a scalable vector database.
    * Storage of metadata in a relational or NoSQL database, linked to raw files and chunks.

* **Knowledge Collection Management:**
    * Creation, updating, and deletion of "Knowledge Collections" (logical groups of documents/data).
    * Definition of collection-specific configurations: system prompts, LLM models, embedding models, chunking strategies, and associated external tools (if relevant).
    * Version control of collection configurations.
    * Role-Based Access Control (RBAC) for managing and sharing collections among users/groups.

* **Retrieval Augmented Generation (RAG):**
    * Processing and embedding of user query.
    * Similarity search in selected Knowledge Collections within the vector database.
    * Retrieval of relevant document chunks.
    * Intelligent merging and re-ranking of context from multiple chunks/collections.
    * Enrichment of LLM prompts with retrieved context and chat history.
    * Generation of responses by a powerful Large Language Model (LLM) (e.g., Gemini, GPT-4, Claude).

* **AI Chat Interface:**
    * Web-based chat interface for user interaction.
    * Support for multi-turn conversations.
    * Management and use of chat history for contextual understanding.
    * Streaming of LLM responses for better user experience.
    * Display of source attribution for generated responses (linking back to document chunks).

* **External Tools Integration (Optional but "Advanced"):**
    * Orchestration layer allowing the LLM to invoke predefined external tools/APIs based on conversational context.
    * Secure management of tool configurations (e.g., via MCP-like JSON configurations) and access credentials.

> The described capabilities point to a highly modular system where the efficiency of each component directly impacts the overall RAG quality. For instance, poor file parsing will lead to poor chunking, which leads to poor retrieval, and ultimately, poor response generation. Inaccurate text extraction or missed metadata (e.g., from a PDF with complex tables or a poorly transcribed audio file) will cause subsequent chunking to be based on flawed data. If chunking is not context-aware (e.g., cutting a sentence mid-thought), embeddings won't accurately represent semantic meaning, leading to irrelevant chunk retrieval. If retrieval fetches irrelevant or insufficient context due to poor embeddings or indexing, the LLM won't have the necessary information to answer accurately. Even with a powerful LLM, if the augmented context is noisy or irrelevant, the generated response is likely to be off-topic, unhelpful, or a hallucination. If the chat interface doesn't manage history well or doesn't display sources clearly, user trust and usability will suffer. This interconnectedness implies that each step must be designed with high quality and robustness in mind. It also highlights the importance of end-to-end evaluation and observability to pinpoint bottlenecks or failures in any part of this chain. A failure in an early stage (like file parsing) will inevitably cascade and degrade the performance of later stages.

## 3. Requirements

### 3.1. Functional Requirements

#### 3.1.1. File Ingestion and Processing Subsystem

**FR-ING-001:** The system shall provide an API endpoint for users to upload files of supported types (PDF, CSV, TXT, Audio).
**FR-ING-002:** The system shall support uploading files up to 100MB per file.
> Handling 100MB files requires robust streaming capabilities on both client and server sides to avoid memory issues and timeouts. Chunked uploads are a recommended practice. <9> Reading a 100MB file entirely into memory before processing is not scalable and can lead to server crashes, especially with concurrent uploads. HTTP requests for large files might time out if not handled properly. Streaming allows the server to process the file in manageable segments as it arrives. This impacts the upload API design (e.g., support for multipart/form-data with streaming or dedicated chunked upload protocols like TUS) and the server-side processing service (which must be able to consume a stream).

**FR-ING-003:** The system shall automatically detect the MIME type of uploaded files. <11>
> Relying solely on file extensions is insecure and unreliable. MIME type detection using libraries like `python-magic` by inspecting file headers is more robust. Users can easily rename files with incorrect extensions. Processing a file based on a misleading extension could lead to parser errors or even security vulnerabilities (e.g., if an executable is disguised as a PDF). `python-magic` <12> checks the binary file signature (magic numbers) to determine its true type, a more reliable method. This ensures the correct parser/processor is chosen for subsequent file analysis stages.

**FR-ING-004:** The system shall calculate a checksum (e.g., SHA256) for each uploaded file for integrity verification and duplicate prevention. <1>
> SHA256 is preferred over MD5 due to its stronger collision resistance, which is vital for ensuring data integrity and reliable duplicate detection in enterprise systems. <13> MD5 has known collision vulnerabilities, meaning different files can produce the same hash, undermining duplicate detection and integrity checks. <13> SHA256 offers a much larger hash space, making accidental collisions astronomically improbable and deliberate collisions computationally infeasible with current technology. For a system handling potentially sensitive enterprise data, the stronger assurance of SHA256 is a better choice, even if slightly more computationally intensive. The HLD <1> mentions MD5 for video, but for new file types, upgrading to SHA256 is recommended.

**FR-ING-005:** The system shall implement duplicate prevention: if an uploaded file (based on checksum) already exists, the system shall link the new metadata/collection association to the existing raw file instead of storing it again. <1>
**FR-ING-006:** The system shall extract textual content from PDF files. This includes handling various PDF structures (text-based, scanned/requiring OCR - though OCR itself might be a v2 feature or require a specific tool). <15> Possible libraries: PyMuPDF (Fitz) for robust extraction from complex PDFs <15>, PDFMiner.six for layout details <15>, PyPDF2 for basic needs. <15> Tika for multiple formats and OCR. <15>
**FR-ING-007:** The system shall extract textual content from CSV files, preserving tabular structure where possible for contextual understanding. <18>
**FR-ING-008:** The system shall extract textual content from TXT files, supporting various encodings (e.g., UTF-8, ASCII). <20>
**FR-ING-009:** The system shall transcribe audio files (e.g., MP3, WAV, M4A) to text. <22>
**FR-ING-010:** The system shall extract standard metadata from PDF files (e.g., author, title, subject, keywords, creation date, modification date, producer, creator, format, encryption status). <24> PyMuPDF's `doc.metadata` provides these fields. <25>
**FR-ING-011:** The system shall extract technical metadata from audio files (e.g., duration, sample rate, bit rate, channels, codec). <28>
**FR-ING-012:** For CSV and TXT files, the system shall allow users to optionally provide or infer metadata (e.g., source, description, relevant dates, keywords), as these formats often lack embedded metadata. <29>
> Inferred and user-supplied metadata for "dumb" formats like TXT/CSV are crucial for effective RAG. RAG relies on retrieving relevant context. For TXT/CSV, the file content alone might lack sufficient context for retrieval if queries are about the data's origin or purpose. For example, a TXT file could be meeting notes, a log file, or a code snippet. Without metadata indicating its nature, it's hard to retrieve accurately for queries like "Summarize recent meeting notes." Allowing users to add tags, descriptions, or link these files to a project/source during upload (or inferring from folder structures/naming conventions) enriches the context available to the vector database's metadata filters and improves retrieval relevance. This implies the ingestion process should include steps for metadata enrichment beyond basic file properties.

**FR-ING-013:** The system shall handle password-protected PDF files by:
    * Attempting decryption with a list of common/default passwords (if configured).
    * If a UI is part of ingestion, prompting the user for a password.
    * If decryption fails, logging the error and marking the file as "unprocessed" with an appropriate status. <16> PyMuPDF `doc.is_encrypted` and `doc.authenticate(password)`. <31>
**FR-ING-014:** The system shall implement robust error handling for file processing failures (e.g., corrupted files, unsupported audio codecs, transcription service errors), log these errors, and provide clear status feedback. <33>

> The variety of file types and potential issues (encryption, corruption, size) necessitates a highly flexible and resilient ingestion pipeline. A monolithic approach to parsing/extraction is likely to fail. For example, PDFs alone have vast structural differences (text-based, image-based, complex layouts, forms, annotations). A single library might not handle all optimally. <15> Audio files can have different codecs and quality levels, affecting transcription success. <23> CSV/TXT files might have encoding issues or non-standard delimiters. Password protection <31> and file corruption are common real-world problems. Therefore, the ingestion subsystem needs a strategy for each file type, potentially involving multiple parsing/extraction libraries or services, and robust error handling at each step (e.g., try PyMuPDF for PDF; if fails and looks scanned, consider Tika with OCR; for audio, if AssemblyAI fails, log error and notify, or use a fallback). This suggests a modular design for the ingestion service, where specific handlers for file types/issues can be plugged in. It also means detailed logging and status tracking are paramount for diagnosing and resolving ingestion problems.

#### Table 2: Supported File Types and Extraction Strategy

| File Type             | Primary Text Extraction Library/Method             | Backup/Secondary Library                   | Key Metadata Fields to Extract                                                                 | Specific Error Handling Notes                                                                      |
|-----------------------|----------------------------------------------------|--------------------------------------------|------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------|
| PDF                   | PyMuPDF (Fitz) <15>                               | pdfminer.six <15>, Tika-Python (with OCR) <15> | Author, Title, Subject, Keywords, CreationDate, ModDate, Producer, Creator, Format, EncryptionStatus, PageCount <25> | Handle encrypted PDFs (attempt decryption, prompt for password, mark as unprocessable). <31> Detect scanned PDFs and route to OCR if needed. |
| CSV                   | pandas <18>, Python `csv` module <19>              | -                                          | File Name, Size, Last Modified, User-Supplied (Source, Description, Tags)                     | Handle different delimiters, encoding issues.                                                      |
| TXT                   | Python built-in file handling <20>                 | -                                          | File Name, Size, Last Modified, Encoding, User-Supplied (Source, Description, Tags)          | Detect and handle different encodings (UTF-8, ASCII, etc.).                                    |
| Audio (MP3, WAV, M4A) | AssemblyAI API <35> / OpenAI Whisper (self-hosted) <23> | - (Log error and notify)                   | Transcription (Text), Duration, Sample Rate, Bit Rate, Channels, Codec, File Name, Size <28>    | Handle API errors (4xx, 5xx codes), unsupported formats, low audio quality, rate limits. <34>      |

#### 3.1.2. Data Preparation Subsystem (Chunking, Embedding)

**FR-DP-001:** The system shall chunk extracted textual content into smaller segments suitable for embedding and retrieval. <2>
**FR-DP-002:** The system shall support configurable chunking strategies, including:
    * Fixed-size chunking (with configurable size and overlap). <38>
    * Recursive character text splitting (e.g., splitting by paragraphs, then sentences, then words, with configurable separators and size). <38>
    * Semantic chunking (grouping sentences/text based on semantic similarity). <38>
    * (Potentially) Document-specific chunking (e.g., by sections for Markdown-like structures if text extraction preserves them). <39>
**FR-DP-003:** The system shall allow configuration of chunking parameters (size, overlap, strategy) per Knowledge Collection.
> Optimal chunking often depends on the nature of the content and the expected query types. A one-size-fits-all approach is suboptimal. Dense technical documents might benefit from smaller, more granular chunks to capture specific details. Narrative texts or legal documents might require larger chunks with more overlap to preserve context and argument flow. <38> Semantic chunking might be best for documents where topics shift frequently. <40> Allowing per-collection configuration enables tailoring the chunking strategy to the specific document set in that collection, thus maximizing retrieval relevance for that collection's purpose.

**FR-DP-004:** The system shall generate high-quality text embeddings for each chunk using an advanced and configurable embedding model (e.g., Google `gemini-embedding-001`, `text-embedding-005` or similar). <41>
    * The model should be suitable for retrieval tasks (task types `RETRIEVAL_DOCUMENT` and `RETRIEVAL_QUERY` if supported by the model's API, as noted for Gemini API in <41>).
    * Models with appropriate dimensionality and context windows for the chunk sizes used should be considered. `gemini-embedding-001` offers 3072 dimensions and `text-embedding-005` (successor to `text-embedding-004`) offers 768 dimensions. <42>
**FR-DP-005:** The system shall store document chunks, their embeddings, and associated metadata (including source document ID, collection ID, chunk sequence number, original filename) in a scalable vector database. <2>
**FR-DP-006:** The system shall store comprehensive metadata about the original files and their processing status in a relational or NoSQL database, linked to the raw file storage and vector database records.

> The choice of chunking strategy and embedding model are closely intertwined and significantly impact retrieval performance. There's no single "best" for all scenarios; configurability is key. <38> Embedding models have optimal input lengths (context windows). Chunks should ideally fit within these without excessive padding or truncation. <42> Semantic chunking aims to create coherent blocks of meaning, which should lead to more distinct and representative embeddings. <38> Fixed-size chunking is simpler but may arbitrarily cut sentences or ideas, potentially harming embedding quality and retrieval relevance. <38> The chosen embedding model's ability to capture nuances in the specific domain of the documents is also critical. A general-purpose model might be less effective than a domain-adapted one if the vocabulary is highly specialized. This implies the system should not only allow configuration of these parameters but also provide guidance or defaults based on document type or collection purpose. Evaluation of different strategies will be important.

> Storing rich metadata alongside vectors in the vector database is crucial to enable effective pre-filtering or post-filtering in the retrieval process, thereby improving accuracy and efficiency. Vector search primarily finds semantically similar chunks. However, users might want to filter results based on criteria like creation date, author, source document, or specific tags associated with the document/chunk. <5> Storing this metadata directly with the chunk in the vector database (if supported) allows the database to perform filtering before or during the similarity search, which can be much more efficient than retrieving many chunks and then filtering them in the application layer. This has significant implications for the vector database schema design and the data ingestion pipeline, which must ensure this metadata is properly propagated.

#### 3.1.3. Knowledge Collection Management Subsystem

**FR-KCM-001:** Users (with appropriate permissions) shall be able to create, view, update, and delete Knowledge Collections. A collection is a logical grouping of ingested documents/data.
**FR-KCM-002:** Each Knowledge Collection shall have configurable settings, including but not limited to:
    * Collection name and description.
    * Default system prompt for RAG. <45>
    * Default LLM model for response generation.
    * Default embedding model used for documents in this collection.
    * Default chunking strategy (and its parameters like size, overlap).
    * (If relevant) Associated external tools and their configurations (e.g., `MCP.json` snippets or references). <47>
**FR-KCM-003:** The system shall support version control for Knowledge Collection configurations (system prompts, tool mappings, model choices). <6>
    * Users shall be able to view version history and revert to previous configurations.
> Version control is critical for reproducibility, A/B testing different prompts/configurations, and safe rollback if a change degrades performance. <7> RAG system performance is highly sensitive to the system prompt, LLM choice, and even chunking strategy. As users experiment to optimize a collection, they will make changes to these configurations. Without versioning, it's hard to track what changes were made, when, and by whom, making it difficult to reproduce good results or debug regressions. A version control system (even a simple one storing JSON configurations with timestamps and user details) allows for systematic experimentation (e.g., "Prompt v1 for conciseness," "Prompt v2 for detail") and the ability to revert to a known good state if a new configuration performs poorly. This is a core MLOps practice. <49>

**FR-KCM-004:** The system shall allow administrators or collection owners to manage access permissions to Knowledge Collections using Role-Based Access Control (RBAC) (e.g., who can view, query, update, delete, or share a collection). <52>
**FR-KCM-005:** Users shall be able to add ingested documents/files to one or more Knowledge Collections.
**FR-KCM-006:** Users shall be able to remove documents/files from a Knowledge Collection (this action will not necessarily delete the raw file if it's part of other collections, but will remove its chunks from the collection's queryable index).

> Collection management is the cornerstone of knowledge organization in a versatile RAG system. It allows for domain-specific tuning and access control. A single monolithic knowledge base might not be optimal if the organization deals with diverse subject areas (e.g., HR documents vs. technical manuals vs. legal contracts). Different subject areas might benefit from different system prompts (e.g., an HR bot needs a different persona than a tech support bot), different LLM models (some models are better at creative tasks, others at factual retrieval), or even different chunking strategies. Collections provide this logical separation. Per-collection RBAC <52> is essential for security and compliance, ensuring only authorized users can access or query sensitive information within specific collections. The ability to version collection configurations <7> is crucial for iterative improvement and managing changes to prompts or models over time without losing track of what worked best.

> The interaction between the collection configuration (e.g., chosen embedding model) and the documents within it is critical. Changing an embedding model for a collection would necessitate re-embedding all documents in that collection. Embeddings are model-specific. An embedding generated by model A is not meaningfully comparable for similarity with an embedding generated by model B. If a collection is configured to use `embedding-model-X`, all its documents must be chunked and embedded using `embedding-model-X`. If a user later changes the collection config to use `embedding-model-Y`, all existing documents in that collection become "stale" from an embedding perspective. The system must therefore handle this: either by disallowing embedding model changes once documents are added, or by triggering a reprocessing (re-embedding) job for all documents in the collection. The latter is more flexible but has operational implications (cost, time). This highlights the need for clear UI/UX around collection configuration and potential background task management for re-indexing.

#### Table 3: Collection Configuration Version History (Conceptual)

| collection_id (UUID) | version_id (UUID) | timestamp (TIMESTAMPTZ) | user_id_modifier (UUID) | system_prompt_snapshot (TEXT) | llm_config_snapshot (JSONB) | embedding_config_snapshot (JSONB) | chunking_config_snapshot (JSONB) | tool_config_snapshot (JSONB, if relevant) | change_notes (TEXT) |
|----------------------|-------------------|-------------------------|-------------------------|-------------------------------|-----------------------------|-----------------------------------|---------------------------------|-------------------------------------------|---------------------|
| (Example)            | (Example)         | (Example)               | (Example)               | (Example)                     | (Example)                   | (Example)                         | (Example)                       | (Example)                                 | (Example)           |
> This table provides an auditable and reproducible history of how a collection's behavior was tuned over time. It's crucial for debugging, rollback, and understanding performance changes. <7>

#### 3.1.4. Retrieval and Augmentation Subsystem

**FR-RA-001:** The system shall accept a user query (text) and selected Knowledge Collection(s) as input.
**FR-RA-002:** The system shall embed the user query using the appropriate embedding model associated with the selected collection(s). If multiple collections with different embedding models are selected, a strategy to handle this must be defined (e.g., query with each, or use a compatible model).
**FR-RA-003:** The system shall perform a similarity search (vector search) in the vector database against the selected Knowledge Collection(s) to retrieve the top-K most relevant document chunks. K shall be configurable.
**FR-RA-004:** The system shall support metadata filtering during retrieval based on user-specified criteria or implied context (e.g., filter by document source, creation date range, keywords present in metadata). <5>
**FR-RA-005:** When multiple Knowledge Collections are selected for a query, the system shall employ a strategy to merge and/or re-rank retrieved contexts from these different collections before presenting them to the LLM. Strategies may include:
    * Simple concatenation.
    * Reciprocal Rank Fusion (RRF) or other re-ranking algorithms. <56>
    * Using an LLM to select the most relevant parts from the combined context.
    * LlamaIndex approaches like `SubQuestionQueryEngine` (decomposes query into sub-queries for different sources) or `RouterQueryEngine` (selects the best source). <58>
**FR-RA-006:** The system shall enrich the prompt for the LLM with the retrieved context, chat history (if relevant), and the current user query, formatted according to the collection's system prompt. <2>
**FR-RA-007:** The system shall handle cases where no relevant context is found (e.g., inform the LLM, or reply to the user that no relevant information was found in the selected collections).

> Effective context merging from multiple diverse collections is a complex challenge. Simple concatenation can exceed context windows or introduce noise. Intelligent re-ranking or query decomposition is key for advanced RAG. <5> Different collections might contain information on different facets of a query, or even conflicting information. Concatenating all retrieved chunks from multiple collections can easily lead to a very large context that might exceed the LLM's context window limit. Even if it fits, a large, unfocused context might make it harder for the LLM to identify the most salient pieces of information (the "lost in the middle" problem - <57>). Re-ranking techniques (like RRF used in LangChain's `EnsembleRetriever` - <61>) can prioritize the most relevant chunks from the combined set. More advanced strategies like LlamaIndex's `SubQuestionQueryEngine` <58> decompose the main query into sub-queries targeted at specific collections/tools, then synthesize a final answer. This can be more effective for complex queries requiring information from multiple, distinct knowledge domains. The choice of merging strategy has significant implications for retrieval quality, LLM performance, and overall system complexity.

> The "no relevant context found" scenario is critical. The system must avoid forcing the LLM to hallucinate an answer. Inevitably, for some queries, the selected collections will not contain relevant information. If the RAG system passes an empty or irrelevant context to the LLM, the LLM might fall back to its parametric knowledge (which could be outdated or generic) or, worse, generate a plausible-sounding but incorrect answer (hallucination). The system prompt should instruct the LLM on how to behave in such cases (e.g., "If the provided context does not contain the answer, state that you do not know based on the available documents"). <62> The retrieval system itself should detect when retrieval confidence is low and potentially surface this to the user or the LLM. This is vital for maintaining user trust.

#### 3.1.5. AI Chat Interface Subsystem

**FR-AIC-001:** The system shall provide a web-based user interface for AI chat.
**FR-AIC-002:** The interface shall allow users to input text queries.
**FR-AIC-003:** The interface shall display chat history, distinguishing between user messages and AI responses. <63>
**FR-AIC-004:** The system shall manage chat session state, including conversation history. <63>
**FR-AIC-005:** The system shall use chat history to provide context for ongoing conversations, allowing for follow-up questions and contextual understanding. <60>
**FR-AIC-006:** AI responses shall be streamed to the interface to improve perceived responsiveness. <66>
**FR-AIC-007:** The interface shall display source attribution for AI-generated responses, linking back to the specific document(s) and ideally the chunk(s) from which information was derived. <65>
> Source attribution is essential for user trust, verifiability, and debugging. It allows users to explore the source material themselves. LLM responses, even when grounded by RAG, are still generated text. Users, especially in enterprise or research contexts, need to verify the source of information. Displaying links to the source documents/chunks allows users to "click through" and read the original context. This transparency builds trust in the system's responses. It also aids in debugging: if the AI provides an incorrect answer, tracing it back to the source chunk can help identify issues in the data, chunking, or retrieval. This requires the backend to pass source metadata along with the generated response to the UI.

**FR-AIC-008:** Users shall be able to select one or more Knowledge Collections to query for the current chat session.
**FR-AIC-009:** Users shall be able to start new conversations (sessions) and potentially view/resume past conversations.

> The AI chat interface is not just a presentation layer; it's an active part of the RAG process, managing session context and user intent. Its design significantly impacts usability and trust. Effective RAG requires more than single query-response. Conversations evolve, and follow-up questions depend on prior exchanges. The chat interface must manage this conversation history <63> and ensure it's passed to the RAG backend to inform query rephrasing or context augmentation. The ability to select collections (FR-AIC-008) means the interface must communicate this choice to the backend for targeted retrieval. Streaming responses (FR-AIC-006 <66>) is crucial for user experience with potentially slower LLM generation times, giving a sense of faster interaction. Displaying sources (FR-AIC-007) is fundamental for building trust and allowing users to verify information, a key differentiator for RAG versus standalone LLMs. The design of these UI/UX elements directly impacts how users can effectively leverage the underlying RAG capabilities.

#### 3.1.6. External Tools Integration Subsystem (Optional, for "Advanced" RAG)

**FR-ETI-001:** The system shall provide a mechanism to define and register external tools (e.g., APIs, functions) that the LLM can invoke. <47>
**FR-ETI-002:** Tool definitions shall include a name, description (for LLM understanding), API endpoint (if relevant), authentication method, and input/output parameters, potentially in a structured format like JSON (e.g., `mcp.json` style). <48>
**FR-ETI-003:** An orchestration component shall manage LLM requests to use tools, execute tools securely, and return results to the LLM.
**FR-ETI-004:** Tool access and invocation shall be subject to security policies and may be linked to Knowledge Collection configurations.

> Integrating external tools transforms the RAG system from a passive information retriever to an active agent capable of performing actions, significantly expanding its utility but also increasing security and orchestration complexity. <47> RAG primarily provides information to the LLM. External tools allow the LLM to act on information or retrieve real-time dynamic data not present in the static knowledge base (e.g., checking current stock price, scheduling a meeting, querying a live database). The Model Context Protocol (MCP) <47> provides a standardized way for LLMs to discover and interact with such tools. This requires a robust orchestrator to: parse the LLM's intent to use a tool, validate the request, securely call the external tool (handling authentication, input mapping), format the tool's output, and return it to the LLM. Security implications are significant: tools might access sensitive APIs or perform actions with real-world consequences. Therefore, granular control over which tools can be used, by whom, and in what context (e.g., per-collection) is essential. This capability elevates the RAG system to an "agentic RAG," <72> which is a more powerful but also more complex paradigm.

#### 3.1.7. Administration and Configuration

**FR-ADM-001:** The system shall provide an administrative interface or API for managing users and their roles/permissions.
**FR-ADM-002:** Administrators shall be able to monitor system health, view logs, and manage configurations.
**FR-ADM-003:** Administrators shall be able to manage Knowledge Collection configurations, including version control.
**FR-ADM-004:** (If multi-tenancy is implemented) Administrators shall be able to manage tenants and their isolated data/collections.

> A robust administration interface is essential for the long-term maintenance, scalability, and security of a complex RAG system. Neglecting this aspect can lead to operational nightmares. As the number of users, collections, and documents grows, manual management becomes unfeasible. Administrators need tools to onboard users, assign permissions (RBAC), and manage collection settings (prompts, models, tools). Monitoring system health (e.g., ingestion pipeline status, query latency, error rates) is crucial for proactive maintenance and troubleshooting (Observability NFRs). Versioning of configurations (FR-KCM-003) needs an interface for administrators to manage these versions. If the system is multi-tenant, tenant management and ensuring data isolation are critical admin functions. Lack of good admin tools often leads to ad-hoc fixes, security vulnerabilities, and difficulty scaling operations.

### 3.2. Non-Functional Requirements (NFRs)
Non-Functional Requirements (NFRs) define the quality attributes of the system and are crucial for user satisfaction and operational stability. <73> Document <1> provides specific examples for a data management system, which will be adapted here.

#### 3.2.1. Performance and Latency

**NFR-PERF-001 (File Ingestion Speed):** Average time to process and index a new file (text extraction, chunking, embedding) shall be < X seconds per MB of text content (target for benchmark).
**NFR-PERF-002 (Query Preprocessing):** Time to embed a user query and perform initial metadata filtering shall be < Y milliseconds (P95).
**NFR-PERF-003 (Context Retrieval Latency):** Time to retrieve the top-K relevant chunks from the vector database for a typical query shall be < Z milliseconds (P95). <76> suggests < 500-1000ms; <77> notes MyScaleDB achieves an average of 18ms.
**NFR-PERF-004 (LLM First Token Latency):** Time to receive the first token of a streamed AI response after query submission shall be < A seconds (P95).
**NFR-PERF-005 (LLM Full Response Latency):** End-to-end latency for a typical AI chat query (from user submission to full response display) shall be < B seconds (P95). <76> suggests 1-2 seconds total for RAG.
**NFR-PERF-006 (Concurrent Queries):** The system shall support at least N concurrent chat queries per second without significant degradation in response latency.
**NFR-PERF-007 (UI Responsiveness):** Chat interface interactions (sending messages, scrolling history) shall feel instantaneous (<200ms response).

> RAG pipeline latency is additive. Each stage (query embedding, retrieval, LLM generation, network) contributes. Optimizing the slowest stages (often retrieval and LLM generation) is critical. <76> User query embedding is typically fast. Retrieval latency from a vector database depends on index size, query complexity, and hardware; it can be a bottleneck. <76> Passing context to the LLM and waiting for generation is often the most time-consuming part, especially for complex prompts or larger models. Streaming responses (NFR-PERF-004) mitigates perceived LLM generation latency by showing partial results quickly. Therefore, performance NFRs should be set for individual stages as well as end-to-end to identify and address bottlenecks effectively. Focusing only on end-to-end latency can hide problems in intermediate steps.

#### Table 4: Performance NFR Targets

| NFR ID        | Description                             | Target             | Percentile |
|---------------|-----------------------------------------|--------------------|------------|
| NFR-PERF-001  | File Ingestion Speed (seconds/MB text)  | < 5 (initial target) | Average    |
| NFR-PERF-002  | Query Preprocessing (ms)                | < 100              | P95        |
| NFR-PERF-003  | Context Retrieval Latency (ms)          | < 750              | P95        |
| NFR-PERF-004  | LLM First Token Latency (s)             | < 1.5              | P95        |
| NFR-PERF-005  | LLM Full Response Latency (s)           | < 3.0              | P95        |
| NFR-PERF-006  | Concurrent Queries (QPS)                | 50                 | -          |
| NFR-PERF-007  | UI Responsiveness (ms)                  | < 200              | P95        |

#### 3.2.2. Scalability and Capacity

**NFR-SCAL-001 (Data Volume):** The system shall be designed to store and manage up to X Terabytes of raw file data and Y Billion vector embeddings (inspired by <1>).
**NFR-SCAL-002 (Number of Collections):** The system shall support up to M Knowledge Collections.
**NFR-SCAL-003 (Documents per Collection):** Each collection shall support up to P documents.
**NFR-SCAL-004 (Concurrent Users):** The system shall support up to Q concurrent active users. <73>
**NFR-SCAL-005 (Ingestion Throughput):** The system shall support ingestion of at least R files per hour during peak load (inspired by <1>).
**NFR-SCAL-006 (Horizontal Scalability):** All core components (ingestion services, vector database, chat API, LLM service if self-hosted) shall be designed for horizontal scalability to handle increasing load by adding more resources/nodes. <1>
**NFR-SCAL-007 (Storage Expansion):** The system shall support seamless addition of storage capacity for raw files, metadata, and vector data without service interruption.

> Scalability for a RAG system has multiple dimensions: data volume (number and size of documents), number of users, query throughput, and ingestion rate. Each requires different architectural considerations. Scaling data volume impacts vector database size and indexing performance; sharding or distributed vector databases might be needed. <1> Scaling concurrent users and query throughput impacts the API gateway, chat service instances, and potentially the LLM serving infrastructure (if not using a third-party API with its own scalability). Scaling ingestion rate impacts the file processing pipeline, embedding generation (which can be GPU-intensive), and write throughput to databases. A design that scales well in one dimension (e.g., data volume) might not scale well in another (e.g., concurrent users) if not considered holistically. Horizontal scalability for all stateful and stateless components is a key principle. <1>

#### 3.2.3. Availability and Reliability

**NFR-AVAIL-001 (System Uptime):** Core chat and retrieval services shall have an uptime of at least 99.9% per month, excluding planned maintenance. <1>
**NFR-AVAIL-002 (Data Durability):** Stored raw files, metadata, and vector embeddings shall have a data durability of 99.9999% or higher. <1>
**NFR-AVAIL-003 (Fault Tolerance):** The system shall be resilient to single points of failure in critical components. Redundancy and failover mechanisms shall be in place. <1>
**NFR-AVAIL-004 (Backup and Recovery):**
    * RPO (Recovery Point Objective): Maximum acceptable data loss shall be 1 hour for metadata and chat history, 24 hours for vector indexes (rebuildable) (RPO examples from <1>).
    * RTO (Recovery Time Objective): Time to restore core services after a major failure shall be < 4 hours (RTO examples from <1>).
    * Regular automated backups for metadata, chat history, and collection configurations. Vector indexes can be rebuilt from source data and embeddings if necessary, but snapshots can reduce RTO.
**NFR-AVAIL-005 (Graceful Degradation):** In case of partial system failure (e.g., one external tool unavailable), the system should degrade gracefully, possibly offering reduced functionality instead of a complete outage.

> High availability for a RAG system depends on the availability of all its critical dependencies: data stores, embedding services, LLM services, and its own components. Failure in any can impact the end-user. The vector database must be highly available for retrieval. The LLM service (whether self-hosted or third-party) must be available for generation. The metadata store and chat history database must be available. Ingestion pipeline components must be reliable, though some asynchronous processing can tolerate transient failures. Achieving 99.9% uptime requires redundancy at multiple levels: infrastructure (e.g., multiple availability zones), application instances (e.g., multiple chat service pods), and data (e.g., replicated databases). RPO/RTO for vector data can be more relaxed if fully reconstructible from source files and metadata, but this reconstruction can be time-consuming, impacting RTO. Balancing backup cost vs. RTO is key.

#### 3.2.4. Security and Access Control

**NFR-SEC-001 (Authentication):** All user access to the system (UI, API) shall require strong authentication (e.g., OAuth 2.0, OpenID Connect). API access to services shall use secure tokens/keys. <1>
**NFR-SEC-002 (Authorization):** Role-Based Access Control (RBAC) shall be implemented to manage user permissions for:
    * Access to specific Knowledge Collections. <52>
    * Management (CRUD) of Knowledge Collections.
    * Administrative functions.
    * Accessing/invoking external tools (if relevant).
**NFR-SEC-003 (Data Encryption):**
    * Data at Rest: All sensitive stored data (raw files, metadata, embeddings, chat history, configurations) shall be encrypted using strong encryption algorithms (e.g., AES-256). <1>
    * Data in Transit: All communication between system components and with users/external services shall use TLS 1.3 or higher. <1>
**NFR-SEC-004 (Input Validation and Output Sanitization):** The system shall validate all user inputs to prevent injection attacks and sanitize outputs from the LLM to mitigate risks of harmful content or script injection if rendered in a web context. <46>
**NFR-SEC-005 (Audit Logging):** Security-relevant events (logins, access attempts, configuration changes, data deletion) shall be logged for auditing and intrusion detection. <1>
**NFR-SEC-006 (Data Isolation in Multi-tenancy - if relevant):** If the system is designed for multi-tenancy, strict data isolation between tenants must be enforced at all layers (storage, retrieval, processing). <54> Vector databases like Qdrant <78> and Pinecone <79> offer namespace/payload-based isolation. PostgreSQL can use RLS. <54>
**NFR-SEC-007 (Dependency Security):** Third-party libraries and dependencies shall be regularly scanned for vulnerabilities, and patches applied promptly.

> Security in RAG systems is multifaceted, encompassing not only traditional data security but also prompt security (injection attacks) and ensuring the LLM doesn't inadvertently leak sensitive information from context. Standard security practices (authentication, authorization, encryption) are fundamental. <1> RAG introduces new attack surfaces. A malicious user might try to craft queries (prompts) to trick the LLM into revealing sensitive information from retrieved documents they aren't authorized to see directly, or to cause the LLM to perform harmful actions if tool integration exists. <46> Therefore, RBAC for collections (NFR-SEC-002) is critical to ensure the retrieval step only fetches data the user is authorized to access. Input validation must check for prompt injection patterns. Output sanitization is needed if LLM responses are rendered as HTML. If multi-tenancy is a requirement, ensuring strict data isolation in the vector database <78> and metadata stores is paramount to prevent data leakage between tenants; this impacts schema design and query logic.

#### 3.2.5. Data Integrity and Consistency

**NFR-DI-001 (Metadata Accuracy):** Metadata extracted from files shall accurately reflect file content and properties.
**NFR-DI-002 (Embedding Consistency):** The same text chunk, processed with the same embedding model and parameters, shall always produce the same embedding vector.
**NFR-DI-003 (Link Integrity):** Links between raw files, metadata records, vector chunks, and chat history shall be consistently maintained. Deleting a source document should trigger appropriate cleanup or marking of related chunks/embeddings.
**NFR-DI-004 (Transactional Updates - Metadata):** Updates to critical metadata (e.g., collection configurations, user permissions) should be transactional to ensure consistency (ACID properties of <1> for metadata).

> Data integrity in RAG systems isn't just about database transactions; it's about the consistency of the entire data lifecycle from raw file to generated response. Inconsistencies can lead to irrelevant retrieval or incorrect answers. If metadata is incorrect (e.g., wrong author, date), filtering based on it will fail. If embeddings are inconsistent for the same content, similarity search becomes unreliable. If a raw file is deleted but its chunks remain in the vector DB, the system might retrieve context for a non-existent document, leading to user confusion or errors when trying to view the source. This implies a need for robust data management processes, including potential periodic checks or reconciliation tasks, especially for orphaned data.

#### 3.2.6. Maintainability and Extensibility

**NFR-MAIN-001 (Modularity):** The system shall be designed with modular components and well-defined APIs to facilitate independent development, testing, and updates.
**NFR-MAIN-002 (Code Quality):** Code shall adhere to defined coding standards, be well-documented, and have high unit test coverage.
**NFR-MAIN-003 (Configuration Management):** System configurations (e.g., service endpoints, model parameters, default prompts) shall be externalized and manageable without code changes. <7>
**NFR-MAIN-004 (Extensibility - New File Types):** The architecture shall allow for the addition of new file type processors with minimal impact on existing components.
**NFR-MAIN-005 (Extensibility - New Models):** The system should make it relatively easy to integrate and switch between different embedding or LLM models.

> The rapid evolution of LLMs and embedding models means model agility (ease of swapping models) is a critical factor for long-term maintainability and performance. New, better, or more cost-effective LLMs and embedding models are constantly being released. A RAG system tightly coupled to one specific model will quickly become outdated or suboptimal. The design should abstract the model interaction layer (e.g., using libraries like LangChain or LlamaIndex that support multiple providers, or through internal adapter interfaces). This allows the system to upgrade models with minimal code changes, facilitating continuous improvement and adaptation to the evolving AI landscape. This also ties into versioning of collection configurations (FR-KCM-003) where model choice is a key parameter.

#### 3.2.7. Observability and Monitoring

**NFR-OBS-001 (Comprehensive Logging):** All system components shall generate structured logs for requests, errors, and significant events. Logs should be centralized and searchable.
**NFR-OBS-002 (Metrics Collection):** The system shall expose key performance and operational metrics for monitoring. This includes:
    * Ingestion pipeline: Files processed, errors, time per stage.
    * Retrieval: Query latency, number of chunks retrieved, hit rate (if ground truth exists).
    * Generation: LLM response latency, token counts (prompt & completion), LLM error rates.
    * End-to-end: Overall query latency, user satisfaction scores (if collected).
    * Resource utilization: CPU, memory, disk, network for all services.
    * <80> (W&B metrics) <1> (monitoring requirements).
**NFR-OBS-003 (Distributed Tracing):** Distributed tracing shall be implemented across microservices to track requests through the entire RAG pipeline, aiding in performance analysis and debugging.
**NFR-OBS-004 (Alerting):** Alerts shall be configured for critical errors, performance degradation, and resource exhaustion.
**NFR-OBS-005 (RAG-Specific Quality Metrics - Advanced):**
    * Retrieval: Precision@k, Recall@k, Mean Reciprocal Rank (MRR) for retrieved chunks (requires evaluation datasets).
    * Generation: Faithfulness (consistency with retrieved context), Answer Relevance (to the query), Absence of Hallucinations (may require human or model-based evaluation). <77>

> Observability for RAG systems goes beyond typical application monitoring. It requires tracking the quality and effectiveness of each stage in the RAG pipeline (retrieve, augment, generate) to understand and improve AI performance. <72> Standard metrics like latency and error rates are important (NFR-OBS-002). However, for a RAG system, knowing *why* a response was good or bad is critical. Was retrieval poor? Did the LLM ignore good context? This demands RAG-specific metrics (NFR-OBS-005): retrieval effectiveness (e.g., did we get the right chunks?), generation quality (e.g., did the LLM use the chunks faithfully? Was the answer relevant?). Tools like Weights & Biases (W&B) Prompts/Weave <80> are designed for this kind of LLM/RAG observability, allowing tracking of inputs/outputs at each stage and evaluation against custom evaluators. Implementing this level of observability is key to iterative improvement, debugging complex issues (like hallucinations), and building trust in the AI's outputs. It also aids in cost tracking by monitoring token usage. <81>

#### 3.2.8. Data Retention and Compliance

**NFR-DRC-001 (Data Retention Policy):** The system shall support configurable retention periods for raw files, metadata, embeddings, and chat history to meet organizational policies or legal requirements (document <1> mentions 180-day retention).
**NFR-DRC-002 (Data Deletion):** The system shall provide automated mechanisms for deleting data that has exceeded its retention period. Deletion should be auditable. <1>
**NFR-DRC-003 (Compliance):** System design and operation shall consider relevant data privacy regulations (e.g., GDPR, CCPA) if handling personal or sensitive information.

> Data retention in RAG systems is complex due to the interconnectedness of data (raw files, chunks, embeddings, metadata, chat history). A simple deletion of a raw file needs to propagate correctly. If a raw file is deleted due to retention policy, its corresponding chunks in the vector DB and its metadata records must also be deleted or marked as stale to prevent retrieval of context from non-existent sources. Chat history might refer to AI responses generated from now-deleted documents. The system needs a strategy for handling this (e.g., indicating the source is no longer available, or deleting chat history linked to deleted documents if required). Automated and auditable deletion mechanisms are essential for compliance and managing storage costs. The partitioning strategy for deletion mentioned in <1> is a good example for efficient deletion.

## 4. High-Level System Design

### 4.1. Architectural Overview

The system architecture will be based on a modular approach, composed of distinct logical services communicating with each other through well-defined APIs. This approach promotes scalability, maintainability, and fault tolerance.

* **Conceptual Architecture:**
    A conceptual flow diagram will illustrate the main functional blocks: File Ingestion, Data Preparation, Knowledge Management, Retrieval & Augmentation, AI Chat Interface, External Tools (optional), and Admin Interface. The diagram will depict high-level interactions between these blocks.

* **Logical Architecture (Microservices):**
    The system will be decomposed into logical services, each responsible for a specific functional domain. Examples of such services include:
    * **File Upload Service:** Responsible for receiving files from the user and initial validation.
    * **File Processing Service:** Orchestrates the extraction, chunking, and embedding processes.
    * **Text Extraction Service(s):** Specific handlers for PDF, DOCX, TXT, CSV.
    * **Audio Transcription Service:** Interface to external or internal transcription services.
    * **Chunking Service:** Implements various chunking strategies.
    * **Embedding Service:** Creates embeddings using selected models.
    * **Vector Store Service:** Abstracts interactions with the vector database.
    * **Metadata Service:** Manages the metadata database.
    * **Collection Management Service:** Handles CRUD operations for collections and their configurations.
    * **RAG Core Service:** Orchestrates query processing, retrieval, context augmentation, and LLM interaction.
    * **Chat Service/API:** Manages chat sessions, history, and user interactions.
    * **Tool Orchestration Service:** (If ETI is included) Manages invocation of external tools.
    * **API Gateway:** Single entry point for UI and external clients.

> A microservices-based logical architecture offers better scalability, maintainability, and fault isolation for a complex RAG system compared to a monolithic architecture. The system has diverse functionalities (file processing, embedding, vector search, LLM interaction, chat management) with potentially different scaling needs and technology choices. For example, file processing and embedding can be resource-intensive (CPU/GPU) and may need to scale independently from the chat interface or metadata service. A microservices approach allows each service to be developed, deployed, and scaled independently. If one service fails (e.g., audio transcription), it ideally shouldn't bring down the entire system (e.g., users can still chat with existing text-based collections). This modularity also makes it easier to update or replace individual components (e.g., swapping out an embedding model or vector database) with less risk to the overall system.

* **Physical Architecture:**
    Will illustrate the deployment of components across infrastructure (e.g., Kubernetes clusters, managed cloud services like S3, RDS/PostgreSQL, managed vector databases, LLM APIs). The diagram will show data flow between physical components (inspired by physical diagram from <1>).

* **Layered Architecture:**
    Description of distinct layers in the system:
    * **Presentation Layer:** AI Chat Interface, Admin Interface.
    * **Application Layer:** API Gateway, Chat Service, RAG Core Service, Collection Management Service.
    * **Processing Layer:** File Processing Services, Chunking, Embedding.
    * **Data Layer:** Raw File Storage, Metadata Database, Vector Database, Chat History Database.

### 4.2. Core System Components

Details of each logical service identified in section 4.1 will include:

* **File Upload Service:**
    * **Purpose:** Handle file ingestion from users and perform initial validation.
    * **Key Functionality:** Receive files via API, validate file size and initial type, transfer files to temporary/permanent storage.
    * **Inputs:** HTTP POST requests with file data (e.g., `multipart/form-data`).
    * **Outputs:** File ID or reference to stored file, upload status.
    * **Key Dependencies:** Raw file storage, File Processing Service.

* **File Processing Service:**
    * **Purpose:** Orchestrate text/metadata extraction, chunking, and embedding of uploaded files.
    * **Key Functionality:** Receive file reference from upload service, route to appropriate text/audio extractor, send extracted content to chunking service, send chunks to embedding service, coordinate storage of results.
    * **Inputs:** File reference (e.g., S3 path), collection ID, processing parameters.
    * **Outputs:** Status updates, processed chunks with embeddings, metadata.
    * **Key Dependencies:** Text Extraction Services, Audio Transcription Service, Chunking Service, Embedding Service, Vector Store Service, Metadata Service, Message Queue (e.g., Kafka, RabbitMQ) for asynchronous coordination.

* **Text Extraction Service(s):**
    * **Purpose:** Extract raw textual content from various file types (PDF, CSV, TXT).
    * **Key Functionality:** Parse file structure, use appropriate libraries (PyMuPDF, pandas) for text extraction, handle different encodings.
    * **Inputs:** File reference, file type.
    * **Outputs:** Extracted textual content, basic metadata (e.g., page count in PDF).
    * **Key Dependencies:** Raw file storage.

* **Audio Transcription Service:**
    * **Purpose:** Convert audio content to text.
    * **Key Functionality:** Send audio file to transcription API (AssemblyAI, Whisper), receive and process transcription results.
    * **Inputs:** Audio file reference.
    * **Outputs:** Transcribed text, transcription metadata (e.g., confidence levels).
    * **Key Dependencies:** Raw file storage, external/internal transcription API service.

* **Chunking Service:**
    * **Purpose:** Divide long text into smaller segments suitable for embedding.
    * **Key Functionality:** Implement various chunking strategies (fixed-size, recursive, semantic) according to configuration.
    * **Inputs:** Text, chunking parameters (size, overlap, strategy).
    * **Outputs:** List of text chunks.
    * **Key Dependencies:** -

* **Embedding Service:**
    * **Purpose:** Generate vector representations (embeddings) for text chunks.
    * **Key Functionality:** Call selected embedding model API (e.g., Gemini API) with text chunks, receive embedding vectors.
    * **Inputs:** List of text chunks, embedding model name.
    * **Outputs:** List of embedding vectors.
    * **Key Dependencies:** External/internal embedding model API service.

* **Vector Store Service:**
    * **Purpose:** Abstract interactions with the vector database for storing and retrieving embeddings.
    * **Key Functionality:** Add vectors and metadata, perform similarity searches, delete vectors.
    * **Inputs:** Embedding vectors, metadata, search queries.
    * **Outputs:** Search results, operation status.
    * **Key Dependencies:** Vector database (e.g., Qdrant, Pinecone).

* **Metadata Service:**
    * **Purpose:** Manage metadata related to files, chunks, and collections in a dedicated database.
    * **Key Functionality:** CRUD operations on metadata records, ensure link integrity.
    * **Inputs:** Metadata, metadata queries.
    * **Outputs:** Metadata records, operation status.
    * **Key Dependencies:** Relational database (e.g., PostgreSQL).

* **Collection Management Service:**
    * **Purpose:** Handle creation, update, deletion, and configuration management of Knowledge Collections.
    * **Key Functionality:** CRUD for collections, version control of collection configurations (prompts, models), RBAC permission management.
    * **Inputs:** Collection management requests, configuration data.
    * **Outputs:** Collection details, operation status.
    * **Key Dependencies:** Metadata Service, Collection configuration store.

* **RAG Core Service:**
    * **Purpose:** Orchestrate the full RAG query-response process.
    * **Key Functionality:** Receive user query, embed query, retrieve context from multiple collections, merge/rerank context, enrich prompt for LLM, call LLM, process LLM response.
    * **Inputs:** User query, selected collection IDs, chat history.
    * **Outputs:** AI response (possibly streamed), source attribution information.
    * **Key Dependencies:** Embedding Service, Vector Store Service, Metadata Service, LLM Service, Collection Management Service (for configurations).

* **Chat Service/API:**
    * **Purpose:** Manage chat sessions, conversation history, and interactions with the UI.
    * **Key Functionality:** Create sessions, store messages, retrieve chat history, pass queries to RAG Core Service, stream responses to UI.
    * **Inputs:** User messages, session IDs.
    * **Outputs:** AI messages, chat history.
    * **Key Dependencies:** RAG Core Service, Chat history database.

* **API Gateway:**
    * **Purpose:** Unified and secure entry point for all client requests (UI, external services).
    * **Key Functionality:** Request routing, authentication, rate limiting, logging.
    * **Inputs:** HTTP requests from clients.
    * **Outputs:** HTTP responses from backend services.
    * **Key Dependencies:** All backend services.

> The interfaces and contracts between these core components are critical. Well-defined APIs (e.g., using OpenAPI for REST or gRPC for internal services) are essential for decoupling and independent evolution. In a microservices architecture, components communicate over a network using APIs. If these API contracts are not clearly defined and versioned, changes in one service can easily break dependent services. Using standards like OpenAPI allows for clear documentation, client/server code generation, and easier testing of inter-service communication. This disciplined approach to interface design is crucial for managing the complexity of a system with many moving parts and ensuring maintainability as the system evolves.

### 4.3. Data Models and Storage

#### 4.3.1. Raw File Storage

* **Technology:** Object storage (e.g., AWS S3, Google Cloud Storage, MinIO).
* **Structure:** Organized by tenant ID (if multi-tenant), then possibly by collection ID or original upload batch.
* **Access Control:** Permissions managed via IAM roles/policies or pre-signed URLs for secure, temporary access by processing services.
* **Versioning:** Object versioning will be enabled for recovery and audit. Document <1> mentions S3/Glacier for cold storage, implying object storage use for large files. <1>

#### 4.3.2. Metadata Database Schema

* **Technology:** PostgreSQL (recommended for relational integrity, JSONB support, and full-text search capabilities for metadata fields). <1> uses PostgreSQL for variable metadata with ACID properties.
* **Key Tables (Conceptual - to be detailed with fields, types, indexes):**
    * `Files`: `file_id` (PK), `original_filename`, `system_filename` (e.g., S3 key), `mime_type`, `size_bytes`, `checksum_sha256`, `upload_timestamp`, `uploader_user_id`, `processing_status` (e.g., pending, processed, error), `error_message`.
    * `File_Metadata_Extracted`: `metadata_id` (PK), `file_id` (FK), `metadata_key` (e.g., "author", "title", "audio_duration"), `metadata_value_text`, `metadata_value_numeric`, `metadata_value_datetime`. (Flexible schema for diverse metadata).
    * `File_Collection_Links`: `link_id` (PK), `file_id` (FK), `collection_id` (FK). (Many-to-many relationship).

> A flexible schema for `File_Metadata_Extracted` (e.g., key-value store or using JSONB in PostgreSQL) is important to accommodate diverse and evolving metadata from different file types without requiring frequent schema migrations. PDF files have a standard set of metadata fields (author, title, etc. - <25>). Audio files have technical metadata (duration, bitrate - <28>). CSV/TXT files might have user-defined metadata (source, project, etc.). Trying to create a rigid table with columns for every possible metadata field would be unmanageable and require constant schema changes as new file types or metadata requirements emerge. A key-value structure (as in `File_Metadata_Extracted`) or a JSONB column in the `Files` table allows storing arbitrary metadata fields without altering the table structure. This improves extensibility and maintainability.

#### 4.3.3. Vector Database Schema and Indexing Strategy

* **Technology:** Qdrant, Pinecone, Weaviate, or PostgreSQL with `pgvector`. <54>
* **Structure:** Typically a single "collection" or "index" per RAG system Knowledge Collection, or use of namespaces/payload-based filtering for multi-tenancy within a larger vector DB collection.
* **Vector Record/Point Schema:**
    * `chunk_id` (PK for the vector record).
    * `vector` (the dense embedding).
    * `payload/metadata` (JSON object):
        * `original_document_id` (FK to Files table).
        * `knowledge_collection_id` (FK to Knowledge_Collections table).
        * `text_chunk` (actual text content of the chunk).
        * `chunk_sequence_number` (order within the document).
        * `source_filename`.
        * Additional filterable metadata (e.g., `creation_date_doc`, `author_doc`, custom tags from `File_Metadata_Extracted`).
* **Indexing Strategy:** HNSW or IVF_FLAT are common for Approximate Nearest Neighbor (ANN) search. Parameters (e.g., `m`, `ef_construction` for HNSW) will be tuned for speed vs. recall. Metadata fields used for filtering should be indexed if the vector DB supports it.

> The metadata stored alongside vectors in the vector database is as important as the vectors themselves for effective RAG, enabling hybrid search (semantic + keyword/metadata filtering). Vector search primarily finds semantically similar chunks. However, users often need to narrow down searches based on factual criteria (e.g., "find documents about X created last month by author Y"). Storing rich metadata (`original_document_id`, `creation_date_doc`, `author_doc`, `custom_tags`) directly in the vector DB's payload allows these filters to be applied efficiently during the search query. <5> This "hybrid search" capability significantly improves retrieval relevance and user experience compared to pure vector similarity search alone. This means the ingestion pipeline must be diligent in propagating all relevant metadata from `Files` and `File_Metadata_Extracted` tables to the vector DB payload.

#### 4.3.4. Chat History Database Schema (with Context Tracking)

* **Technology:** PostgreSQL (leveraging its relational capabilities and JSONB for flexibility).
* **Key Tables:**
    * `Users`: `user_id` (PK, UUID), `username` (VARCHAR, UNIQUE), `email` (VARCHAR, UNIQUE), `created_at` (TIMESTAMPTZ).
    * `Conversations`: `conversation_id` (PK, UUID), `user_id` (FK to Users), `title` (VARCHAR, optional, can be auto-generated), `created_at` (TIMESTAMPTZ), `last_updated_at` (TIMESTAMPTZ), `active_collection_ids` (ARRAY of UUIDs or JSONB, representing collections selected for this conversation).
    * `Messages`: `message_id` (PK, UUID), `conversation_id` (FK to Conversations), `parent_message_id` (FK to Messages, NULLABLE, for accurate turn threading/ordering), `sender_type` (ENUM: 'USER', 'AI', 'SYSTEM'), `content` (TEXT), `timestamp` (TIMESTAMPTZ).
    * `AI_Message_Context_Sources`: `context_source_id` (PK, BIGSERIAL or UUID), `ai_message_id` (FK to Messages where sender_type='AI'), `knowledge_collection_id` (FK to Knowledge_Collections), `source_document_id` (TEXT, reference to `Files.file_id`), `chunk_id_or_reference` (TEXT, specific ID from vector DB or offset), `retrieved_text_preview` (TEXT, optional snippet of the chunk), `relevance_score` (FLOAT, optional relevance score from retrieval).
* **Indexes:** On foreign keys, timestamps, `user_id` in `Conversations`, `conversation_id` in `Messages`. Full-text search index on `Messages.content`. Indexes on `AI_Message_Context_Sources` for `ai_message_id`, `source_document_id`.
* <84> shows a basic SQL schema for conversations and messages. <64> discusses chat history conceptually.

> The `AI_Message_Context_Sources` table is the linchpin for traceability and explainability in the RAG system. It directly links an AI's utterance to the specific pieces of knowledge it "read." A key requirement for enterprise RAG is understanding *why* the AI said what it said. This table provides that audit trail. For each AI message, `AI_Message_Context_Sources` can be queried to find all document chunks (from specific collections, original documents, and chunk IDs) that were retrieved and fed to the LLM to generate that response. This is invaluable for: debugging (if AI gives a wrong answer, were retrieved chunks irrelevant or did LLM misinterpret good context?), compliance/audit (demonstrating AI responses are based on approved knowledge sources), user trust (allowing users, perhaps via UI, to see the sources), and feedback loop (identifying frequently retrieved but unhelpful chunks, or documents that often lead to good/bad answers, which can inform content curation or prompt tuning). The design of this table (linking `ai_message_id` to multiple source chunk identifiers) is critical. Storing `retrieved_text_preview` can also be useful for quick inspection without re-fetching from the vector DB.

#### Table 5: Example Database Schema for Chat History and Context Tracking (PostgreSQL)

| Table                       | Column                    | Data Type     | Constraints                                          | Notes                                                       |
|-----------------------------|---------------------------|---------------|------------------------------------------------------|-------------------------------------------------------------|
| `Users`                     | `user_id`                 | UUID          | PRIMARY KEY                                          | Unique user identifier                                      |
|                             | `username`                | VARCHAR(255)  | UNIQUE, NOT NULL                                     | Username                                                    |
|                             | `email`                   | VARCHAR(255)  | UNIQUE, NOT NULL                                     | Email address                                               |
|                             | `created_at`              | TIMESTAMPTZ   | DEFAULT CURRENT_TIMESTAMP                            | Creation timestamp                                          |
| `Knowledge_Collections`     | `collection_id`           | UUID          | PRIMARY KEY                                          | Unique collection identifier                                |
|                             | `name`                    | VARCHAR(255)  | UNIQUE, NOT NULL                                     | Collection name                                             |
|                             | `description`             | TEXT          |                                                      | Collection description                                      |
|                             | `owner_user_id`           | UUID          | FOREIGN KEY (`Users`)                                | User ID of the creator                                      |
|                             | `created_at`              | TIMESTAMPTZ   | DEFAULT CURRENT_TIMESTAMP                            | Collection creation timestamp                             |
|                             | `current_version_id`      | UUID          | FOREIGN KEY (`Collection_Versions`), NULLABLE        | ID of the active configuration version                      |
| `Collection_Versions`       | `version_id`              | UUID          | PRIMARY KEY                                          | Unique configuration version identifier                     |
|                             | `collection_id`           | UUID          | FOREIGN KEY (`Knowledge_Collections`), NOT NULL        |                                                             |
|                             | `version_number`          | INTEGER       | NOT NULL                                             | Incrementing version number                                 |
|                             | `system_prompt`           | TEXT          |                                                      | System prompt for LLM                                       |
|                             | `llm_model_name`          | VARCHAR(255)  |                                                      | LLM model name                                              |
|                             | `llm_parameters`          | JSONB         |                                                      | LLM model parameters                                        |
|                             | `embedding_model_name`    | VARCHAR(255)  |                                                      | Embedding model name                                        |
|                             | `chunking_strategy`       | VARCHAR(50)   |                                                      | Chunking strategy                                           |
|                             | `chunking_parameters`     | JSONB         |                                                      | Chunking parameters                                         |
|                             | `tool_config_ids`         | UUID[]        |                                                      | Array of associated tool IDs (if any)                       |
|                             | `created_at`              | TIMESTAMPTZ   | DEFAULT CURRENT_TIMESTAMP                            |                                                             |
|                             | `creator_user_id`         | UUID          | FOREIGN KEY (`Users`)                                |                                                             |
|                             | `version_notes`           | TEXT          |                                                      | Notes about changes in this version                         |
| `Conversations`             | `conversation_id`         | UUID          | PRIMARY KEY                                          | Unique conversation identifier                              |
|                             | `user_id`                 | UUID          | FOREIGN KEY (`Users`), NOT NULL                      | User ID managing the conversation                           |
|                             | `title`                   | VARCHAR(512)  |                                                      | Conversation title (can be auto-generated)                |
|                             | `created_at`              | TIMESTAMPTZ   | DEFAULT CURRENT_TIMESTAMP                            |                                                             |
|                             | `last_updated_at`         | TIMESTAMPTZ   | DEFAULT CURRENT_TIMESTAMP                            |                                                             |
|                             | `active_collection_ids`   | UUID[]        |                                                      | Array of collection IDs selected for this conversation      |
| `Messages`                  | `message_id`              | UUID          | PRIMARY KEY                                          | Unique message identifier                                   |
|                             | `conversation_id`         | UUID          | FOREIGN KEY (`Conversations`), NOT NULL              |                                                             |
|                             | `parent_message_id`       | UUID          | FOREIGN KEY (`Messages`), NULLABLE                   | Allows message threading in a turn                          |
|                             | `sender_type`             | VARCHAR(10)   | CHECK (`sender_type` IN ('USER', 'AI', 'SYSTEM')), NOT NULL | Who sent the message                                        |
|                             | `content`                 | TEXT          | NOT NULL                                             | Message content                                             |
|                             | `timestamp`               | TIMESTAMPTZ   | DEFAULT CURRENT_TIMESTAMP                            |                                                             |
| `AI_Message_Context_Sources`| `context_source_id`       | BIGSERIAL     | PRIMARY KEY                                          | Unique context link identifier                              |
|                             | `ai_message_id`           | UUID          | FOREIGN KEY (`Messages`), NOT NULL                   | ID of the AI message that used this context                 |
|                             | `knowledge_collection_id` | UUID          | FOREIGN KEY (`Knowledge_Collections`), NOT NULL        | ID of the collection from which context was taken           |
|                             | `source_document_id`      | TEXT          | NOT NULL                                             | Original document ID (e.g., `Files.file_id`)                |
|                             | `chunk_id_or_reference`   | TEXT          | NOT NULL                                             | Specific chunk ID from vector DB                            |
|                             | `retrieved_text_preview`  | TEXT          |                                                      | Preview of text from the chunk (optional)                   |
|                             | `relevance_score`         | FLOAT         |                                                      | Relevance score of the chunk (optional)                     |

**Search and Filtering Capabilities Supported by This Schema:**
* **By User:** Conversations and messages can be filtered by `Users.user_id` or `Users.username`.
* **By Date Range:** Conversations and messages can be filtered by `Conversations.created_at`, `Conversations.last_updated_at`, or `Messages.timestamp`.
* **By Keywords in Messages:** A full-text search index on `Messages.content` can be used to find conversations/messages containing specific keywords.
* **By Context Source:** All AI messages that used context from a specific document (`AI_Message_Context_Sources.source_document_id`), a specific collection (`AI_Message_Context_Sources.knowledge_collection_id`), or even a specific chunk (`AI_Message_Context_Sources.chunk_id_or_reference`) can be located. This allows analysis of which information sources most influence AI responses.
* **By Active Collections in Conversation:** Conversations can be filtered by `Conversations.active_collection_ids` to find all conversations based on a particular set of collections.

#### 4.3.5. Collection Configuration Store

* **Technology:** PostgreSQL (using JSONB for flexible configuration storage) or a dedicated configuration management store.
* **Key Tables (Conceptual, if using PostgreSQL):**
    * `Knowledge_Collections`: `collection_id` (PK, UUID), `name` (VARCHAR, UNIQUE), `description` (TEXT), `owner_user_id` (FK to Users), `created_at` (TIMESTAMPTZ), `current_version_id` (FK to `Collection_Versions`, NULLABLE).
    * `Collection_Versions`: `version_id` (PK, UUID), `collection_id` (FK to `Knowledge_Collections`), `version_number` (INT), `system_prompt` (TEXT), `llm_model_name` (VARCHAR), `llm_parameters` (JSONB), `embedding_model_name` (VARCHAR), `chunking_strategy` (VARCHAR), `chunking_parameters` (JSONB), `tool_config_ids` (ARRAY of UUIDs or JSONB referencing `Tool_Definitions`), `created_at` (TIMESTAMPTZ), `creator_user_id` (FK to Users), `version_notes` (TEXT).
    * `Tool_Definitions` (if using MCP-like tools): `tool_id` (PK, UUID), `tool_name` (VARCHAR, UNIQUE), `description` (TEXT), `api_endpoint` (VARCHAR), `authentication_details` (JSONB), `input_schema` (JSONB), `output_schema` (JSONB), `created_at` (TIMESTAMPTZ). <6>

> Storing configurations (prompts, model parameters, tool mappings) as versioned entities allows for systematic evolution and A/B testing of collection behavior. A Knowledge Collection's "behavior" in RAG is determined by its configuration: the system prompt guides the LLM, model parameters tune its output, chunking strategy affects retrieval, and tool mappings define its capabilities. As users refine a collection, they will experiment with these settings. Storing these configurations in a database, with a versioning mechanism (like the `Collection_Versions` table), enables: tracking changes over time (who changed what, when, and why - via `version_notes`), rollback (if a new configuration performs poorly, it's easy to revert to a previous, known-good version), A/B testing (different versions can be deployed or used for comparison), and auditability (provides a history of how collection behavior was configured). This is far more robust than embedding configurations in code or using simple files without version history. Using JSONB for parameters offers flexibility.

### 4.4. Key Data Flows and Process Diagrams

* **File Ingestion and Processing Flow:** Diagram showing steps from file upload -> type detection -> checksum/deduplication -> text/metadata extraction -> chunking -> embedding -> storage in vector DB and metadata DB. Error paths should be included.
* **RAG Query-Response Cycle:** Diagram illustrating user query -> query embedding -> collection selection -> vector search + metadata filtering -> context retrieval -> context merging/re-ranking -> prompt augmentation (with history) -> LLM generation -> response streaming -> source attribution display.
* **Multi-Collection Retrieval Flow:** Detail on how context from multiple selected collections is retrieved and then merged/prioritized before LLM augmentation. Decision points for different merging strategies should be shown.
* **Collection Configuration Update Flow:** How an admin/user updates a collection's prompt or model, how a new version is created, and how this new version becomes active.
* **(If relevant) External Tool Invocation Flow:** LLM indicates intent to use a tool -> orchestrator validates -> tool execution -> result returned to LLM. <1> (Sequence, state, activity diagrams) <2> (Pipeline diagrams).

## Works Cited
1.  `2_HLD 0.6 Intelligence Data Management_Leon_YW.docx`
2.  RAG Pipeline Diagram: How to Augment LLMs With Your Data - Multimodal, accessed May 26, 2025, https://www.multimodal.dev/post/rag-pipeline-diagram
3.  RAG Pipeline: Example, Tools & How to Build It - lakeFS, accessed May 26, 2025, https://lakefs.io/blog/what-is-rag-pipeline/
4.  Best practices of retrieval/context maintenance for multi-turn RAG conversational systems, accessed May 26, 2025, https://www.reddit.com/r/LocalLLaMA/comments/1hybfdx/best_practices_of_retrievalcontext_maintenance/
5.  Basic Strategies - LlamaIndex, accessed May 26, 2025, https://docs.llamaindex.ai/en/stable/optimizing/basic_strategies/basic_strategies/
6.  RAG in Production: Deployment Strategies & Practical Considerations - Coralogix, accessed May 26, 2025, https://coralogix.com/ai-blog/rag-in-production-deployment-strategies-and-practical-considerations/
7.  Prompt Versioning & Management Guide for Building AI Features - LaunchDarkly, accessed May 26, 2025, https://launchdarkly.com/blog/prompt-versioning-and-management/
8.  How to Calculate MD5 Hash of a File in Python, accessed May 26, 2025, https://www.quickprogrammingtips.com/python/how-to-calculate-md5-hash-of-a-file-in-python.html
9.  Optimizing file uploads in web applications - Transloadit, accessed May 26, 2025, https://transloadit.com/devtips/optimizing-file-uploads-in-web-applications/
10. How to Handle Large File Uploads (Without Losing Your Mind) - DEV Community, accessed May 26, 2025, https://dev.to/leapcell/how-to-handle-large-file-uploads-without-losing-your-mind-3dck
11. magicfile - PyPI, accessed May 26, 2025, https://pypi.org/project/magicfile/
12. python-magic - PyPI, accessed May 26, 2025, https://pypi.org/project/python-magic/
13. How likely is a collision using MD5 compared to SHA256 (for checking file integrity)?, accessed May 26, 2025, https://security.stackexchange.com/questions/203344/how-likely-is-a-collision-using-md5-compared-to-sha256-for-checking-file-integr
14. File Checksums - Duplicate File Detective, accessed May 26, 2025, https://www.duplicatedetective.com/content/static/help/html/filechecksums.html
15. A Guide to PDF Extraction Libraries in Python - Metric Coders, accessed May 26, 2025, https://www.metriccoders.com/post/a-guide-to-pdf-extraction-libraries-in-python
16. Extract Text From PDF Files With Python For Use In Generative AI And RAG Solutions, accessed May 26, 2025, https://build5nines.com/extract-text-from-pdf-files-with-python-for-use-in-generative-ai-and-rag-solutions/
17. genieincodebottle/parsemypdf: Collection of PDF parsing libraries like AI based docling, claude, openai, llama-vision, unstructured-io, and pdfminer, pymupdf, pdfplumber etc for efficient snapshot, text, table, and metadata extraction. - GitHub, accessed May 26, 2025, https://github.com/genieincodebottle/parsemypdf
18. Reading and Writing CSV Files in Python - Real Python, accessed May 26, 2025, https://realpython.com/python-csv/
19. csv — CSV File Reading and Writing — Python 3.13.3 documentation, accessed May 26, 2025, https://docs.python.org/3/library/csv.html
20. 4 Ways To Read a Text File With Python, accessed May 26, 2025, https://python.land/read-text-file
21. Text Processing Services — Python 3.13.3 documentation, accessed May 26, 2025, https://docs.python.org/3/library/text.html
22. pytranscript - PyPI, accessed May 26, 2025, https://pypi.org/project/pytranscript/
23. Python Speech Recognition in 2025 - AssemblyAI, accessed May 26, 2025, https://www.assemblyai.com/blog/the-state-of-python-speech-recognition
24. Metadata — PyPDF2 documentation, accessed May 26, 2025, https://pypdf2.readthedocs.io/en/3.0.0/user/metadata.html
25. Tutorial - PyMuPDF 1.26.0 documentation - Read the Docs, accessed May 26, 2025, https://pymupdf.readthedocs.io/en/latest/tutorial.html#accessing-meta-data
26. Tutorial - PyMuPDF 1.26.0 documentation, accessed May 26, 2025, https://pymupdf.readthedocs.io/en/latest/tutorial.html
27. API - PyMuPDF 1.26.0 documentation, accessed May 26, 2025, https://pymupdf.readthedocs.io/en/latest/pymupdf4llm/api.html
28. TinyTag - Python library for reading audio file metadata - GitHub, accessed May 26, 2025, https://github.com/tinytag/tinytag
29. Building production level RAG for csv files - Stack Overflow, accessed May 26, 2025, https://stackoverflow.com/questions/78945591/building-production-level-rag-for-csv-files
30. How to Chunk Documents for RAG - Multimodal, accessed May 26, 2025, https://www.multimodal.dev/post/how-to-chunk-documents-for-rag
31. The Basics - PyMuPDF 1.26.0 documentation, accessed May 26, 2025, https://pymupdf.readthedocs.io/en/latest/the-basics.html
32. How to Encrypt and Decrypt PDF Files Using Python - MakeUseOf, accessed May 26, 2025, https://www.makeuseof.com/python-encrypt-decrypt-pdf-files/
33. Retrieval-augmented generation (RAG) failure modes and how to fix them - Snorkel AI, accessed May 26, 2025, https://snorkel.ai/blog/retrieval-augmented-generation-rag-failure-modes-and-how-to-fix-them/
34. Overview | AssemblyAI | Documentation, accessed May 26, 2025, https://www.assemblyai.com/docs/api-reference/overview
35. Transcribe audio and video files with Python and Universal-1 - AssemblyAI, accessed May 26, 2025, https://www.assemblyai.com/blog/transcribe-audio-python-universal-1
36. Transcript status | AssemblyAI | Documentation, accessed May 26, 2025, https://assemblyai.com/docs/speech-to-text/pre-recorded-audio/transcript-status
37. Best Practices for Production-Scale RAG Systems — An Implementation Guide - Orkes, accessed May 26, 2025, https://orkes.io/blog/rag-best-practices/
38. Chunking Strategies for LLM Applications | Pinecone, accessed May 26, 2025, https://www.pinecone.io/learn/chunking-strategies/
39. Chunking strategies for RAG tutorial using Granite - IBM, accessed May 26, 2025, https://www.ibm.com/think/tutorials/chunking-strategies-for-rag-with-langchain-watsonx-ai
40. How to Chunk Text in JavaScript for Your RAG Application | DataStax, accessed May 26, 2025, https://www.datastax.com/blog/how-to-chunk-text-in-javascript-for-rag-applications
41. Gemini API reference | Google AI for Developers, accessed May 26, 2025, https://ai.google.dev/docs/gemini_api_overview
42. Get text embeddings | Generative AI on Vertex AI | Google Cloud, accessed May 26, 2025, https://cloud.google.com/vertex-ai/generative-ai/docs/embeddings/get-text-embeddings
43. Google models | Generative AI on Vertex AI, accessed May 26, 2025, https://cloud.google.com/vertex-ai/generative-ai/docs/models
44. Use embedding models with Vertex AI RAG Engine - Google Cloud, accessed May 26, 2025, https://cloud.google.com/vertex-ai/generative-ai/docs/rag-engine/use-embedding-models
45. RAG vs Fine-tuning vs Prompt Engineering: Everything You Need to Know | InterSystems, accessed May 26, 2025, https://www.intersystems.com/resources/rag-vs-fine-tuning-vs-prompt-engineering-everything-you-need-to-know/
46. Customizing Retrieval Augmented Generation (RAG) Systems | deepset Blog, accessed May 26, 2025, https://www.deepset.ai/blog/customizing-rag
47. How RAG and MCP Combine for Smarter Agentic Development - CData Software, accessed May 26, 2025, https://www.cdata.com/blog/how-rag-and-mcp-enable-smarter-agentic-development
48. What Is Model Context Protocol (MCP)? - CustomGPT.ai, accessed May 26, 2025, https://customgpt.ai/what-is-model-context-protocol-mcp/
49. How to Implement Version Control AI - PromptLayer, accessed May 26, 2025, https://blog.promptlayer.com/version-control-ai/
50. Prompt Versioning: Best Practices - Ghost, accessed May 26, 2025, https://latitude-blog.ghost.io/blog/prompt-versioning-best-practices/
51. Best Data Versioning Tools for MLOps| Coralogix Blog, accessed May 26, 2025, https://coralogix.com/ai-blog/best-data-versioning-tools-for-mlops/
52. AI Access Granted: RAG Apps with Identity and Access Control - Pangea.Cloud, accessed May 26, 2025, https://pangea.cloud/blog/ai-access-granted-rag-apps-with-identity-and-access-control/
53. RAG & RBAC integration: Protect data and boost AI capabilities - Elasticsearch Labs, accessed May 26, 2025, https://www.elastic.co/search-labs/blog/rag-and-rbac-integration
54. Multi-tenant vector search with Amazon Aurora PostgreSQL and Amazon Bedrock Knowledge Bases | AWS Database Blog, accessed May 26, 2025, https://aws.amazon.com/blogs/database/multi-tenant-vector-search-with-amazon-aurora-postgresql-and-amazon-bedrock-knowledge-bases/
55. Design a Secure Multitenant RAG Inferencing Solution - Azure Architecture Center, accessed May 26, 2025, https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/secure-multitenant-rag
56. LOTR (Merger Retriever) - ️ LangChain, accessed May 26, 2025, https://python.langchain.com/docs/integrations/retrievers/merger_retriever/
57. Introducing Contextual Retrieval - Anthropic, accessed May 26, 2025, https://www.anthropic.com/news/contextual-retrieval
58. Router QueryEngine and SubQuestion QueryEngine - LlamaIndex, accessed May 26, 2025, https://docs.llamaindex.ai/en/stable/examples/cookbooks/oreilly_course_cookbooks/Module-6/Router_And_SubQuestion_QueryEngine/
59. Advanced RAG: Recursive Retrieval with llamaindex - Pondhouse Data, accessed May 26, 2025, https://www.pondhouse-data.com/blog/advanced-rag-recursive-retrieval-with-llamaindex
60. What is Retrieval-Augmented Generation (RAG)? A Practical Guide - K2view, accessed May 26, 2025, https://www.k2view.com/what-is-retrieval-augmented-generation
61. How to combine results from multiple retrievers | 🦜️ LangChain, accessed May 26, 2025, https://python.langchain.com/docs/how_to/ensemble_retriever/
62. Complete Guide to Building a Robust RAG Pipeline 2025 - DhiWise, accessed May 26, 2025, https://www.dhiwise.com/post/build-rag-pipeline-guide
63. Build a basic LLM chat app - Streamlit Docs, accessed May 26, 2025, https://docs.streamlit.io/develop/tutorials/chat-and-llm-apps/build-conversational-apps
64. Historical chat as context for future prompts - RAG Agent · AI Automation Society - Skool, accessed May 26, 2025, https://www.skool.com/ai-automation-society/historical-chat-as-context-for-future-prompts-rag-agent
65. How to add chat history to RAG using langchain - Stack Overflow, accessed May 26, 2025, https://stackoverflow.com/questions/78643508/how-to-add-chat-history-to-rag-using-langchain
66. Teams Toolkit ChatBot - Streaming Response from LLM - Microsoft Q&A, accessed May 26, 2025, https://learn.microsoft.com/en-us/answers/questions/2184285/teams-toolkit-chatbot-streaming-response-from-llm
67. How to stream responses from an LLM - ️ LangChain, accessed May 26, 2025, https://python.langchain.com/docs/how_to/streaming_llm/
68. Step by Step: Building a RAG Chatbot with Minor Hallucinations - Coralogix, accessed May 26, 2025, https://coralogix.com/ai-blog/step-by-step-building-a-rag-chatbot-with-minor-hallucinations/
69. Natural-language interaction with your APIs (API to MCP) - Tyk.io, accessed May 26, 2025, https://tyk.io/docs/ai-management/mcps/api-to-mcp/
70. Exposing OpenAPI as MCP Tools - Semantics Matter - Christian Posta, accessed May 26, 2025, https://blog.christianposta.com/semantics-matter-exposing-openapi-as-mcp-tools/
71. The Right Context at the Right Time: Designing with RAG and MCP - Meibel, accessed May 26, 2025, https://www.meibel.ai/post/the-right-context-at-the-right-time-designing-with-rag-and-mcp
72. RAG++ course: Optimize LLM and GenAI applications for production - Weights & Biases, accessed May 26, 2025, https://wandb.ai/site/courses/rag/
73. NFRs: What is Non Functional Requirements (Example & Types) - BrowserStack, accessed May 26, 2025, https://www.browserstack.com/guide/non-functional-requirements-examples
74. Non Functional Requirements · A Guide to Software Architecture - raghumb, accessed May 26, 2025, https://raghumb.gitbooks.io/a-guide-to-software-architecture/content/general_principles/non_functional_req.html
75. Introduction to NFRs - Packt, accessed May 26, 2025, https://www.packtpub.com/en-us/learning/how-to-tutorials/introduction-nfrs
76. What is an acceptable latency for a RAG system in an interactive setting (e.g., a chatbot), and how do we ensure both retrieval and generation phases meet this target? - Milvus, accessed May 26, 2025, https://milvus.io/ai-quick-reference/what-is-an-acceptable-latency-for-a-rag-system-in-an-interactive-setting-eg-a-chatbot-and-how-do-we-ensure-both-retrieval-and-generation-phases-meet-this-target
77. Production-Ready RAG: Engineering Guidelines for Scalable Systems - Netguru, accessed May 26, 2025, https://www.netguru.com/blog/rag-for-scalable-systems
78. How to Implement Multitenancy and Custom Sharding in Qdrant, accessed May 26, 2025, https://qdrant.tech/articles/multitenancy/
79. Implement multitenancy using namespaces - Pinecone Docs, accessed May 26, 2025, https://docs.pinecone.io/guides/index-data/implement-multitenancy
80. Tutorial: Model-Based Evaluation of RAG applications - W&B Weave, accessed May 26, 2025, https://weave-docs.wandb.ai/tutorial-rag
81. What is LLMOps and how does it work? - Weights & Biases - Wandb, accessed May 26, 2025, https://wandb.ai/site/articles/what-is-llmops-and-how-does-it-work/
82. LLM evaluation: Metrics, frameworks, and best practices | genai-research - Wandb, accessed May 26, 2025, https://wandb.ai/onlineinference/genai-research/reports/LLM-evaluation-Metrics-frameworks-and-best-practices--VmlldzoxMTMxNjQ4NA
83. Build a Fully Local RAG App With PostgreSQL, Mistral, and Ollama - Timescale, accessed May 26, 2025, https://www.timescale.com/blog/build-a-fully-local-rag-app-with-postgresql-mistral-and-ollama
84. ai-chatbot/schema.sql at main · team-telnyx/ai-chatbot · GitHub, accessed May 26, 2025, https://github.com/team-telnyx/ai-chatbot/blob/main/schema.sql
85. How can I train a chatbot to understand PostgreSQL schema with 200+ tables and complex relationships? : r/LangChain - Reddit, accessed May 26, 2025, https://www.reddit.com/r/LangChain/comments/1k6no1b/how_can_i_train_a_chatbot_to_understand/
86. Persistent Memory for Chatbots using PostgreSQL and LangChain - HexaCluster, accessed May 26, 2025, https://hexacluster.ai/postgresql/postgres-for-chat-history-langchain-postgres-postgreschatmessagehistory/
```
# Contract Review

> AI-powered legal document analysis with risk scoring, compliance checking, and contract comparison.

## Features

- **PDF Parsing** - Extract text while preserving layout
- **Clause Analysis** - LLM-powered identification of key clauses
- **Risk Scoring** - Per-clause and overall risk assessment
- **Compliance Checking** - GDPR and standard clause verification
- **Contract Comparison** - Side-by-side diff with alignment
- **Cost Tracking** - Monitor API usage and costs
- **Demo Mode** - Try the full pipeline without any API keys

## Quick Start

1. **Install dependencies**

   ```bash
   git clone https://github.com/KarasiewiczStephane/contract-review.git
   cd contract-review
   make install    # installs Python packages and downloads the spaCy model
   ```

2. **Prepare data**

   Three sample PDFs are included in `data/sample/` (NDA, service agreement, employment contract). The dashboard lets you load them with one click, or you can upload your own PDF (up to 50 pages).

3. **Launch the dashboard**

   ```bash
   make streamlit
   ```

   Open [http://localhost:8501](http://localhost:8501) in your browser. Select **Demo (No API needed)** in the sidebar to try the app without setting up API keys.

### Using a real LLM provider (optional)

To use OpenAI or Anthropic models instead of Demo mode:

```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY and/or ANTHROPIC_API_KEY
```

Then select **OpenAI** or **Anthropic** from the sidebar dropdown in the dashboard.

## Docker

```bash
make docker
```

Or manually:

```bash
docker build -t contract-review .
docker run -p 8501:8501 contract-review
```

Open [http://localhost:8501](http://localhost:8501). To use a real LLM provider, pass your key as an environment variable:

```bash
docker run -p 8501:8501 -e ANTHROPIC_API_KEY=sk-ant-... contract-review
```

## Usage

The dashboard has six tabs:

| Tab | Description |
|-----|-------------|
| **Upload** | Upload a PDF or pick a sample contract, then click Analyze |
| **Overview** | Parties, dates, governing law, and overall risk score |
| **Clauses** | Explore individual clauses with risk level and summary |
| **Risk Report** | High-risk areas, missing standard clauses, compliance checks, and recommendations |
| **Compare** | Upload two contracts for side-by-side clause diff |
| **Export** | Download the full analysis as JSON or Markdown |

## Architecture

```
contract-review/
├── src/
│   ├── parsing/          # PDF extraction, section detection, clause segmentation
│   ├── analysis/         # LLM client abstraction, clause analysis, risk scoring, compliance
│   ├── comparison/       # Clause alignment, diff generation
│   ├── dashboard/        # Streamlit application (app.py)
│   └── utils/            # Config loader, logger, cost tracker
├── configs/
│   ├── config.yaml       # LLM provider, model, and app settings
│   └── compliance_rules.yaml  # Rules for compliance checking
├── data/
│   └── sample/           # Sample PDF contracts for testing
├── tests/
├── Dockerfile
├── Makefile
└── requirements.txt
```

## Configuration

Edit `configs/config.yaml` to change default LLM settings (the dashboard sidebar overrides the provider/model at runtime):

```yaml
llm:
  provider: openai     # or anthropic
  model: gpt-4
  temperature: 0.0
  max_tokens: 4096
max_pages: 50
```

Compliance rules are defined in `configs/compliance_rules.yaml`.

## Development

```bash
make install    # Install dependencies + spaCy model
make test       # Run tests with coverage (≥80% required)
make lint       # Check code style with ruff
make lint-fix   # Auto-fix style issues
make clean      # Remove __pycache__ and .pyc files
```


## Author

**Stéphane Karasiewicz** — [skarazdata.com](https://skarazdata.com) | [LinkedIn](https://www.linkedin.com/in/stephane-karasiewicz/)

## License

MIT

# Contract Review

> AI-powered legal document analysis with risk scoring, compliance checking, and contract comparison.

## Features

- **PDF Parsing** - Extract text while preserving layout
- **Clause Analysis** - LLM-powered identification of key clauses
- **Risk Scoring** - Per-clause and overall risk assessment
- **Compliance Checking** - GDPR and standard clause verification
- **Contract Comparison** - Side-by-side diff with alignment
- **Cost Tracking** - Monitor API usage and costs

## Quick Start

```bash
# Clone repository
git clone https://github.com/KarasiewiczStephane/contract-review.git
cd contract-review

# Install dependencies
make install

# Set up environment
cp .env.example .env
# Edit .env with your API keys

# Run application
make streamlit
```

## Docker

```bash
docker build -t contract-review .
docker run -p 8501:8501 -e OPENAI_API_KEY=sk-... contract-review
```

Open http://localhost:8501 in your browser.

## Usage

### 1. Upload Contract
Upload a PDF contract (up to 50 pages) and click "Analyze".

### 2. Review Analysis
- **Overview Tab**: See parties, dates, and risk score
- **Clauses Tab**: Explore individual clauses with risk levels
- **Risk Report Tab**: View high-risk areas and recommendations

### 3. Compare Contracts
Upload two contracts to see side-by-side differences.

### 4. Export Results
Download analysis as JSON or Markdown.

## Architecture

```
src/
├── parsing/          # PDF extraction, section detection, clause segmentation
├── analysis/         # LLM clause analysis, risk scoring, compliance
├── comparison/       # Clause alignment, diff generation
├── dashboard/        # Streamlit application
└── utils/            # Config, logging, cost tracking
```

## Configuration

Edit `configs/config.yaml`:
```yaml
llm:
  provider: openai  # or anthropic
  model: gpt-4
  temperature: 0.0
max_pages: 50
```

Customize compliance rules in `configs/compliance_rules.yaml`.

## Sample Output

```json
{
  "risk_report": {
    "overall_score": 65,
    "risk_level": "medium",
    "high_risk_clauses": [
      {
        "type": "liability",
        "reasoning": "Unlimited liability clause detected"
      }
    ],
    "recommendations": [
      "Review liability clause: Consider adding a cap"
    ]
  }
}
```

## Development

```bash
make install    # Install dependencies
make test       # Run tests with coverage
make lint       # Check code style
make lint-fix   # Auto-fix style issues
```

## License

MIT
